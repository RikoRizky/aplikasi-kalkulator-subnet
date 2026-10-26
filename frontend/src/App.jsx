import React, { useState, useEffect, useMemo } from 'react';
import {
  Network,
  Cpu,
  Layers,
  Table as TableIcon,
  Terminal,
  BookOpen,
  Copy,
  Check,
  Download,
  RotateCcw,
  Search,
  Sparkles,
  Server,
  ArrowRight,
  ShieldCheck,
  HelpCircle,
  ExternalLink
} from 'lucide-react';

// Preset soal & skenario praktikum
const PRESETS = [
  {
    name: '🎯 Tugas Flowchart (/26)',
    ip: '192.168.1.0/24',
    prefix: 26,
    desc: 'Soal praktikum: 192.168.1.0/24 dibagi 4 subnet /26'
  },
  {
    name: '🏢 Kantor Cabang (/27)',
    ip: '192.168.10.0/24',
    prefix: 27,
    desc: '8 subnet dengan masing-masing 30 host usable'
  },
  {
    name: '🌐 Kampus Kelas B (/20)',
    ip: '172.16.0.0/16',
    prefix: 20,
    desc: '16 subnet dengan masing-masing 4094 host usable'
  },
  {
    name: '⚡ Point-to-Point WAN (/30)',
    ip: '192.168.100.0/24',
    prefix: 30,
    desc: '64 link router point-to-point (2 host usable)'
  }
];

export default function App() {
  const [alamatAwal, setAlamatAwal] = useState('192.168.1.0/24');
  const [prefixBaru, setPrefixBaru] = useState(26);
  const [activeTab, setActiveTab] = useState('overview');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedKey, setCopiedKey] = useState(null);
  const [activePreset, setActivePreset] = useState(0);

  // Extract base prefix from alamatAwal
  const prefixAwalDetected = useMemo(() => {
    if (alamatAwal.includes('/')) {
      const p = parseInt(alamatAwal.split('/')[1], 10);
      if (!isNaN(p) && p >= 0 && p <= 32) return p;
    }
    return 24;
  }, [alamatAwal]);

  // Fungsi fetch data ke Python FastAPI Backend (dengan fallback client-side calculator)
  const hitungSubnet = async (ipStr = alamatAwal, newP = prefixBaru) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/calculate?alamat_awal=${encodeURIComponent(ipStr)}&prefix_baru=${newP}&limit=512`
      );

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || `HTTP Error ${response.status}`);
      }

      const resData = await response.json();
      setData(resData);
    } catch (err) {
      console.warn('Backend API request failed, utilizing client-side calculation engine:', err.message);
      // Fallback calculation in JS so app works immediately
      try {
        const fallbackData = calculateSubnetClient(ipStr, newP);
        setData(fallbackData);
      } catch (clientErr) {
        setError(clientErr.message || 'Gagal memproses subnet');
      }
    } finally {
      setLoading(false);
    }
  };

  // Trigger calculation on load or when input changes
  useEffect(() => {
    hitungSubnet(alamatAwal, prefixBaru);
  }, []);

  const handleApplyPreset = (preset, index) => {
    setActivePreset(index);
    setAlamatAwal(preset.ip);
    setPrefixBaru(preset.prefix);
    hitungSubnet(preset.ip, preset.prefix);
  };

  const handleCopy = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleExportCSV = () => {
    if (!data || !data.subnets) return;
    const headers = ['No', 'Subnet', 'Network ID', 'Host Pertama', 'Host Terakhir', 'Broadcast', 'Usable Host', 'Netmask'];
    const rows = data.subnets.map(s => [
      s.no,
      s.subnet,
      s.network_id,
      s.host_pertama,
      s.host_terakhir,
      s.broadcast,
      s.jumlah_host,
      s.netmask
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `alokasi_subnet_${alamatAwal.replace('/', '_')}_to_${prefixBaru}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Filter subnets for table
  const filteredSubnets = useMemo(() => {
    if (!data || !data.subnets) return [];
    if (!searchQuery.trim()) return data.subnets;
    const q = searchQuery.toLowerCase();
    return data.subnets.filter(
      s =>
        s.subnet.toLowerCase().includes(q) ||
        s.network_id.toLowerCase().includes(q) ||
        s.host_pertama.toLowerCase().includes(q) ||
        s.host_terakhir.toLowerCase().includes(q) ||
        s.broadcast.toLowerCase().includes(q)
    );
  }, [data, searchQuery]);

  // Generate ASCII CLI terminal output text matching Python output
  const terminalText = useMemo(() => {
    if (!data) return '';
    const divider = '='.repeat(68);
    const tblDivider = '-'.repeat(99);

    const subValidList = data.subnets.slice(0, 8).map(s => `  - Subnet ${s.no}: ${s.subnet}`).join('\n');
    const tableRows = data.subnets.slice(0, 16).map(s => 
      `| ${String(s.no).padEnd(3)} | ${s.subnet.padEnd(18)} | ${s.network_id.padEnd(15)} | ${s.host_pertama.padEnd(15)} | ${s.host_terakhir.padEnd(15)} | ${s.broadcast.padEnd(15)} | ${String(s.jumlah_host).padEnd(6)} |`
    ).join('\n');

    return `${divider}
               PROGRAM KALKULATOR SUBNETTING IPV4
           Berdasarkan Flowchart Praktikum Modul ipaddress
${divider}

[+] OUTPUT 1: INFORMASI AWAL
  * Jaringan Awal        : ${data.alamat_awal}
  * Subnet Mask Awal     : ${data.subnet_mask_awal} (/${data.prefix_awal})
  * Prefix Baru          : /${data.prefix_baru}
  * Subnet Mask Baru     : ${data.subnet_mask_baru}
  * Bit yang Dipinjam (n): ${data.bit_dipinjam} bit (/${data.prefix_baru} - /${data.prefix_awal})
  * Rumus Jumlah Subnet  : 2^${data.bit_dipinjam}
  * Jumlah Subnet        : ${data.jumlah_subnet} Subnet

[+] OUTPUT 2: INFORMASI HOST PER SUBNET
  * Bit Host (h)         : ${data.bit_host} bit (32 - ${data.prefix_baru})
  * Rumus Total IP       : 2^${data.bit_host}
  * Total IP / Subnet    : ${data.total_ip} IP
  * Rumus Host Usable    : ${data.total_ip} - 2
  * Host Usable / Subnet : ${data.host_per_subnet} Host

[+] LOOP 1: MENAMPILKAN SUBNET VALID
${subValidList}${data.subnets.length > 8 ? `\n  ... (+${data.subnets.length - 8} subnet lainnya)` : ''}

[+] LOOP 2: TABEL ALOKASI IP SETIAP SUBNET
${tblDivider}
| No  | Subnet             | Network ID      | Host Pertama    | Host Terakhir   | Broadcast       | Usable |
${tblDivider}
${tableRows}
${tblDivider}${data.subnets.length > 16 ? `\n(Menampilkan 16 dari total ${data.total_subnets_count} subnet)` : ''}

[+] HASIL AKHIR (KONSEPTUAL):
  * Jumlah subnet          = ${data.jumlah_subnet}
  * Host usable per subnet = ${data.host_per_subnet}
  * Subnet valid           =
${data.subnets.slice(0, 4).map(s => `    - ${s.subnet}`).join('\n')}
${divider}`;
  }, [data]);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand-section">
          <div className="brand-logo-icon">
            <Network size={28} />
          </div>
          <div>
            <h1 className="brand-title">
              SubnetIQ <span style={{ fontSize: '0.9rem', color: '#818cf8', fontWeight: 600 }}>v2.0</span>
            </h1>
            <p className="brand-subtitle">
              Kalkulator Subnetting IPv4 • Python <span className="mono">ipaddress</span> + React
            </p>
          </div>
        </div>

        <div className="header-badges">
          <span className="badge badge-python">
            <Server size={14} /> Python 3.14 API
          </span>
          <span className="badge badge-react">
            <Cpu size={14} /> React 19 Frontend
          </span>
          <span className="badge badge-flowchart">
            <ShieldCheck size={14} /> Sesuai Flowchart Praktikum
          </span>
        </div>
      </header>

      {/* Hero Calculator Card */}
      <section className="glass-card calc-hero-card">
        <div className="hero-header">
          <div className="hero-title-group">
            <h2>Parameter Subnetting</h2>
            <p>Masukkan alamat jaringan awal dan tentukan prefix CIDR baru untuk menghitung subnet</p>
          </div>
          <button
            className="btn-icon-text"
            onClick={() => handleApplyPreset(PRESETS[0], 0)}
            title="Reset ke Soal Praktikum"
          >
            <RotateCcw size={14} /> Reset Soal Tugas
          </button>
        </div>

        {/* Preset Chips */}
        <div className="presets-container">
          <span className="preset-label">Pilihan Cepat:</span>
          {PRESETS.map((p, idx) => (
            <button
              key={p.name}
              className={`preset-chip ${activePreset === idx ? 'active-tugas' : ''}`}
              onClick={() => handleApplyPreset(p, idx)}
            >
              {p.name}
            </button>
          ))}
        </div>

        {/* Input Form Grid */}
        <form
          className="input-grid"
          onSubmit={(e) => {
            e.preventDefault();
            hitungSubnet(alamatAwal, prefixBaru);
          }}
        >
          <div className="form-group">
            <label className="form-label" htmlFor="ip-input">
              <span>Alamat Jaringan Awal (CIDR)</span>
              <span className="hint">Contoh: 192.168.1.0/24</span>
            </label>
            <div className="input-wrapper">
              <Network size={18} className="input-icon" />
              <input
                id="ip-input"
                className="custom-input"
                type="text"
                value={alamatAwal}
                placeholder="192.168.1.0/24"
                onChange={(e) => {
                  setActivePreset(-1);
                  setAlamatAwal(e.target.value);
                }}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="prefix-select">
              <span>Prefix Baru (Subnet Mask Baru)</span>
              <span className="hint">Rentang: /{prefixAwalDetected} s/d /32</span>
            </label>
            <div className="prefix-selector-group">
              <select
                id="prefix-select"
                className="prefix-select"
                value={prefixBaru}
                onChange={(e) => {
                  setActivePreset(-1);
                  const val = parseInt(e.target.value, 10);
                  setPrefixBaru(val);
                }}
              >
                {Array.from({ length: 33 }, (_, i) => i)
                  .filter((p) => p >= prefixAwalDetected)
                  .map((p) => (
                    <option key={p} value={p}>
                      /{p} ({prefixToSubnetMask(p)})
                    </option>
                  ))}
              </select>
            </div>
          </div>

          <button
            type="submit"
            className="btn-calculate"
            disabled={loading}
            id="btn-hitung"
          >
            {loading ? (
              <span>Menghitung...</span>
            ) : (
              <>
                <Sparkles size={18} /> Hitung Subnet
              </>
            )}
          </button>
        </form>

        {/* Prefix Range Slider */}
        <div className="prefix-slider-box">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/{prefixAwalDetected}</span>
          <input
            type="range"
            min={prefixAwalDetected}
            max={32}
            value={prefixBaru}
            onChange={(e) => {
              const val = parseInt(e.target.value, 10);
              setPrefixBaru(val);
              hitungSubnet(alamatAwal, val);
            }}
          />
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/32</span>
          <span className="slider-val-badge">Aktif: /{prefixBaru}</span>
        </div>
      </section>

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          <HelpCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Results Section */}
      {data && (
        <>
          {/* Key Metrics Row */}
          <section className="metrics-row">
            <div className="metric-card">
              <div className="metric-icon-box purple">
                <Layers size={24} />
              </div>
              <div className="metric-info">
                <span className="metric-title">Jumlah Subnet</span>
                <span className="metric-value">{data.jumlah_subnet.toLocaleString()} Subnet</span>
                <span className="metric-sub">Rumus: 2^{data.bit_dipinjam} (pinjam {data.bit_dipinjam} bit)</span>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon-box cyan">
                <Cpu size={24} />
              </div>
              <div className="metric-info">
                <span className="metric-title">Host Usable / Subnet</span>
                <span className="metric-value">{data.host_per_subnet.toLocaleString()} Host</span>
                <span className="metric-sub">Rumus: 2^{data.bit_host} - 2</span>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon-box emerald">
                <Network size={24} />
              </div>
              <div className="metric-info">
                <span className="metric-title">Total Alamat IP</span>
                <span className="metric-value">{data.total_ip.toLocaleString()} IP / Subnet</span>
                <span className="metric-sub">Bit Host (h) = {data.bit_host} bit</span>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon-box amber">
                <Server size={24} />
              </div>
              <div className="metric-info">
                <span className="metric-title">Subnet Mask Baru</span>
                <span className="metric-value mono" style={{ fontSize: '1.05rem' }}>{data.subnet_mask_baru}</span>
                <span className="metric-sub">CIDR: /{data.prefix_baru} • {data.ip_class}</span>
              </div>
            </div>
          </section>

          {/* Navigation Tabs */}
          <nav className="tabs-nav">
            <button
              className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              <Cpu size={16} /> Alur Perhitungan Flowchart
            </button>
            <button
              className={`tab-btn ${activeTab === 'table' ? 'active' : ''}`}
              onClick={() => setActiveTab('table')}
            >
              <TableIcon size={16} /> Tabel Alokasi IP ({data.total_subnets_count})
            </button>
            <button
              className={`tab-btn ${activeTab === 'visual' ? 'active' : ''}`}
              onClick={() => setActiveTab('visual')}
            >
              <Layers size={16} /> Visualisasi Blok CIDR
            </button>
            <button
              className={`tab-btn ${activeTab === 'terminal' ? 'active' : ''}`}
              onClick={() => setActiveTab('terminal')}
            >
              <Terminal size={16} /> Output Terminal Python
            </button>
            <button
              className={`tab-btn ${activeTab === 'jurnal' ? 'active' : ''}`}
              onClick={() => setActiveTab('jurnal')}
            >
              <BookOpen size={16} /> Penjelasan Istilah (Jurnal Praktikum)
            </button>
          </nav>

          {/* Tab 1: Overview & Flowchart Steps */}
          {activeTab === 'overview' && (
            <div className="glass-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', marginBottom: 4 }}>Tahapan Algoritma Subnetting Sesuai Flowchart</h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Implementasi kode modul Python <span className="mono">ipaddress</span>
                  </p>
                </div>
                <span className="badge badge-flowchart">
                  Flowchart Praktikum Validated
                </span>
              </div>

              <div className="flowchart-grid">
                <div className="step-card">
                  <div className="step-header">
                    <span className="step-num">1</span>
                    <span className="step-name">Input & Jaringan Awal</span>
                  </div>
                  <div className="step-detail">
                    alamat_awal = "{data.alamat_awal}"<br />
                    prefix_baru = {data.prefix_baru}
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Inisialisasi objek: <span className="mono">ip_network(alamat_awal, strict=False)</span>
                  </p>
                </div>

                <div className="step-card">
                  <div className="step-header">
                    <span className="step-num">2</span>
                    <span className="step-name">Perhitungan Bit Subnet</span>
                  </div>
                  <div className="step-detail">
                    bit_dipinjam = {data.prefix_baru} - {data.prefix_awal} = {data.bit_dipinjam} bit<br />
                    jumlah_subnet = 2^{data.bit_dipinjam} = {data.jumlah_subnet} subnet
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Meminjam {data.bit_dipinjam} bit dari porsi host untuk network prefix
                  </p>
                </div>

                <div className="step-card">
                  <div className="step-header">
                    <span className="step-num">3</span>
                    <span className="step-name">Perhitungan Host per Subnet</span>
                  </div>
                  <div className="step-detail">
                    bit_host = 32 - {data.prefix_baru} = {data.bit_host} bit<br />
                    total_ip = 2^{data.bit_host} = {data.total_ip} IP<br />
                    host_usable = {data.total_ip} - 2 = {data.host_per_subnet} host
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    2 IP dikurangi untuk Network ID dan Broadcast Address
                  </p>
                </div>

                <div className="step-card">
                  <div className="step-header">
                    <span className="step-num">4</span>
                    <span className="step-name">Loop 1: Subnet Valid</span>
                  </div>
                  <div className="step-detail">
                    subnet_list = list(jaringan.subnets(new_prefix={data.prefix_baru}))<br />
                    {data.subnets.slice(0, 2).map(s => s.subnet).join(', ')} ...
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Menghasilkan {data.total_subnets_count} subnet terbagi rata
                  </p>
                </div>
              </div>

              {/* Binary Representation Breakdown */}
              <div className="binary-box">
                <h4 style={{ fontSize: '0.95rem', marginBottom: 12, color: '#38bdf8' }}>
                  Representasi Biner 32-Bit (Oktet IPv4)
                </h4>
                <div className="binary-row">
                  <span>Network Address Awal ({data.network_awal}):</span>
                  <span className="binary-text">{data.binary_network || toBinaryOctets(data.network_awal)}</span>
                </div>
                <div className="binary-row">
                  <span>Subnet Mask Awal ({data.subnet_mask_awal}):</span>
                  <span className="binary-text">{data.binary_netmask_awal || toBinaryOctets(data.subnet_mask_awal)}</span>
                </div>
                <div className="binary-row">
                  <span>Subnet Mask Baru ({data.subnet_mask_baru}):</span>
                  <span className="binary-text" style={{ color: '#818cf8' }}>
                    {data.binary_netmask_baru || toBinaryOctets(data.subnet_mask_baru)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Tab 2: Subnet Allocation Table */}
          {activeTab === 'table' && (
            <div className="glass-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div className="input-wrapper" style={{ width: 280 }}>
                    <Search size={16} className="input-icon" />
                    <input
                      type="text"
                      className="custom-input"
                      placeholder="Cari IP, Subnet, Host..."
                      style={{ padding: '8px 12px 8px 38px', fontSize: '0.85rem' }}
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    Menampilkan {filteredSubnets.length} dari {data.total_subnets_count} subnet
                  </span>
                </div>

                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    className={`btn-icon-text ${copiedKey === 'table' ? 'copied' : ''}`}
                    onClick={() => {
                      const text = data.subnets.map(s => `${s.no}\t${s.subnet}\t${s.network_id}\t${s.host_pertama}\t${s.host_terakhir}\t${s.broadcast}\t${s.jumlah_host}`).join('\n');
                      handleCopy(text, 'table');
                    }}
                  >
                    {copiedKey === 'table' ? <Check size={14} /> : <Copy size={14} />} Salin Tabel
                  </button>
                  <button className="btn-icon-text" onClick={handleExportCSV}>
                    <Download size={14} /> Download CSV
                  </button>
                </div>
              </div>

              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>No</th>
                      <th>Subnet (CIDR)</th>
                      <th>Network ID</th>
                      <th>Host Pertama</th>
                      <th>Host Terakhir</th>
                      <th>Broadcast Address</th>
                      <th>Host Usable</th>
                      <th>Subnet Mask</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredSubnets.map((sub) => (
                      <tr key={sub.no}>
                        <td>{sub.no}</td>
                        <td style={{ color: '#818cf8', fontWeight: 600 }}>{sub.subnet}</td>
                        <td>{sub.network_id}</td>
                        <td style={{ color: '#38bdf8' }}>{sub.host_pertama}</td>
                        <td style={{ color: '#38bdf8' }}>{sub.host_terakhir}</td>
                        <td style={{ color: '#f43f5e' }}>{sub.broadcast}</td>
                        <td>
                          <span className="badge-table-usable">{sub.jumlah_host} Host</span>
                        </td>
                        <td style={{ color: 'var(--text-muted)' }}>{sub.netmask}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Tab 3: Visual CIDR Bar */}
          {activeTab === 'visual' && (
            <div className="glass-card cidr-visual-section">
              <h3 style={{ fontSize: '1.2rem', marginBottom: 6 }}>Visualisasi Pembagian Blok Ruang Alamat IP</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Blok jaringan induk <span className="mono" style={{ color: '#38bdf8' }}>{data.alamat_awal}</span> dipecah menjadi{' '}
                <span className="mono" style={{ color: '#34d399' }}>{data.jumlah_subnet} subnet berukuran /{data.prefix_baru}</span>.
              </p>

              {/* Graphical visual bar */}
              <div className="cidr-bar-container">
                {data.subnets.slice(0, 32).map((s, idx) => {
                  const colors = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];
                  const color = colors[idx % colors.length];
                  return (
                    <div
                      key={s.no}
                      className="cidr-bar-segment"
                      style={{
                        flex: 1,
                        background: color,
                        opacity: 0.9
                      }}
                      title={`Subnet ${s.no}: ${s.subnet}\nHost: ${s.host_pertama} - ${s.host_terakhir}\nBroadcast: ${s.broadcast}`}
                    >
                      {data.subnets.length <= 8 ? s.subnet : `#${s.no}`}
                    </div>
                  );
                })}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12, marginTop: 20 }}>
                {data.subnets.slice(0, 8).map((s) => (
                  <div
                    key={s.no}
                    style={{
                      background: 'rgba(15, 23, 42, 0.6)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '12px 14px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                      <span style={{ fontWeight: 700, color: '#818cf8', fontSize: '0.85rem' }}>Subnet {s.no}</span>
                      <span className="mono" style={{ fontSize: '0.8rem', color: '#34d399' }}>/{data.prefix_baru}</span>
                    </div>
                    <div className="mono" style={{ fontSize: '0.82rem', marginBottom: 4 }}>
                      Net: {s.network_id}
                    </div>
                    <div className="mono" style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                      Range: {s.host_pertama} - {s.host_terakhir}
                    </div>
                    <div className="mono" style={{ fontSize: '0.78rem', color: '#f43f5e' }}>
                      Bcast: {s.broadcast}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 4: Terminal Python Output */}
          {activeTab === 'terminal' && (
            <div className="glass-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', marginBottom: 4 }}>Tampilan Konsol Python (subnet_calc.py)</h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Output persis yang dihasilkan program saat dijalankan via terminal Python
                  </p>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    className={`btn-icon-text ${copiedKey === 'cmd' ? 'copied' : ''}`}
                    onClick={() => handleCopy(`python3 subnet_calc.py ${data.alamat_awal} ${data.prefix_baru}`, 'cmd')}
                  >
                    {copiedKey === 'cmd' ? <Check size={14} /> : <Copy size={14} />} Salin Perintah CLI
                  </button>
                  <button
                    className={`btn-icon-text ${copiedKey === 'terminal' ? 'copied' : ''}`}
                    onClick={() => handleCopy(terminalText, 'terminal')}
                  >
                    {copiedKey === 'terminal' ? <Check size={14} /> : <Copy size={14} />} Salin Output
                  </button>
                </div>
              </div>

              <div className="terminal-window">
                <div className="terminal-header">
                  <div className="terminal-dots">
                    <span className="terminal-dot dot-red"></span>
                    <span className="terminal-dot dot-yellow"></span>
                    <span className="terminal-dot dot-green"></span>
                  </div>
                  <span className="terminal-title">python3 subnet_calc.py {data.alamat_awal} {data.prefix_baru}</span>
                  <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>bash</span>
                </div>
                <div className="terminal-body">{terminalText}</div>
              </div>
            </div>
          )}

          {/* Tab 5: Jurnal Praktikum & Penjelasan Istilah */}
          {activeTab === 'jurnal' && (
            <div className="glass-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', marginBottom: 4 }}>Penjelasan Istilah Subnetting (Untuk Slide & Jurnal Praktikum)</h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Penjelasan materi dan konsep dasar subnetting sesuai instruksi penugasan praktikum Edlink
                  </p>
                </div>
                <button
                  className={`btn-icon-text ${copiedKey === 'jurnal' ? 'copied' : ''}`}
                  onClick={() => {
                    const txt = (data.penjelasan_istilah || []).map(p => `• ${p.istilah}:\n  ${p.arti}\n  Contoh: ${p.contoh}\n`).join('\n');
                    handleCopy(txt, 'jurnal');
                  }}
                >
                  {copiedKey === 'jurnal' ? <Check size={14} /> : <Copy size={14} />} Salin Penjelasan
                </button>
              </div>

              <div className="glossary-grid">
                {(data.penjelasan_istilah || []).map((term, i) => (
                  <div key={i} className="glossary-card">
                    <div className="glossary-title">
                      <BookOpen size={16} /> {term.istilah}
                    </div>
                    <p className="glossary-desc">{term.arti}</p>
                    <div className="glossary-example">
                      <strong>Contoh Kasus:</strong> {term.contoh}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Aplikasi Kalkulator Subnetting IPv4 • Dibuat dengan <strong>Python (<span className="mono">ipaddress</span> + FastAPI)</strong> dan <strong>React</strong>.
        </p>
        <p style={{ marginTop: 6, fontSize: '0.75rem' }}>
          Sesuai Flowchart Praktikum Jaringan Komputer: Subnetting 192.168.1.0/24 menjadi 4 subnet /26.
        </p>
      </footer>
    </div>
  );
}

// Client-side helper functions for zero-downtime calculation
function prefixToSubnetMask(prefix) {
  const mask = [];
  for (let i = 0; i < 4; i++) {
    const bits = Math.max(0, Math.min(8, prefix - i * 8));
    mask.push(256 - Math.pow(2, 8 - bits));
  }
  return mask.join('.');
}

function toBinaryOctets(ipStr) {
  try {
    return ipStr.split('.').map(octet => Number(octet).toString(2).padStart(8, '0')).join('.');
  } catch (e) {
    return '';
  }
}

function ipToLong(ip) {
  return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet, 10), 0) >>> 0;
}

function longToIp(long) {
  return [
    (long >>> 24) & 255,
    (long >>> 16) & 255,
    (long >>> 8) & 255,
    long & 255
  ].join('.');
}

// Client-side subnet calculator fallback
function calculateSubnetClient(ipInput, newPrefix) {
  let [ipStr, rawPrefix] = ipInput.trim().split('/');
  const oldPrefix = rawPrefix ? parseInt(rawPrefix, 10) : 24;

  if (newPrefix < oldPrefix) {
    throw new Error(`Prefix baru (/${newPrefix}) harus lebih besar atau sama dengan prefix awal (/${oldPrefix})!`);
  }

  const baseLong = ipToLong(ipStr);
  const oldMaskLong = ((0xFFFFFFFF << (32 - oldPrefix)) >>> 0);
  const networkLong = (baseLong & oldMaskLong) >>> 0;

  const bitDipinjam = newPrefix - oldPrefix;
  const jumlahSubnet = Math.pow(2, bitDipinjam);
  const bitHost = 32 - newPrefix;
  const totalIp = Math.pow(2, bitHost);
  const hostUsable = totalIp >= 4 ? totalIp - 2 : (totalIp === 2 ? 2 : 1);

  const subnetMaskBaru = prefixToSubnetMask(newPrefix);
  const subnetMaskAwal = prefixToSubnetMask(oldPrefix);

  const subnets = [];
  const limit = Math.min(jumlahSubnet, 512);

  for (let i = 0; i < limit; i++) {
    const subNetLong = (networkLong + i * totalIp) >>> 0;
    const bcastLong = (subNetLong + totalIp - 1) >>> 0;

    const netAddr = longToIp(subNetLong);
    const bcastAddr = longToIp(bcastLong);
    const hostPertama = totalIp >= 4 ? longToIp(subNetLong + 1) : netAddr;
    const hostTerakhir = totalIp >= 4 ? longToIp(bcastLong - 1) : bcastAddr;

    subnets.push({
      no: i + 1,
      subnet: `${netAddr}/${newPrefix}`,
      network_id: netAddr,
      host_pertama: hostPertama,
      host_terakhir: hostTerakhir,
      range_host: `${hostPertama} - ${hostTerakhir}`,
      broadcast: bcastAddr,
      jumlah_host: hostUsable,
      netmask: subnetMaskBaru
    });
  }

  return {
    alamat_awal: `${longToIp(networkLong)}/${oldPrefix}`,
    network_awal: longToIp(networkLong),
    subnet_mask_awal: subnetMaskAwal,
    prefix_awal: oldPrefix,
    prefix_baru: newPrefix,
    subnet_mask_baru: subnetMaskBaru,
    bit_dipinjam: bitDipinjam,
    jumlah_subnet: jumlahSubnet,
    bit_host: bitHost,
    total_ip: totalIp,
    host_per_subnet: hostUsable,
    subnets,
    total_subnets_count: jumlahSubnet,
    ip_class: 'Kelas C',
    penjelasan_istilah: [
      {
        istilah: "Network ID (Alamat Jaringan)",
        arti: "Alamat IP pertama dalam subnet yang berfungsi sebagai identitas kelompok jaringan. IP ini tidak boleh digunakan untuk perangkat host komputer.",
        contoh: `Subnet 1: ${subnets[0]?.network_id || '-'}`
      },
      {
        istilah: "Broadcast Address",
        arti: "Alamat IP terakhir dalam subnet yang dipakai untuk mengirim pesan secara serentak (broadcast) ke seluruh host dalam subnet tersebut. Tidak boleh dipakai sebagai IP host.",
        contoh: `Subnet 1: ${subnets[0]?.broadcast || '-'}`
      },
      {
        istilah: "Usable Host Range (Rentang IP Host Valid)",
        arti: "Daftar alamat IP di antara Network ID dan Broadcast Address yang sah dan dapat dialokasikan ke perangkat (PC, laptop, smartphone, router interface).",
        contoh: `Subnet 1: ${subnets[0]?.range_host || '-'}`
      },
      {
        istilah: "Subnet Mask & Prefix (CIDR)",
        arti: "Penanda pembagi antara porsi Network dan porsi Host dalam alamat 32-bit IPv4. Angka prefix (contoh: /26) menunjukkan banyaknya bit 1 pada netmask.",
        contoh: `/${newPrefix} = ${subnetMaskBaru}`
      },
      {
        istilah: "Bit Dipinjam (n) & Jumlah Subnet",
        arti: "Banyaknya bit host yang dialihkan (dipinjam) menjadi bit subnet (n = Prefix Baru - Prefix Awal). Rumus jumlah subnet adalah 2ⁿ.",
        contoh: `2^${bitDipinjam} = ${jumlahSubnet} subnet`
      },
      {
        istilah: "Bit Host (h) & Usable Host",
        arti: "Sisa bit yang dialokasikan untuk penomoran host (h = 32 - Prefix Baru). Rumus total IP adalah 2ʰ, dan IP yang bisa digunakan adalah 2ʰ - 2.",
        contoh: `2^${bitHost} - 2 = ${hostUsable} host per subnet`
      }
    ]
  };
}
