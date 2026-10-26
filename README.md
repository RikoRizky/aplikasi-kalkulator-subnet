# 🌐 Kalkulator Subnetting IPv4 (100% Full Python)

Aplikasi kalkulator subnetting IPv4 interaktif dan lengkap yang **100% berbasis Python murni** (tanpa React/Node.js). Menggunakan modul standar `ipaddress` sesuai diagram alur (*flowchart*) praktikum jaringan komputer.

Tersedia **3 mode tampilan** yang dapat Anda pilih sesuai kebutuhan:

---

## 🎯 3 Pilihan Mode Tampilan

| Mode | Perintah Terminal | Deskripsi |
|---|---|---|
| **1. Tampilan Web Python** | `python3 app.py` | Antarmuka Web modern (Flask + HTML/CSS responsif) di browser `http://127.0.0.1:5050` (otomatis terbuka). |
| **2. Tampilan Desktop GUI** | `python3 gui_subnet.py` | Aplikasi jendela desktop native macOS berbasis modul built-in `tkinter`. |
| **3. Tampilan Konsol CLI** | `python3 subnet_calc.py` | Output teks rapi di terminal untuk keperluan tangkapan layar (*screenshot*) jurnal praktikum Edlink. |

---

## 📂 Struktur File

```
/Users/rikorizky/new coding/
├── app.py             # 🌐 Aplikasi Web Full Python (Flask + ipaddress)
├── gui_subnet.py      # 🖥️ Aplikasi Desktop GUI Full Python (Tkinter)
├── subnet_calc.py     # 💻 Script CLI Python untuk screenshot tugas
└── README.md          # Dokumentasi & penjelasan istilah praktikum
```

---

## 🚀 Cara Menjalankan

### 1. Menjalankan Tampilan Web (Flask)
Cukup jalankan satu perintah:
```bash
python3 app.py
```
Peramban (*browser*) Anda akan otomatis terbuka ke alamat **http://127.0.0.1:5050**.
Tersedia fitur pemilihan preset, slider prefix, alur flowchart, tabel alokasi IP, format biner, dan output terminal.

### 2. Menjalankan Tampilan Desktop Window (Tkinter)
```bash
python3 gui_subnet.py
```
Jendela aplikasi desktop native akan langsung terbuka di layar Mac Anda lengkap dengan tabel alokasi IP dan tombol kalkulasi.

### 3. Menjalankan Script Terminal (Untuk Screenshot Tugas Edlink)
```bash
python3 subnet_calc.py 192.168.1.0/24 26
```
*(Atau cukup `python3 subnet_calc.py`)*

---

## 📝 Penjelasan Istilah untuk Slide & Jurnal Praktikum (Edlink)

| Istilah | Penjelasan Fungsi / Arti | Contoh Kasus (192.168.1.0/24 ke /26) |
|---|---|---|
| **Network ID (Alamat Jaringan)** | Alamat IP pertama dalam setiap subnet yang berfungsi sebagai identitas pengenal subnet tersebut. Tidak boleh dipasang ke host. | Subnet 1: `192.168.1.0`<br>Subnet 2: `192.168.1.64` |
| **Broadcast Address** | Alamat IP terakhir dalam subnet yang dipakai untuk membroadcast paket ke semua perangkat dalam subnet. Tidak dapat digunakan untuk host. | Subnet 1: `192.168.1.63`<br>Subnet 2: `192.168.1.127` |
| **Host Usable (Host Valid)** | Rentang IP di antara Network ID dan Broadcast yang valid untuk dialokasikan ke perangkat komputer/laptop/router. | Subnet 1: `192.168.1.1` s/d `192.168.1.62` (Total 62 Host) |
| **Subnet Mask & Prefix (CIDR)** | Penanda batas antara porsi Network (bit 1) dan porsi Host (bit 0) dalam 32-bit IPv4. | `/26` = `255.255.255.192` (26 bit bernilai '1') |
| **Bit Dipinjam ($n$)** | Jumlah bit dari bagian host yang dipinjam untuk subnet: $n = \text{prefix\_baru} - \text{prefix\_lama}$. Rumus subnet: $2^n$. | $26 - 24 = 2$ bit dipinjam.<br>Jumlah subnet = $2^2 = 4$ Subnet. |
| **Bit Host ($h$)** | Sisa bit host setelah peminjaman bit: $h = 32 - \text{prefix\_baru}$. Rumus total IP: $2^h$, usable: $2^h - 2$. | $32 - 26 = 6$ bit host.<br>Total IP = $2^6 = 64$. Usable = $64 - 2 = 62$ Host. |
