"""
Backend FastAPI Subnet Calculator API
Mengimplementasikan logika algoritma subnetting IPv4 dengan modul ipaddress.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import ipaddress
from typing import Optional, List, Dict, Any

app = FastAPI(
    title="Kalkulator Subnetting IPv4 API",
    description="API untuk menghitung pembagian subnet sesuai alur flowchart praktikum ipaddress",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SubnetRequest(BaseModel):
    alamat_awal: str = Field(..., examples=["192.168.1.0/24"], description="IP Network awal dengan prefix (CIDR)")
    prefix_baru: int = Field(..., examples=[26], description="Prefix subnet baru (antara prefix awal s/d 32)")
    limit: Optional[int] = Field(256, description="Batas maksimal subnet yang ditampilkan pada tabel alokasi")


def get_ip_class(ip_obj: ipaddress.IPv4Address) -> str:
    first_octet = int(str(ip_obj).split('.')[0])
    if 1 <= first_octet <= 126:
        return "Kelas A"
    elif 128 <= first_octet <= 191:
        return "Kelas B"
    elif 192 <= first_octet <= 223:
        return "Kelas C"
    elif 224 <= first_octet <= 239:
        return "Kelas D (Multicast)"
    else:
        return "Kelas E (Eksperimental)"


def to_binary_octets(ip_str: str) -> str:
    try:
        octets = [int(x) for x in ip_str.split('.')]
        return ".".join(f"{x:08b}" for x in octets)
    except Exception:
        return ""


def hitung_subnet_core(alamat_awal: str, prefix_baru: int, limit: int = 256) -> Dict[str, Any]:
    # Normalisasi format
    alamat_awal = alamat_awal.strip()
    if "/" not in alamat_awal:
        # Default assume /24 if not provided
        alamat_awal += "/24"

    try:
        jaringan = ipaddress.ip_network(alamat_awal, strict=False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Alamat IP/Network '{alamat_awal}' tidak valid: {str(e)}")

    if prefix_baru < jaringan.prefixlen:
        raise HTTPException(
            status_code=400,
            detail=f"Prefix baru (/{prefix_baru}) harus lebih besar atau sama dengan prefix awal (/{jaringan.prefixlen})! Anda tidak bisa membagi ke prefix yang lebih kecil (supernetting)."
        )

    if prefix_baru > 32 or prefix_baru < 0:
        raise HTTPException(status_code=400, detail="Prefix IPv4 harus berada dalam rentang 0 sampai 32!")

    # Perhitungan Bit & Subnet
    bit_dipinjam = prefix_baru - jaringan.prefixlen
    jumlah_subnet = 2 ** bit_dipinjam

    # Perhitungan Host per Subnet
    bit_host = 32 - prefix_baru
    total_ip = 2 ** bit_host
    if total_ip >= 4:
        host_usable = total_ip - 2
    elif total_ip == 2: # /31 RFC 3021
        host_usable = 2
    else: # /32
        host_usable = 1

    # Dapatkan subnet mask baru
    sample_sub = ipaddress.ip_network(f"0.0.0.0/{prefix_baru}", strict=False)
    subnet_mask_baru = str(sample_sub.netmask)
    wildcard_mask = str(sample_sub.hostmask)

    # Subnet list generation
    subnets_output = []
    total_subnets_count = jumlah_subnet
    
    # Gunakan generator subnets agar hemat memori jika subnet sangat banyak
    subnets_iter = jaringan.subnets(new_prefix=prefix_baru)
    
    truncated = False
    for idx, sub in enumerate(subnets_iter, start=1):
        if idx > limit:
            truncated = True
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

    ip_class = get_ip_class(jaringan.network_address)
    is_private = jaringan.is_private

    # Penjelasan istilah untuk laporan / jurnal praktikum
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
        "is_private": is_private,
        "binary_network": to_binary_octets(str(jaringan.network_address)),
        "binary_netmask_awal": to_binary_octets(str(jaringan.netmask)),
        "binary_netmask_baru": to_binary_octets(subnet_mask_baru),
        "bit_dipinjam": bit_dipinjam,
        "jumlah_subnet": jumlah_subnet,
        "bit_host": bit_host,
        "total_ip": total_ip,
        "host_per_subnet": host_usable,
        "subnets": subnets_output,
        "total_subnets_count": total_subnets_count,
        "displayed_subnets_count": len(subnets_output),
        "truncated": truncated,
        "penjelasan_istilah": penjelasan_istilah,
        "flowchart_steps": [
            {"step": "Input", "detail": f"Alamat awal = {str(jaringan)}, Prefix baru = {prefix_baru}"},
            {"step": "Inisialisasi Jaringan", "detail": f"ip_network('{str(jaringan)}', strict=False)"},
            {"step": "Bit Dipinjam", "detail": f"prefix_baru ({prefix_baru}) - prefix_awal ({jaringan.prefixlen}) = {bit_dipinjam} bit"},
            {"step": "Jumlah Subnet", "detail": f"2^{bit_dipinjam} = {jumlah_subnet} subnet"},
            {"step": "Bit Host", "detail": f"32 - {prefix_baru} = {bit_host} bit"},
            {"step": "Total IP & Host Usable", "detail": f"Total = 2^{bit_host} = {total_ip} IP, Usable = {total_ip} - 2 = {host_usable} host"},
            {"step": "Loop 1 (Subnet Valid)", "detail": f"{min(len(subnets_output), 4)} dari {total_subnets_count} subnet pertama di-generate"},
            {"step": "Loop 2 (Tabel Alokasi)", "detail": "Menghitung Host Pertama (+1), Host Terakhir (-1), dan Broadcast Address"}
        ]
    }


@app.get("/api/health")
def api_health():
    return {
        "status": "online",
        "app": "IPv4 Subnet Calculator API",
        "docs": "/docs",
        "author": "Python + React Subnet Calculator"
    }


@app.get("/")
def read_root():
    dist_index = os.path.join(frontend_dist, "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index)
    return api_health()



@app.get("/api/calculate")
def calculate_get(
    alamat_awal: str = Query(..., description="IP Network awal, cth: 192.168.1.0/24"),
    prefix_baru: int = Query(..., ge=0, le=32, description="Prefix subnet baru, cth: 26"),
    limit: int = Query(256, ge=1, le=1024, description="Limit subnet rows")
):
    return hitung_subnet_core(alamat_awal, prefix_baru, limit)


@app.post("/api/calculate")
def calculate_post(req: SubnetRequest):
    return hitung_subnet_core(req.alamat_awal, req.prefix_baru, req.limit or 256)


# Static files mount for React frontend distribution
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        target = os.path.join(frontend_dist, full_path)
        if full_path and os.path.exists(target) and os.path.isfile(target):
            return FileResponse(target)
        return FileResponse(os.path.join(frontend_dist, "index.html"))


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("🚀 Server Subnet Calculator API & React Berjalan!")
    print("📍 URL: http://127.0.0.1:8000")
    print("📖 Dokumentasi API Swagger: http://127.0.0.1:8000/docs")
    print("Tekan CTRL+C untuk menghentikan server.")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)


