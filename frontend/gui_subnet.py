#!/usr/bin/env python3
"""
Aplikasi Kalkulator Subnetting IPv4 - Desktop GUI (Tkinter)
100% Pure Python menggunakan modul built-in ipaddress & tkinter.
Jalankan dengan: python3 gui_subnet.py
"""

import ipaddress
import tkinter as tk
from tkinter import ttk, messagebox

def hitung_subnet_data(alamat_awal: str, prefix_baru: int):
    try:
        jaringan = ipaddress.ip_network(alamat_awal, strict=False)
    except ValueError as e:
        return None, f"Format alamat IP/Network tidak valid: {e}"

    if prefix_baru < jaringan.prefixlen:
        return None, f"Prefix baru (/{prefix_baru}) harus >= prefix awal (/{jaringan.prefixlen})!"

    bit_dipinjam = prefix_baru - jaringan.prefixlen
    jumlah_subnet = 2 ** bit_dipinjam
    bit_host = 32 - prefix_baru
    total_ip = 2 ** bit_host
    host_usable = total_ip - 2 if total_ip >= 4 else (2 if total_ip == 2 else 1)

    subnets_list = list(jaringan.subnets(new_prefix=prefix_baru))
    sample_sub = ipaddress.ip_network(f"0.0.0.0/{prefix_baru}", strict=False)

    rows = []
    for idx, sub in enumerate(subnets_list[:128], 1):
        num_addr = sub.num_addresses
        net_addr = sub.network_address
        bcast_addr = sub.broadcast_address

        if num_addr >= 4:
            hp = str(net_addr + 1)
            ht = str(bcast_addr - 1)
            uh = num_addr - 2
        elif num_addr == 2:
            hp = str(net_addr)
            ht = str(bcast_addr)
            uh = 2
        else:
            hp = str(net_addr)
            ht = str(net_addr)
            uh = 1

        rows.append((idx, str(sub), str(net_addr), hp, ht, str(bcast_addr), uh))

    meta = {
        "alamat_awal": str(jaringan),
        "prefix_awal": jaringan.prefixlen,
        "prefix_baru": prefix_baru,
        "mask_awal": str(jaringan.netmask),
        "mask_baru": str(sample_sub.netmask),
        "bit_dipinjam": bit_dipinjam,
        "jumlah_subnet": jumlah_subnet,
        "bit_host": bit_host,
        "total_ip": total_ip,
        "host_usable": host_usable,
        "subnets_count": len(subnets_list)
    }

    return meta, rows


class SubnetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator Subnetting IPv4 (Pure Python Tkinter)")
        self.geometry("960x680")
        self.minsize(800, 550)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.create_widgets()
        self.calculate()

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self, padding="15 15 15 10")
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="Kalkulator Subnetting IPv4", font=("Helvetica", 18, "bold"))
        title_lbl.pack(anchor=tk.W)
        sub_lbl = ttk.Label(header_frame, text="Sesuai Flowchart Praktikum Jaringan Komputer (Modul ipaddress)", font=("Helvetica", 10))
        sub_lbl.pack(anchor=tk.W)

        # Input Frame
        input_frame = ttk.LabelFrame(self, text=" Parameter Subnetting ", padding="15")
        input_frame.pack(fill=tk.X, padx=15, pady=5)

        ttk.Label(input_frame, text="Alamat Jaringan Awal:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ip_var = tk.StringVar(value="192.168.1.0/24")
        self.ip_entry = ttk.Entry(input_frame, textvariable=self.ip_var, width=22, font=("Menlo", 11))
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Prefix Baru (/):").grid(row=0, column=2, sticky=tk.W, padx=(20, 5), pady=5)
        self.prefix_var = tk.IntVar(value=26)
        self.prefix_spin = ttk.Spinbox(input_frame, from_=1, to=32, textvariable=self.prefix_var, width=6, font=("Menlo", 11))
        self.prefix_spin.grid(row=0, column=3, padx=5, pady=5)

        btn_calc = ttk.Button(input_frame, text="Hitung Subnet", command=self.calculate)
        btn_calc.grid(row=0, column=4, padx=(20, 5), pady=5)

        btn_reset = ttk.Button(input_frame, text="Reset Soal Tugas", command=self.reset_preset)
        btn_reset.grid(row=0, column=5, padx=5, pady=5)

        # Result Summary Frame
        self.summary_frame = ttk.LabelFrame(self, text=" Ringkasan Hasil Perhitungan ", padding="12")
        self.summary_frame.pack(fill=tk.X, padx=15, pady=10)

        self.lbl_subnets = ttk.Label(self.summary_frame, text="Jumlah Subnet: -", font=("Helvetica", 11, "bold"))
        self.lbl_subnets.grid(row=0, column=0, sticky=tk.W, padx=10, pady=3)

        self.lbl_hosts = ttk.Label(self.summary_frame, text="Host Usable: -", font=("Helvetica", 11, "bold"))
        self.lbl_hosts.grid(row=0, column=1, sticky=tk.W, padx=20, pady=3)

        self.lbl_netmask = ttk.Label(self.summary_frame, text="Netmask Baru: -", font=("Helvetica", 11, "bold"))
        self.lbl_netmask.grid(row=0, column=2, sticky=tk.W, padx=20, pady=3)

        self.lbl_detail1 = ttk.Label(self.summary_frame, text="", font=("Menlo", 10))
        self.lbl_detail1.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=10, pady=(6, 2))

        self.lbl_detail2 = ttk.Label(self.summary_frame, text="", font=("Menlo", 10))
        self.lbl_detail2.grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=10, pady=2)

        # Table Frame
        tbl_frame = ttk.LabelFrame(self, text=" Tabel Alokasi IP Subnet ", padding="10")
        tbl_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columns = ("No", "Subnet", "Network ID", "Host Pertama", "Host Terakhir", "Broadcast", "Usable")
        self.tree = ttk.Treeview(tbl_frame, columns=columns, show="headings")

        self.tree.heading("No", text="No")
        self.tree.heading("Subnet", text="Subnet (CIDR)")
        self.tree.heading("Network ID", text="Network ID")
        self.tree.heading("Host Pertama", text="Host Pertama")
        self.tree.heading("Host Terakhir", text="Host Terakhir")
        self.tree.heading("Broadcast", text="Broadcast")
        self.tree.heading("Usable", text="Host Usable")

        self.tree.column("No", width=50, anchor=tk.CENTER)
        self.tree.column("Subnet", width=140, anchor=tk.W)
        self.tree.column("Network ID", width=120, anchor=tk.W)
        self.tree.column("Host Pertama", width=120, anchor=tk.W)
        self.tree.column("Host Terakhir", width=120, anchor=tk.W)
        self.tree.column("Broadcast", width=120, anchor=tk.W)
        self.tree.column("Usable", width=90, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tbl_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def reset_preset(self):
        self.ip_var.set("192.168.1.0/24")
        self.prefix_var.set(26)
        self.calculate()

    def calculate(self):
        ip_in = self.ip_var.get()
        p_in = self.prefix_var.get()

        meta, rows = hitung_subnet_data(ip_in, p_in)
        if meta is None:
            messagebox.showerror("Error Perhitungan", rows)
            return

        self.lbl_subnets.config(text=f"Jumlah Subnet: {meta['jumlah_subnet']} Subnet")
        self.lbl_hosts.config(text=f"Host Usable / Subnet: {meta['host_usable']} Host")
        self.lbl_netmask.config(text=f"Netmask Baru: {meta['mask_baru']} (/{meta['prefix_baru']})")

        self.lbl_detail1.config(
            text=f"• Bit Dipinjam (n) = {meta['bit_dipinjam']} bit (/{meta['prefix_baru']} - /{meta['prefix_awal']}) -> Rumus: 2^{meta['bit_dipinjam']} = {meta['jumlah_subnet']} Subnet"
        )
        self.lbl_detail2.config(
            text=f"• Bit Host (h) = {meta['bit_host']} bit (32 - {meta['prefix_baru']}) -> Total IP = 2^{meta['bit_host']} = {meta['total_ip']} | Usable = {meta['total_ip']} - 2 = {meta['host_usable']} Host"
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert("", tk.END, values=row)


if __name__ == "__main__":
    app = SubnetApp()
    app.mainloop()
