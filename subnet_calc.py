#!/usr/bin/env python3
"""
Program Kalkulator Subnetting IPv4
Sesuai Flowchart Praktikum dengan Modul ipaddress
Dibuat untuk tugas praktikum jaringan komputer.
"""

import ipaddress
import sys

def hitung_subnet(alamat_awal: str, prefix_baru: int):
    """
    Menghitung pembagian subnet sesuai alur flowchart praktikum.
    """
    try:
        jaringan = ipaddress.ip_network(alamat_awal, strict=False)
    except ValueError as e:
        print(f"Error: Format alamat jaringan tidak valid! ({e})")
        return None

    if prefix_baru < jaringan.prefixlen:
        print(f"Error: Prefix baru (/{prefix_baru}) harus lebih besar atau sama dengan prefix awal (/{jaringan.prefixlen})!")
        return None
    
    if prefix_baru > 32:
        print("Error: Prefix IPv4 maksimal adalah /32!")
        return None

    # Proses: Pembagian subnet
    subnet_list = list(jaringan.subnets(new_prefix=prefix_baru))

    # Proses Perhitungan Jumlah Subnet
    bit_dipinjam = prefix_baru - jaringan.prefixlen
    jumlah_subnet = 2 ** bit_dipinjam

    # Proses Perhitungan Host per Subnet
    bit_host = 32 - prefix_baru
    total_ip = 2 ** bit_host
    # Pada IPv4 standar, usable host = total_ip - 2 (kecuali /31 dan /32)
    host_per_subnet = total_ip - 2 if total_ip >= 2 else 0

    hasil = {
        "alamat_awal": str(jaringan),
        "network_awal": str(jaringan.network_address),
        "subnet_mask_awal": str(jaringan.netmask),
        "prefix_awal": jaringan.prefixlen,
        "prefix_baru": prefix_baru,
        "subnet_mask_baru": str(subnet_list[0].netmask) if subnet_list else "",
        "bit_dipinjam": bit_dipinjam,
        "jumlah_subnet": jumlah_subnet,
        "bit_host": bit_host,
        "total_ip": total_ip,
        "host_per_subnet": host_per_subnet,
        "subnets": []
    }

    # Loop 1 & Loop 2: Menampilkan Subnet Valid & Tabel Alokasi IP
    for idx, sub in enumerate(subnet_list, 1):
        num_addr = sub.num_addresses
        net_addr = sub.network_address
        bcast_addr = sub.broadcast_address

        if num_addr >= 4:
            host_pertama = str(net_addr + 1)
            host_terakhir = str(bcast_addr - 1)
            usable_hosts = num_addr - 2
        elif num_addr == 2: # /31 RFC 3021
            host_pertama = str(net_addr)
            host_terakhir = str(bcast_addr)
            usable_hosts = 2
        else: # /32 Host route
            host_pertama = str(net_addr)
            host_terakhir = str(net_addr)
            usable_hosts = 1

        hasil["subnets"].append({
            "no": idx,
            "subnet": str(sub),
            "network_id": str(net_addr),
            "host_pertama": host_pertama,
            "host_terakhir": host_terakhir,
            "range_host": f"{host_pertama} - {host_terakhir}" if usable_hosts > 1 else host_pertama,
            "broadcast": str(bcast_addr),
            "jumlah_host": usable_hosts,
            "netmask": str(sub.netmask)
        })

    return hasil


def tampilkan_output_cli(hasil):
    """Mencetak hasil dengan format rapi untuk tangkapan layar praktikum"""
    print("=" * 70)
    print("               PROGRAM KALKULATOR SUBNETTING IPV4")
    print("           Berdasarkan Flowchart Praktikum Modul ipaddress")
    print("=" * 70)
    
    print("\n[+] OUTPUT 1: INFORMASI AWAL")
    print(f"  * Jaringan Awal        : {hasil['alamat_awal']}")
    print(f"  * Subnet Mask Awal     : {hasil['subnet_mask_awal']} (/{hasil['prefix_awal']})")
    print(f"  * Prefix Baru          : /{hasil['prefix_baru']}")
    print(f"  * Subnet Mask Baru     : {hasil['subnet_mask_baru']}")
    print(f"  * Bit yang Dipinjam (n): {hasil['bit_dipinjam']} bit (/{hasil['prefix_baru']} - /{hasil['prefix_awal']})")
    print(f"  * Rumus Jumlah Subnet  : 2^{hasil['bit_dipinjam']}")
    print(f"  * Jumlah Subnet        : {hasil['jumlah_subnet']} Subnet")

    print("\n[+] OUTPUT 2: INFORMASI HOST PER SUBNET")
    print(f"  * Bit Host (h)         : {hasil['bit_host']} bit (32 - {hasil['prefix_baru']})")
    print(f"  * Rumus Total IP       : 2^{hasil['bit_host']}")
    print(f"  * Total IP / Subnet    : {hasil['total_ip']} IP")
    print(f"  * Rumus Host Usable    : {hasil['total_ip']} - 2")
    print(f"  * Host Usable / Subnet : {hasil['host_per_subnet']} Host")

    print("\n[+] LOOP 1: MENAMPILKAN SUBNET VALID")
    for s in hasil["subnets"]:
        print(f"  - Subnet {s['no']}: {s['subnet']}")

    print("\n[+] LOOP 2: TABEL ALOKASI IP SETIAP SUBNET")
    header = f"| {'No':<3} | {'Subnet':<18} | {'Network ID':<15} | {'Host Pertama':<15} | {'Host Terakhir':<15} | {'Broadcast':<15} | {'Usable':<6} |"
    divider = "-" * len(header)
    print(divider)
    print(header)
    print(divider)
    for s in hasil["subnets"]:
        print(f"| {s['no']:<3} | {s['subnet']:<18} | {s['network_id']:<15} | {s['host_pertama']:<15} | {s['host_terakhir']:<15} | {s['broadcast']:<15} | {s['jumlah_host']:<6} |")
    print(divider)

    print("\n[+] HASIL AKHIR (KONSEPTUAL):")
    print(f"  * Jumlah subnet          = {hasil['jumlah_subnet']}")
    print(f"  * Host usable per subnet = {hasil['host_per_subnet']}")
    print("  * Subnet valid           =")
    for s in hasil["subnets"]:
        print(f"    - {s['subnet']}")
    print("=" * 70)


if __name__ == "__main__":
    # Sesuai contoh pada tugas flowchart:
    # alamat_awal = "192.168.1.0/24"
    # prefix_baru = 26
    if len(sys.argv) >= 3:
        ip_in = sys.argv[1]
        prefix_in = int(sys.argv[2].replace("/", ""))
    else:
        ip_in = "192.168.1.0/24"
        prefix_in = 26

    print(f"Menjalankan kalkulasi untuk {ip_in} dengan prefix baru /{prefix_in}...\n")
    data = hitung_subnet(ip_in, prefix_in)
    if data:
        tampilkan_output_cli(data)
