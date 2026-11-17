# 📓 AI Logbook — Awan CLI (GITUS)

Dokumentasi ini mencatat seluruh riwayat interaksi pemanfaatan kecerdasan artifisial (AI) dalam perancangan, penyusunan kerangka kode (*scaffolding*), pengujian dan perbaikan galat (*debugging*), serta refleksi pemahaman kode pada pengembangan aplikasi **Awan CLI (GITUS) — GitHub Release Cloud Storage**.

> 📖 **Dokumentasi Utama:** Kembali ke panduan instalasi, konfigurasi GitHub, dan daftar perintah lengkap pada **[README.md](./README.md)**.

* **Nama Produk Digital:** Awan CLI (GITUS) — GitHub Release Cloud Storage
* **Penulis / Perancang:** Zaidaan Ali Wirayudha & Leon Agustian Rachmat
* **Asal Sekolah:** SMA NEGERI 2 KOTA MADIUN
* **Kegiatan:** Pelatihan TIK Bagi Murid SMA/SMK (LATIKA) Tahun 2026 — UPT. TIKP Dinas Pendidikan Provinsi Jawa Timur
* **Asisten Pengembangan AI:** Gemini 4 Hydrogen

---

## Tahap 1: Eksplorasi Ide & Perancangan Solusi

* **Interaksi AI (Prompt):**
  > *"Bagaimana merancang program Python lintas sistem operasi (Windows, Linux, dan Termux Android) yang memanfaatkan fitur GitHub Releases dan Git Tags sebagai penyimpanan cloud pribadi hingga 2 GB per file?"*
* **Saran AI:**
  AI menyarankan pemanfaatan endpoint GitHub REST API (`/releases` dan `uploads.github.com`) dengan memetakan setiap objek *Release* dan *Git Tag* sebagai folder virtual, serta mengusulkan struktur CLI berbasis pustaka `argparse` dengan sub-perintah `setup` terpisah yang mengharuskan pengguna mengetik parameter `--token`, `--owner`, dan `--repo` setiap kali mengatur konfigurasi.
* **Validasi & Modifikasi Mandiri:**
  Setelah mengevaluasi alur penggunaan awal pada perangkat *mobile* (Termux Android), pendekatan argumen `argparse` dinilai terlalu panjang dan rawan salah ketik. Tim pengembang memodifikasi alur autentikasi agar program otomatis mendeteksi keberadaan berkas `.gh_cloud_config.json` saat dijalankan, meminta kredensial secara interaktif sekali saja dengan panduan pembuatan *Personal Access Token* (PAT), serta menambahkan fungsi `format_tag()` untuk mengonversi spasi pada nama folder menjadi tanda hubung (`-`) agar selalu valid sesuai aturan *tag* GitHub.

---

## Tahap 2: Penyusunan Kerangka Kode (Scaffolding)

* **Interaksi AI (Prompt):**
  > *"Pecah skrip tunggal menjadi struktur modular (`main.py`, `config.py`, `github_api.py`, `utils.py`) agar mudah dipelihara, tambahkan tampilan Syarat & Ketentuan (S&K), deteksi OS, serta rombak antarmuka terminal menjadi modern menggunakan pustaka Rich lengkap dengan fitur unduh file."*
* **Saran AI:**
  AI menyusun arsitektur 4 modul utama:
  1. `config.py` untuk penyimpanan konfigurasi JSON.
  2. `github_api.py` untuk kelas klien `GitHubCloudClient` yang menangani komunikasi API dan unduhan biner secara *streaming* (`Accept: application/octet-stream`).
  3. `utils.py` untuk fungsi bantuan tampilan terminal, pembersihan layar (*auto-clear*), dan tampilan S&K.
  4. `main.py` untuk alur menu utama menggunakan komponen `Panel`, `Table`, dan `Spinner` dari `rich`.
* **Validasi & Modifikasi Mandiri:**
  Kami menguji kerangka awal dan menemukan bahwa jendela terminal langsung tertutup (*exit*) sesaat setelah proses unggah selesai sehingga hasil URL tidak sempat terbaca. Tim menambahkan jeda interaktif (`pause_dan_clear`) sebelum layar dibersihkan, memusatkan penyimpanan `.gh_cloud_config.json` dan direktori hasil unduhan (`download/`) langsung di dalam direktori skrip (`Path(__file__).resolve().parent`) agar bersifat portabel lintas perangkat, serta memastikan konfirmasi persetujuan S&K (`y/n`) selalu muncul di awal program demi kepatuhan batas 2 GB per file.

---

## Tahap 3: Pemecahan Masalah & Penanganan Galat (Debugging)

### Iterasi 3A — Perbaikan Navigasi Direktori, Paginasi, & Pemulihan Input Salah Ketik

* **Interaksi AI (Prompt):**
  > *"Perbaiki navigasi agar langsung menampilkan daftar folder dengan pagination, masuk ke folder menggunakan nama asli tanpa nomor urut, dan jangan langsung keluar ke menu utama ketika pengguna salah mengetik nama file saat unduh atau hapus."*
* **Saran AI:**
  AI menerapkan pembagian halaman (`PAGE_SIZE = 8`), menyembunyikan tabel bantuan panjang dari layar utama (dipindahkan ke perintah `h` / `help`), serta membuat fungsi pencocokan nama toleran (`cocokkan_file_by_nama`).
* **Validasi & Modifikasi Mandiri:**
  Saat menguji skenario salah ketik (*typo*) pada perintah `dl` maupun `del`, kami memvalidasi perilaku program dan menambahkan perulangan pemulihan kesalahan (*input fallback loop*) agar pengguna dapat langsung memperbaiki nama target tanpa harus mengulang perintah dari awal. Kami juga menghapus kolom nomor urut pada tabel folder maupun file sehingga navigasi terasa alami seperti direktori lokal, serta mendukung pintasan langsung seperti `dl folder/file`.

### Iterasi 3B — Penanganan Bug Path PowerShell & Multi-File Batch Upload

* **Interaksi AI (Prompt):**
  > *"Tambahkan fitur multi-file upload yang mendukung drag & drop banyak file sekaligus, wildcard (`*.pdf`, `*.jpg`), dan path folder lokal dengan progress bar Rich."*
* **Saran AI:**
  AI membuat fungsi `ekstrak_daftar_file` menggunakan ekspresi reguler (*regex*) dan modul `glob`, serta menampilkan antrean unggahan dengan komponen `rich.progress`.
* **Validasi & Modifikasi Mandiri:**
  Pada pengujian di Windows PowerShell, fitur *drag & drop* file ke terminal menghasilkan awalan karakter `& ` dan tanda kutip yang menyebabkan *path* dianggap tidak valid (`FileNotFoundError`). Kami menambahkan logika pembersihan khusus pada `bersihkan_path()` dan `ekstrak_daftar_file()` untuk memangkas awalan `& ` secara otomatis, serta menambahkan mode antrean interaktif (`+` untuk menambah file sebelum unggah) dan *quick upload* langsung dari argumen CLI (`python main.py file1 file2`).

### Iterasi 3C — Perbaikan Galat `del <nama_folder>`, Pembersihan Git Tag, & Resolusi Konflik Upload

* **Interaksi AI (Prompt):**
  > *"Pisahkan teks S&K ke file `S&K.txt` eksternal, perbaiki galat saat menghapus folder langsung di menu utama (`del GITUS`), dukung multi-delete, serta tangani kasus ketika nama file yang diunggah sudah ada di folder tujuan."*
* **Saran AI:**
  AI memisahkan teks ketentuan ke berkas `S&K.txt` (dengan pembuatan otomatis apabila berkas hilang), menambahkan metode `delete_folder` pada `github_api.py`, membuat pemecah argumen multi-target (`pecah_argumen_multi`), serta menyusun fungsi `selesaikan_konflik_upload`.
* **Validasi & Modifikasi Mandiri:**
  Berdasarkan hasil pengujian langsung pada CLI utama, ditemukan dua masalah kritis:
  1. Perintah `del <nama_folder>` gagal karena *parser* sebelumnya hanya mengenali format `folder/file`, serta penghapusan *Release* di GitHub masih menyisakan *Git Tag* kosong. Kami memperbarui `alur_hapus_di_root()` agar mampu membedakan target folder maupun file secara bersamaan dalam satu perintah massal, serta memastikan `delete_folder()` turut menghapus referensi `/git/refs/tags/{tag_name}`.
  2. Pada pengujian unggah file bernama sama, kami memvalidasi alur `selesaikan_konflik_upload()` agar pengguna memiliki kendali penuh untuk memilih **Timpa (`t`)**, **Rename (`r`)** dengan mempertahankan ekstensi asli file secara otomatis, atau **Cancel (`c`)** tanpa menghentikan sisa antrean.

---

## Tahap 4: Refleksi & Penjelasan Kode

* **Pemahaman & Penjelasan Arsitektur Kode:**
  Melalui proses perancangan bertahap, pengujian galat (*debugging*), dan validasi mandiri bersama AI, tim pengembang memahami secara menyeluruh mekanisme kerja aplikasi **Awan CLI (GITUS)**:
  * **Pemisahan Tanggung Jawab Modular**: `config.py` menjaga persistensi kredensial lokal; `github_api.py` mengisolasi seluruh komunikasi HTTP ke REST API GitHub (termasuk *streaming* potongan *chunk* 64 KB saat mengunduh file besar agar hemat memori pada perangkat Android/Termux); `utils.py` menangani sanitasi *path* lintas OS dan ekspansi *wildcard*; sedangkan `main.py` mengatur state navigasi dua tingkat (*Root Directory* dan *Sub-folder View*).
  * **Manajemen Siklus Hidup Objek GitHub**: Setiap folder dipetakan ke pasangan *GitHub Release* dan *Git Tag*, sedangkan setiap berkas disimpan sebagai *Release Asset* berkapasitas hingga 2 GB.
* **Validasi & Modifikasi Mandiri:**
  Seluruh kode sumber (`main.py`, `github_api.py`, `config.py`, `utils.py`), dokumen ketentuan (`S&K.txt`), serta dokumentasi proyek ([README.md](./README.md) dan [AI_LOGBOOK.md](./AI_LOGBOOK.md)) telah diuji secara menyeluruh pada lingkungan terminal lintas sistem operasi dan diverifikasi keandalannya oleh tim pengembang sebelum dipublikasikan ke repositori.