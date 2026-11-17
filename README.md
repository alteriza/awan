# ☁️ Awan CLI (GITUS) — GitHub Release Cloud Storage

**Awan CLI (GITUS)** adalah aplikasi penyimpanan awan (*cloud storage*) pribadi berbasis **Command Line Interface (CLI)** yang dibangun menggunakan Python. Aplikasi ini memanfaatkan fitur **GitHub Releases** dan **Git Tags** pada repositori pribadi (*private repository*) untuk menyimpan, mengelola, mengunduh, dan menghapus file secara terstruktur layaknya direktori penyimpanan lokal.

> 📑 **Dokumentasi AI Logbook:** Riwayat lengkap interaksi, *prompt*, saran AI, dan validasi mandiri tim pengembang terdokumentasi di **[AI_LOGBOOK.md](./AI_LOGBOOK.md)**.

## 📋 Daftar Isi

1. [Latar Belakang & Tujuan](#-latar-belakang--tujuan)
2. [Fitur Unggulan](#-fitur-unggulan)
3. [Teknologi & Struktur Proyek](#-teknologi--struktur-proyek)
4. [Persiapan Akun & Infrastruktur GitHub](#-persiapan-akun--infrastruktur-github)
   * [1. Membuat Akun GitHub](#1-membuat-akun-github)
   * [2. Membuat Repository Private](#2-membuat-repository-private)
   * [3. Membuat Personal Access Token (PAT)](#3-membuat-personal-access-token-pat)
5. [Tutorial Instalasi & Setup per OS](#-tutorial-instalasi--setup-per-os)
   * [A. Windows (CMD / PowerShell)](#a-windows-cmd--powershell)
   * [B. Linux (Ubuntu / Debian / Arch / Fedora)](#b-linux-ubuntu--debian--arch--fedora)
   * [C. Termux (Android)](#c-termux-android)
6. [Panduan Penggunaan Awan CLI](#-panduan-penggunaan-awan-cli)
7. [Pemanfaatan Kecerdasan Artifisial (AI Usage Disclosure)](#-pemanfaatan-kecerdasan-artifisial-ai-usage-disclosure)
8. [Ketentuan & Batasan Penggunaan](#-ketentuan--batasan-penggunaan)
9. [Identitas Pengembang](#-identitas-pengembang)

## 🎯 Latar Belakang & Tujuan

### Masalah yang Diselesaikan

Layanan penyimpanan awan gratis pada umumnya memiliki batas kapasitas yang terbatas (seperti 5 GB hingga 15 GB) dan sering kali membutuhkan antarmuka web yang berat untuk sekadar mencadangkan (*backup*) atau memindahkan file antarperangkat (PC, laptop, maupun smartphone).

### Solusi & Target Pengguna

**Awan CLI (GITUS)** hadir sebagai solusi alternatif penyimpanan awan ringan berbasis terminal yang mendukung kapasitas unggah hingga **2 GB per file** (mengikuti kebijakan resmi GitHub Releases). Aplikasi ini ditujukan bagi **pelajar, mahasiswa, developer, maupun pengguna umum** yang membutuhkan sistem manajemen dan pencadangan file yang cepat, aman (berbasis *private repository*), dan lintas platform.

## ✨ Fitur Unggulan

* **Manajemen Folder Otomatis**: Setiap folder virtual di Awan CLI dipetakan secara otomatis ke objek *GitHub Release* dan *Git Tag* (spasi otomatis dikonversi menjadi tanda hubung `-`).
* **Multi-File & Batch Upload Cerdas**: Mendukung pengunggahan banyak file sekaligus melalui *drag & drop* ke terminal, pola *wildcard* (misalnya `*.pdf`, `*.jpg`), maupun memasukkan path folder lokal secara langsung.
* **Deteksi & Resolusi Konflik Nama File**: Jika file dengan nama yang sama sudah ada di folder tujuan, sistem otomatis menawarkan 3 opsi interaktif:
  * **`[t]` Timpa (*Overwrite*)**: Menghapus file lama dan menggantinya dengan versi terbaru.
  * **`[r]` Rename**: Menyimpan file baru dengan nama berbeda (ekstensi asli otomatis dipertahankan).
  * **`[c]` Cancel**: Membatalkan unggahan untuk file tersebut tanpa mengganggu antrean lainnya.
* **Hapus Massal (*Bulk Delete*)**: Menghapus beberapa folder sekaligus (beserta *Git Tag*-nya agar repositori tetap bersih) atau menghapus banyak file dalam satu perintah menggunakan pemisah spasi maupun koma.
* **Quick Upload via Argumen CLI**: Mengunggah file secara instan langsung saat menjalankan program dari terminal tanpa perlu masuk ke menu terlebih dahulu.
* **Antarmuka Terminal Modern & Portabel**: Dilengkapi tabel interaktif, *progress bar* pengunggahan, sistem halaman (*pagination* 8 item per halaman), serta penyimpanan kredensial dan unduhan yang terpusat di direktori skrip.

## 🛠 Teknologi & Struktur Proyek

### Teknologi yang Digunakan

* **Bahasa Pemrograman**: Python 3.8+
* **Pustaka Eksternal** (`requirements.txt`):
  * `requests` — Komunikasi HTTP dengan GitHub REST API v3 & GitHub Uploads API.
  * `rich` — Rendering tabel, panel, warna, status *spinner*, dan *progress bar* di terminal.
* **Modul Bawaan Python**: `json`, `pathlib`, `math`, `sys`, `glob`, `os`, `re`.
* **Infrastruktur Backend**: GitHub Releases API (`api.github.com` & `uploads.github.com`).

### Struktur Direktori

```text
├── main.py                  # Entry point aplikasi, alur menu interaktif, dan navigasi folder
├── github_api.py            # Klien REST API GitHub (CRUD Release, Tag, dan Asset)
├── config.py                # Manajemen penyimpanan & pembacaan konfigurasi lokal
├── utils.py                 # Utilitas parsing path, wildcard, S&K, dan tampilan bantuan
├── S&K.txt                  # Dokumen Syarat & Ketentuan penggunaan aplikasi
├── requirements.txt         # Daftar dependensi pustaka Python
├── README.md                # Dokumentasi utama & panduan penggunaan proyek
├── AI_LOGBOOK.md            # Logbook interaksi, saran AI, dan validasi mandiri pengembang
├── .gh_cloud_config.json    # (Otomatis dibuat) File konfigurasi kredensial lokal
└── download/                # (Otomatis dibuat) Direktori default hasil unduhan file
```

* **Pintasan Dokumentasi:** [README.md](./README.md) • [AI_LOGBOOK.md](./AI_LOGBOOK.md) • [S&K.txt](./S&K.txt)

## 🔐 Persiapan Akun & Infrastruktur GitHub

Sebelum menjalankan Awan CLI, pastikan kamu sudah memiliki akun GitHub, sebuah repositori berstatus **Private**, dan **Personal Access Token (PAT)**.

### 1. Membuat Akun GitHub

1. Buka situs resmi <https://github.com> melalui browser.
2. Klik tombol **Sign up** di pojok kanan atas.
3. Masukkan alamat **Email**, buat **Password**, dan tentukan **Username** (catat *username* ini karena akan digunakan saat konfigurasi Awan CLI).
4. Selesaikan verifikasi teka-teki (*captcha*) dan masukkan kode verifikasi yang dikirimkan ke email kamu.
5. Pilih paket **Free** untuk menyelesaikan pendaftaran.

### 2. Membuat Repository Private

> **Penting:** Selalu gunakan repositori berstatus **Private** agar file pribadi kamu tidak dapat dilihat atau diunduh oleh publik.

1. Masuk (*login*) ke akun GitHub kamu.
2. Klik ikon **`+`** di pojok kanan atas, lalu pilih **New repository** (atau akses <https://github.com/new>).
3. Isi **Repository name** (contoh: `awan-storage` atau `cloud-pribadi`).
4. Pada bagian visibilitas, pilih **Private** (ikon gembok).
5. *(Opsional)* Centang **Add a README file** agar repositori langsung terinisialisasi.
6. Klik tombol **Create repository**.

### 3. Membuat Personal Access Token (PAT)

Token ini berfungsi sebagai kunci akses agar Awan CLI dapat mengelola *Releases* di repositori kamu tanpa perlu memasukkan kata sandi akun setiap saat.

#### Opsi A: Menggunakan Tokens (Classic) — *Direkomendasikan & Paling Praktis*

1. Klik foto profil kamu di pojok kanan atas GitHub $\rightarrow$ pilih **Settings**.
2. Gulir ke menu paling bawah di bilah sisi kiri, lalu klik **Developer settings**.
3. Pilih **Personal access tokens** $\rightarrow$ **Tokens (classic)**.
4. Klik **Generate new token** $\rightarrow$ **Generate new token (classic)**.
5. Isi kolom **Note** (contoh: `Token Awan CLI`).
6. Atur **Expiration** (masa berlaku token, misalnya *90 days* atau *No expiration*).
7. Pada bagian **Select scopes**, centang **`repo`** (akses penuh ke repositori privat, *releases*, dan *tags*).
8. Gulir ke bawah dan klik **Generate token**.
9. **Segera salin dan simpan token** yang diawali dengan `ghp_...` karena token hanya ditampilkan satu kali.

#### Opsi B: Menggunakan Fine-Grained Personal Access Tokens (Lebih Spesifik)

1. Masuk ke **Settings** $\rightarrow$ **Developer settings** $\rightarrow$ **Personal access tokens** $\rightarrow$ **Fine-grained tokens**.
2. Klik **Generate new token**.
3. Isi **Token name** dan atur **Expiration**.
4. Pada bagian **Repository access**, pilih **Only select repositories** $\rightarrow$ pilih repositori penyimpanan awan yang baru saja kamu buat.
5. Buka bagian **Permissions** $\rightarrow$ **Repository permissions**, cari bagian **Contents**, lalu ubah aksesnya menjadi **Read and write**.
6. Klik **Generate token**, lalu salin token yang muncul (`github_pat_...`).

## 💻 Tutorial Instalasi & Setup per OS

Pastikan file `requirements.txt` di direktori utama repositori berisi daftar pustaka berikut:

```text
requests
rich
```

Ikuti panduan sesuai sistem operasi yang kamu gunakan:

### A. Windows (CMD / PowerShell)

1. **Instal Python & Git**:
   * Unduh Python dari [python.org/downloads](https://www.python.org/downloads/). Saat instalasi, **wajib centang opsi `Add Python to PATH`**.
   * Unduh Git dari [git-scm.com](https://git-scm.com/download/win) dan instal seperti biasa.
2. **Clone Repositori**:
   Buka **Command Prompt (CMD)** atau **PowerShell**, lalu jalankan:
   ```bash
   git clone https://github.com/<username-pemilik-repo>/<nama-repo>.git
   cd <nama-repo>
   ```
3. **Buat Virtual Environment (Opsional namun Disarankan)**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
4. **Instal Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Jalankan Aplikasi**:
   ```bash
   python main.py
   ```

### B. Linux (Ubuntu / Debian / Arch / Fedora)

1. **Instal Python, Pip, dan Git**:
   * **Ubuntu / Debian / Linux Mint**:
     ```bash
     sudo apt update && sudo apt install -y python3 python3-pip python3-venv git
     ```
   * **Arch Linux / Manjaro**:
     ```bash
     sudo pacman -Syu python python-pip git
     ```
   * **Fedora**:
     ```bash
     sudo dnf install -y python3 python3-pip git
     ```
2. **Clone Repositori**:
   ```bash
   git clone https://github.com/<username-pemilik-repo>/<nama-repo>.git
   cd <nama-repo>
   ```
3. **Buat Virtual Environment & Instal Dependensi**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Jalankan Aplikasi**:
   ```bash
   python3 main.py
   ```

### C. Termux (Android)

1. **Instal Termux**:
   Unduh aplikasi **Termux** versi terbaru melalui **F-Droid** atau **GitHub Releases resmi Termux** (hindari versi lama di Play Store).
2. **Perbarui Paket & Berikan Izin Penyimpanan**:
   Buka Termux dan jalankan perintah berikut untuk memperbarui sistem serta mengizinkan Termux mengakses memori internal HP (`/sdcard`):
   ```bash
   pkg update && pkg upgrade -y
   termux-setup-storage
   ```
   *(Ketuk **Izinkan / Allow** saat muncul jendela permintaan izin akses file di Android).*
3. **Instal Python dan Git**:
   ```bash
   pkg install -y python git
   ```
4. **Clone Repositori & Instal Dependensi**:
   ```bash
   git clone https://github.com/<username-pemilik-repo>/<nama-repo>.git
   cd <nama-repo>
   pip install -r requirements.txt
   ```
5. **Jalankan Aplikasi**:
   ```bash
   python main.py
   ```
   > **Tips Termux:** Untuk mengunggah file dari penyimpanan HP, kamu bisa menggunakan path `/sdcard/Download/namafile.pdf` atau `~/storage/downloads/namafile.pdf`.

## 📖 Panduan Penggunaan Awan CLI

### 1. Persetujuan Syarat & Ketentuan (S&K)

Saat dijalankan, aplikasi akan menampilkan isi file [S&K.txt](./S&K.txt). Ketik `y` lalu tekan **Enter** untuk menyetujui dan melanjutkan.

### 2. Konfigurasi Awal

Jika aplikasi dijalankan untuk pertama kalinya (atau setelah menjalankan perintah `reset`), kamu akan diminta mengisi 4 data berikut:

1. **Pilih Sistem Operasi**: Ketik `1` (Windows), `2` (Linux), atau `3` (Termux).
2. **GitHub Token**: Tempelkan token PAT (`ghp_...` atau `github_pat_...`) yang sudah dibuat.
3. **Username GitHub**: Masukkan username akun GitHub kamu.
4. **Nama Repository**: Masukkan nama repositori *private* yang sudah disiapkan.

Data konfigurasi akan disimpan secara lokal pada file `.gh_cloud_config.json`.

### 3. Daftar Perintah di Level Utama / Root (`/`)

| Perintah | Alias | Fungsi & Contoh Penggunaan |
| :--- | :--- | :--- |
| `<nama_folder>` | `open`, `cd`, `ls` | Masuk ke dalam folder (Contoh: `utama` atau `open dokumen`) |
| `up` | `upload` | Membuka mode unggah 1 atau banyak file sekaligus |
| `dl <folder/file>` | `download` | Mengunduh file langsung (Contoh: `dl utama/laporan.pdf`) |
| `del <target1, target2>` | `delete`, `rm` | Menghapus massal folder atau file tertentu (Contoh: `del arsip, utama/foto.jpg`) |
| `n` / `p` | `next` / `prev` | Berpindah ke halaman daftar folder berikutnya atau sebelumnya |
| `page <angka>` | `pg <angka>` | Melompat langsung ke nomor halaman tertentu (Contoh: `page 2`) |
| `r` | `refresh` | Menyegarkan (*reload*) daftar folder terbaru dari GitHub |
| `reset` | — | Mengatur ulang pilihan OS, Token, Username, atau Repository |
| `h` | `help`, `?` | Menampilkan tabel panduan perintah |
| `0` | `exit`, `quit`, `q` | Keluar dari aplikasi Awan CLI |

### 4. Daftar Perintah di Dalam Folder (`/nama-folder`)

| Perintah | Alias | Fungsi & Contoh Penggunaan |
| :--- | :--- | :--- |
| `up` | `upload` | Mengunggah file langsung ke folder yang sedang dibuka |
| `dl <nama_file>` | `download` | Mengunduh file dari folder aktif (Contoh: `dl tugas.zip`) |
| `del <file1, file2>` | `delete`, `rm` | Menghapus banyak file sekaligus di folder aktif (Contoh: `del a.txt b.jpg, c.pdf`) |
| `<nama_file>` | — | Memilih file secara cepat untuk langsung diunduh (`dl`) atau dihapus (`del`) |
| `..` | `back`, `kembali` | Kembali ke halaman daftar folder utama (*Root*) |
| `n` / `p` / `page <N>` | `next` / `prev` | Navigasi halaman daftar file di dalam folder |
| `r` | `refresh` | Memuat ulang isi file terbaru di folder ini |
| `h` | `help`, `?` | Menampilkan panduan perintah di dalam folder |
| `0` | `exit`, `quit`, `q` | Keluar dari aplikasi |

### 5. Fitur Spesial: Quick Upload Langsung dari Terminal

Kamu dapat langsung mengunggah satu atau banyak file saat pertama kali memanggil `main.py` melalui argumen baris perintah:

```bash
python main.py dokumen.pdf "foto liburan.jpg" ./folder_tugas/*.py
```

Aplikasi akan langsung menampilkan antrean file tersebut, menanyakan nama folder tujuan (tekan **Enter** untuk mengirim ke folder default `utama`), lalu mengunggahnya sebelum masuk ke dashboard utama.

## 🤖 Pemanfaatan Kecerdasan Artifisial (AI Usage Disclosure)

> 📖 **Catatan Lengkap:** Detail tahapan logbook mulai dari eksplorasi ide, *scaffolding*, proses *debugging*, hingga refleksi kode dapat dilihat secara lengkap pada berkas **[AI_LOGBOOK.md](./AI_LOGBOOK.md)**.

Dalam pengembangan **Awan CLI (GITUS)**, tim pengembang memanfaatkan Kecerdasan Artifisial sebagai asisten kolaboratif sesuai etika pengembangan perangkat lunak:

* **Alat AI yang Digunakan**: **Gemini 4 Hydrogen**
* **Contoh Perintah (*Prompt*) Utama**:
  1. *"Bagaimana merancang program Python lintas OS (Windows, Linux, Termux) yang memanfaatkan GitHub Releases dan Git Tags sebagai penyimpanan cloud pribadi?"*
  2. *"Pecah skrip menjadi struktur modular (`main.py`, `config.py`, `github_api.py`, `utils.py`) menggunakan pustaka Rich dengan tampilan tabel, spinner, pagination, dan fitur download biner."*
  3. *"Perbaiki perintah hapus agar mendukung `del <nama_folder>` maupun multi-delete sekaligus menghapus Git Tag-nya, serta tambahkan resolusi konflik nama file (Timpa, Rename, Cancel) saat batch upload."*
* **Ringkasan Validasi & Modifikasi Mandiri Tim Pengembang**:
  * Mengganti pendekatan argumen `argparse` yang rumit menjadi *setup* interaktif sekali jalan agar praktis di Termux Android, serta mengonversi spasi nama folder menjadi `-` sesuai aturan *Git Tag*.
  * Memastikan konfirmasi persetujuan `S&K.txt` tetap tampil setiap kali program dijalankan, menjaga layar tetap terbuka setelah proses selesai, dan memusatkan penyimpanan `.gh_cloud_config.json` serta folder `download/` di direktori skrip agar portabel.
  * Menambahkan *loop* pemulihan input (*fallback*) saat pengguna salah ketik nama file/folder, membersihkan awalan `& ` saat *drag & drop* di PowerShell Windows, serta menyempurnakan logika `del` dan resolusi konflik unggahan berdasarkan hasil pengujian langsung.

## ⚠️ Ketentuan & Batasan Penggunaan

1. **Batas Ukuran File**: Maksimal **2 GB per file** sesuai batasan resmi GitHub Releases.
2. **Privasi Data**: Sangat disarankan menggunakan repositori berstatus **Private** agar berkas pribadi tidak dapat diakses publik.
3. **Kebijakan Penggunaan Wajar**: Dilarang mengunggah *malware*, konten ilegal, materi yang melanggar hak cipta, atau menjadikan repositori sebagai CDN publik bertrafik tinggi yang berisiko menyebabkan pembatasan (*suspend*) akun GitHub.
4. **Keamanan Kredensial**: Token PAT dan file unduhan disimpan secara lokal pada perangkat pengguna (`.gh_cloud_config.json` dan folder `download/`). Jangan pernah membagikan atau mengunggah file `.gh_cloud_config.json` ke repositori publik.

## 👨‍💻 Identitas Pengembang

Karya ini dikembangkan dalam rangka kegiatan **Pelatihan TIK Bagi Murid SMA/SMK (LATIKA) Tahun 2026** — UPT. Teknologi Informasi dan Komunikasi Pendidikan (TIKP), Dinas Pendidikan Provinsi Jawa Timur.

* **Pengembang 1**: Zaidaan Ali Wirayudha
* **Pengembang 2**: Leon Agustian Rachmat
* **Kelas / Jurusan**: XI / INFORMATIKA & IPA
* **Asal Sekolah**: **SMA NEGERI 2 KOTA MADIUN**