#!/usr/bin/env python3
"""
Kalkulator Subnetting IPv4 - Full Python Server
Menyajikan antarmuka lengkap persis seperti React langsung dari Python!
Backend logika: modul ipaddress bawaan Python
Dijalankan cukup dengan: python3 app.py
"""

import os
import ipaddress
import webbrowser
import threading
from flask import Flask, send_from_directory, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Cek lokasi folder dist React
DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")
if not os.path.exists(DIST_DIR):
    DIST_DIR = os.path.join(BASE_DIR, "dist")

app = Flask(__name__, static_folder=None)


def hitung_subnet(alamat_awal: str, prefix_baru: int, limit: int = 512):
    """
    Logika perhitungan subnetting sesuai alur flowchart modul ipaddress.
    """
    alamat_awal = alamat_awal.strip()
    if "/" not in alamat_awal:
        alamat_awal += "/24"

    try:
        jaringan = ipaddress.ip_network(alamat_awal, strict=False)
    except ValueError as e:
        return {"error": f"Format alamat IP/Network '{alamat_awal}' tidak valid: {e}"}

    if prefix_baru < jaringan.prefixlen:
        return {"error": f"Prefix baru (/{prefix_baru}) harus lebih besar atau sama dengan prefix awal (/{jaringan.prefixlen})!"}

    if prefix_baru > 32 or prefix_baru < 0:
        return {"error": "Prefix IPv4 harus berada dalam rentang 0 sampai 32!"}

    # Perhitungan Bit & Subnet
    bit_dipinjam = prefix_baru - jaringan.prefixlen
    jumlah_subnet = 2 ** bit_dipinjam

    # Perhitungan Host per Subnet
    bit_host = 32 - prefix_baru
    total_ip = 2 ** bit_host
    host_usable = total_ip - 2 if total_ip >= 4 else (2 if total_ip == 2 else 1)

    sample_sub = ipaddress.ip_network(f"0.0.0.0/{prefix_baru}", strict=False)
    subnet_mask_baru = str(sample_sub.netmask)
    wildcard_mask = str(sample_sub.hostmask)

    subnets_output = []
    subnets_iter = jaringan.subnets(new_prefix=prefix_baru)
    
    for idx, sub in enumerate(subnets_iter, start=1):
        if idx > limit:
            break
        num_addr = sub.num_addresses
        net_addr = sub.network_address
        bcast_addr = sub.broadcast_address

        if num_addr >= 4:
            host_pertama = str(net_addr + 1)
            host_terakhir = str(bcast_addr - 1)
            usable_count = num_addr - 2
        elif num_addr == 2:
            host_pertama = str(net_addr)
            host_terakhir = str(bcast_addr)
            usable_count = 2
        else:
            host_pertama = str(net_addr)
            host_terakhir = str(net_addr)
            usable_count = 1

        subnets_output.append({
            "no": idx,
            "subnet": str(sub),
            "network_id": str(net_addr),
            "host_pertama": host_pertama,
            "host_terakhir": host_terakhir,
            "range_host": f"{host_pertama} - {host_terakhir}" if usable_count > 1 else host_pertama,
            "broadcast": str(bcast_addr),
            "jumlah_host": usable_count,
            "netmask": str(sub.netmask)
        })

    # Kelas IP
    first_octet = int(str(jaringan.network_address).split('.')[0])
    if 1 <= first_octet <= 126:
        ip_class = "Kelas A"
    elif 128 <= first_octet <= 191:
        ip_class = "Kelas B"
    elif 192 <= first_octet <= 223:
        ip_class = "Kelas C"
    elif 224 <= first_octet <= 239:
        ip_class = "Kelas D (Multicast)"
    else:
        ip_class = "Kelas E (Eksperimental)"

    def to_bin(ip_str):
        try:
            return ".".join(f"{int(x):08b}" for x in ip_str.split('.'))
        except Exception:
            return ""

    penjelasan_istilah = [
        {
            "istilah": "Network ID (Alamat Jaringan)",
            "arti": "Alamat IP pertama dalam subnet yang berfungsi sebagai identitas kelompok jaringan. IP ini tidak boleh digunakan untuk perangkat host komputer.",
            "contoh": f"Subnet 1: {subnets_output[0]['network_id']}" if subnets_output else "-"
        },
        {
            "istilah": "Broadcast Address",
            "arti": "Alamat IP terakhir dalam subnet yang dipakai untuk mengirim pesan secara serentak (broadcast) ke seluruh host dalam subnet tersebut. Tidak boleh dipakai sebagai IP host.",
            "contoh": f"Subnet 1: {subnets_output[0]['broadcast']}" if subnets_output else "-"
        },
        {
            "istilah": "Usable Host Range (Rentang IP Host Valid)",
            "arti": "Daftar alamat IP di antara Network ID dan Broadcast Address yang sah dan dapat dialokasikan ke perangkat (PC, laptop, smartphone, router interface).",
            "contoh": f"Subnet 1: {subnets_output[0]['range_host']}" if subnets_output else "-"
        },
        {
            "istilah": "Subnet Mask & Prefix (CIDR)",
            "arti": "Penanda pembagi antara porsi Network dan porsi Host dalam alamat 32-bit IPv4. Angka prefix (contoh: /26) menunjukkan banyaknya bit 1 pada netmask.",
            "contoh": f"/{prefix_baru} = {subnet_mask_baru}"
        },
        {
            "istilah": "Bit Dipinjam (n) & Jumlah Subnet",
            "arti": "Banyaknya bit host yang dialihkan (dipinjam) menjadi bit subnet (n = Prefix Baru - Prefix Awal). Rumus jumlah subnet adalah 2ⁿ.",
            "contoh": f"2^{bit_dipinjam} = {jumlah_subnet} subnet"
        },
        {
            "istilah": "Bit Host (h) & Usable Host",
            "arti": "Sisa bit yang dialokasikan untuk penomoran host (h = 32 - Prefix Baru). Rumus total IP adalah 2ʰ, dan IP yang bisa digunakan adalah 2ʰ - 2.",
            "contoh": f"2^{bit_host} - 2 = {host_usable} host per subnet"
        }
    ]

    return {
        "alamat_awal": str(jaringan),
        "network_awal": str(jaringan.network_address),
        "subnet_mask_awal": str(jaringan.netmask),
        "prefix_awal": jaringan.prefixlen,
        "prefix_baru": prefix_baru,
        "subnet_mask_baru": subnet_mask_baru,
        "wildcard_mask": wildcard_mask,
        "ip_class": ip_class,
        "binary_network": to_bin(str(jaringan.network_address)),
        "binary_netmask_awal": to_bin(str(jaringan.netmask)),
        "binary_netmask_baru": to_bin(subnet_mask_baru),
        "bit_dipinjam": bit_dipinjam,
        "jumlah_subnet": jumlah_subnet,
        "bit_host": bit_host,
        "total_ip": total_ip,
        "host_per_subnet": host_usable,
        "subnets": subnets_output,
        "total_subnets_count": jumlah_subnet,
        "penjelasan_istilah": penjelasan_istilah
    }


# Route API Kalkulasi Subnet
@app.route("/api/calculate", methods=["GET", "POST"])
def api_calculate():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        alamat_awal = data.get("alamat_awal", "192.168.1.0/24")
        prefix_baru = int(data.get("prefix_baru", 26))
        limit = int(data.get("limit", 512))
    else:
        alamat_awal = request.args.get("alamat_awal", "192.168.1.0/24")
        prefix_baru = int(request.args.get("prefix_baru", 26))
        limit = int(request.args.get("limit", 512))
    return jsonify(hitung_subnet(alamat_awal, prefix_baru, limit))


# Route Aset Statis (CSS, JS, Font, Gambar)
@app.route("/assets/<path:filename>")
def serve_assets(filename):
    assets_dir = os.path.join(DIST_DIR, "assets")
    return send_from_directory(assets_dir, filename)


# Route Utama (Menampilkan Halaman UI Persis Seperti React)
@app.route("/")
@app.route("/<path:path>")
def serve_index(path=""):
    if path and os.path.exists(os.path.join(DIST_DIR, path)):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, "index.html")


def auto_open_browser():
    webbrowser.open_new("http://127.0.0.1:5050")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("   🌐 KALKULATOR SUBNETTING IPV4 - FULL PYTHON SERVER")
    print("      Tampilan 100% Persis Seperti React, Dijalankan dari Python!")
    print("=" * 70)
    print("   📍 URL Aplikasi : http://127.0.0.1:5050")
    print("   🚀 Browser akan otomatis terbuka dalam 1 detik...")
    print("   🛑 Tekan CTRL+C untuk menghentikan server")
    print("=" * 70 + "\n")

    threading.Timer(1.0, auto_open_browser).start()
    app.run(host="127.0.0.1", port=5050, debug=False)
