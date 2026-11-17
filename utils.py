import glob
import os
import re
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich import box

console = Console()
SCRIPT_DIR = Path(__file__).resolve().parent
SK_FILE = SCRIPT_DIR / "S&K.txt"

DEFAULT_SK_CONTENT = """=============================================================================
            SYARAT & KETENTUAN PENGGUNAAN (S&K) - AWAN CLI STORAGE
             (GITUS - GitHub Release Storage Client Interface)
=============================================================================

[INFORMASI PENGEMBANG & PROYEK]
Nama Aplikasi       : Awan CLI Storage (GITUS)
Penulis / Perancang : Zaidaan Ali Wirayudha & Leon Pratama Agustian Rachmad
Asal Sekolah        : SMA NEGERI 2 KOTA MADIUN
Asisten Pengembangan: Gemini 4 Hydrogen
Tujuan Proyek       : Karya Proyek Pelatihan TIK Siswa SMA/SMK Tahun 2026
                      (UPT. TIKP Dinas Pendidikan Provinsi Jawa Timur)

-----------------------------------------------------------------------------
1. RUANG LINGKUP & SIFAT LAYANAN
-----------------------------------------------------------------------------
1.1. Awan CLI adalah antarmuka baris perintah (Command Line Interface) yang
     berfungsi sebagai jembatan (client) antara perangkat lokal pengguna
     dengan layanan GitHub REST API & GitHub Releases.
1.2. Aplikasi ini tidak menyediakan server penyimpanan mandiri; seluruh data
     disimpan langsung di dalam repository milik pengguna di platform GitHub.

-----------------------------------------------------------------------------
2. BATASAN TEKNIS & KEBIJAKAN GITHUB
-----------------------------------------------------------------------------
2.1. Ukuran File Tunggal: Batas maksimal ukuran untuk setiap file (asset)
     yang diunggah adalah 2 GB (2.147.483.648 bytes) sesuai ketentuan teknis
     resmi GitHub Releases. File melebihi batas ini akan otomatis ditolak.
2.2. Batas Permintaan API (Rate Limit): Pengguna wajib mematuhi batas kuota
     permintaan API GitHub (umumnya 5.000 permintaan per jam untuk akun
     terautentikasi).
2.3. Larangan Penyalahgunaan Bandwidth: Dilarang keras memanfaatkan tautan
     unduhan sebagai Content Delivery Network (CDN) publik dengan trafik
     tinggi karena dapat memicu pemblokiran akun atau repository oleh GitHub.

-----------------------------------------------------------------------------
3. PRIVASI & KEAMANAN KREDENSIAL
-----------------------------------------------------------------------------
3.1. Status Repository: Pengguna sangat diwajibkan menggunakan repository
     berstatus PRIVATE untuk menyimpan dokumen pribadi atau sensitif agar
     aset rilis tidak dapat diakses maupun diunduh oleh pihak luar.
3.2. Penyimpanan Lokal: Personal Access Token (PAT) GitHub dan konfigurasi
     akun disimpan secara lokal di file '.gh_cloud_config.json' pada
     direktori aplikasi di perangkat pengguna sendiri.
3.3. Tanggung Jawab Token: Pengembang tidak pernah mengirimkan, mencatat,
     atau mengumpulkan token pengguna ke pihak ketiga. Pengguna bertanggung
     jawab penuh menjaga kerahasiaan file konfigurasi lokal tersebut.
3.4. Hak Akses Token: Disarankan hanya memberikan izin (scope) 'repo' yang
     dibutuhkan saat membuat Personal Access Token di GitHub.

-----------------------------------------------------------------------------
4. ETIKA PENGGUNAAN & KONTEN YANG DILARANG
-----------------------------------------------------------------------------
4.1. Pengguna dilarang mengunggah perangkat lunak berbahaya (malware, virus,
     ransomware), skrip eksploitasi, atau file yang merusak sistem.
4.2. Dilarang mengunggah materi bajakan, konten ilegal, pornografi, atau
     dokumen yang melanggar Undang-Undang Hak Cipta dan regulasi hukum yang
     berlaku di Indonesia maupun Terms of Service GitHub.

-----------------------------------------------------------------------------
5. PENAFIAN (DISCLAIMER) & BATASAN TANGGUNG JAWAB
-----------------------------------------------------------------------------
5.1. Aplikasi ini disediakan "sebagaimana adanya" (AS IS) untuk tujuan
     edukasi dan produktivitas pribadi.
5.2. Pengembang (Zaidaan Ali Wirayudha & Leon Pratama Agustian Rachmad) dibebaskan
     dari segala tuntutan hukum atau kerugian akibat hilangnya data,
     gangguan koneksi internet, perubahan kebijakan API GitHub, maupun
     pembekuan akun (suspend) yang disebabkan oleh kelalaian pengguna dalam
     mematuhi S&K ini.

=============================================================================
Dengan melanjutkan penggunaan aplikasi ini, kamu menyatakan telah membaca,
memahami, dan menyetujui seluruh butir Syarat & Ketentuan di atas.
=============================================================================
"""


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause_dan_clear(pesan: str = "Tekan [bold white]Enter[/bold white] untuk melanjutkan..."):
    console.input(f"\n[dim]{pesan}[/dim]")
    clear_screen()


def pastikan_file_sk() -> str:
    if not SK_FILE.exists():
        SK_FILE.write_text(DEFAULT_SK_CONTENT, encoding="utf-8")
    return SK_FILE.read_text(encoding="utf-8").strip()


def _format_sk_responsif(raw_text: str) -> str:
    """
    Membersihkan garis ASCII statis (==== / ----) dan hard-wrap manual
    dari file S&K.txt agar teks mengalir responsif di layar HP maupun PC.
    """
    baris_bersih = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        # Buang garis pembatas statis
        if stripped and set(stripped) <= {"=", "-"}:
            continue
        # Hilangkan judul header atas karena sudah ditampilkan di title Panel
        if stripped.startswith("SYARAT & KETENTUAN") or stripped.startswith("(GITUS -"):
            continue
        baris_bersih.append(line.rstrip())

    # Gabungkan baris yang terpotong hard-wrap menjadi paragraf utuh
    paragraf = []
    buffer = ""

    for line in baris_bersih:
        stripped = line.strip()
        if not stripped:
            if buffer:
                paragraf.append(buffer)
                buffer = ""
            paragraf.append("")
            continue

        # Deteksi awal blok baru: [HEADER], pasal angka (1., 1.1.), atau metadata (Key : Value)
        is_section = stripped.startswith("[") and stripped.endswith("]")
        is_numbered = bool(re.match(r"^\d+(\.\d+)*\.", stripped))
        is_meta_key = ":" in line and not line.startswith(" ")

        if is_section:
            if buffer:
                paragraf.append(buffer)
                buffer = ""
            paragraf.append(f"\n[bold cyan]{stripped}[/bold cyan]")
        elif is_numbered:
            if buffer:
                paragraf.append(buffer)
            # Highlight nomor pasal (misal 1.1.) dan judul tebal sebelum titik dua
            formatted = re.sub(r"^(\d+\.\d+\.)\s*([^:]+:)?", lambda m: f"[bold yellow]{m.group(1)}[/bold yellow] " + (f"[bold white]{m.group(2)}[/bold white]" if m.group(2) else ""), stripped)
            buffer = formatted
        elif is_meta_key:
            if buffer:
                paragraf.append(buffer)
            k, v = stripped.split(":", 1)
            buffer = f"[bold]{k.strip()}[/bold]: {v.strip()}"
        else:
            # Lanjutan baris sebelumnya -> gabung dengan spasi tunggal
            if buffer:
                buffer += " " + stripped
            else:
                buffer = stripped

    if buffer:
        paragraf.append(buffer)

    hasil = "\n".join(paragraf)
    # Rapikan spasi kosong berlebih
    hasil = re.sub(r"\n{3,}", "\n\n", hasil).strip()
    return hasil


def tampilkan_dan_konfirmasi_sk() -> bool:
    clear_screen()
    isi_mentah = pastikan_file_sk()
    isi_responsif = _format_sk_responsif(isi_mentah)

    # Padding menyesuaikan lebar layar (lebih hemat di HP/Termux)
    lebar_layar = console.width
    pad = (0, 1) if lebar_layar < 65 else (1, 2)

    console.print(
        Panel(
            isi_responsif,
            title="[bold white]SYARAT & KETENTUAN (S&K)[/bold white]",
            subtitle=f"[dim]{SK_FILE.name}[/dim]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=pad,
        )
    )

    while True:
        jawab = console.input("[bold yellow]Apakah kamu setuju dengan S&K di atas? (y/n): [/bold yellow]").strip().lower()
        if jawab in ("y", "ya", "setuju"):
            return True
        if jawab in ("n", "no", "tidak"):
            console.print("[bold red]Program dibatalkan karena S&K tidak disetujui.[/bold red]")
            sys.exit(0)
        console.print("[red]Input tidak valid. Ketik 'y' untuk setuju atau 'n' untuk batal.[/red]")


def tampilkan_panduan_help(di_dalam_folder: bool = False):
    table = Table(
        title="[bold cyan]PANDUAN PERINTAH AWAN CLI[/bold cyan]",
        box=box.ROUNDED,
        header_style="bold yellow",
        expand=True,
    )
    table.add_column("Perintah", style="bold white", width=28)
    table.add_column("Fungsi & Contoh Penggunaan", style="dim white")

    if not di_dalam_folder:
        table.add_row("<nama_folder>", "Masuk langsung ke folder (contoh: [cyan]utama[/cyan] atau [cyan]open utama[/cyan])")
        table.add_row("up / upload", "Upload 1 atau banyak file (mendukung Timpa / Rename / Cancel jika sama)")
        table.add_row("dl <folder/file>", "Unduh file langsung (contoh: [cyan]dl utama/data.zip[/cyan])")
        table.add_row("del <target1, target2>", "Hapus massal folder atau folder/file (contoh: [cyan]del GITUS, utama/a.txt[/cyan])")
    else:
        table.add_row("up / upload", "Upload 1 atau banyak file langsung ke folder aktif ini")
        table.add_row("dl <nama_file>", "Unduh file dari folder ini (contoh: [cyan]dl data.zip[/cyan])")
        table.add_row("del <file1, file2>", "Hapus massal file di folder ini (contoh: [cyan]del a.txt b.jpg, c.pdf[/cyan])")
        table.add_row(".. / back", "Kembali ke daftar folder utama")

    table.add_row("n / p / page <angka>", "Navigasi halaman (Next, Prev, atau lompat ke halaman N)")
    table.add_row("r / refresh", "Muat ulang data terbaru dari GitHub")
    table.add_row("reset", "Ubah pengaturan OS, Token, atau Repository")
    table.add_row("h / help", "Tampilkan panduan perintah ini")
    table.add_row("0 / exit", "Keluar dari aplikasi")

    console.print(table)
    console.print(
        "[dim]Tips: Pada perintah [bold]del[/bold], pisahkan beberapa target dengan spasi atau koma "
        "(gunakan tanda kutip jika nama mengandung spasi).[/dim]"
    )


def get_default_download_dir(os_type: str = "") -> Path:
    dl_dir = SCRIPT_DIR / "download"
    dl_dir.mkdir(parents=True, exist_ok=True)
    return dl_dir


def bersihkan_path(raw_path: str, os_type: str) -> Path:
    clean = raw_path.strip()
    if os_type == "windows" and clean.startswith("& "):
        clean = clean[2:].strip()
    clean = clean.strip('"').strip("'")
    return Path(clean).expanduser().resolve()


def pecah_argumen_multi(raw_arg: str) -> list[str]:
    """
    Memecah input menjadi daftar target dengan pemisah spasi atau koma,
    tetap menjaga teks di dalam tanda kutip tetap utuh.
    """
    if not raw_arg or not raw_arg.strip():
        return []
    matches = re.findall(r'"([^"]+)"|\'([^\']+)\'|([^\s,]+)', raw_arg.strip())
    hasil = []
    seen = set()
    for m in matches:
        item = (m[0] or m[1] or m[2]).strip()
        if item and item.lower() not in seen:
            seen.add(item.lower())
            hasil.append(item)
    return hasil


def ekstrak_daftar_file(raw_input: str, os_type: str) -> tuple[list[Path], list[str]]:
    clean = raw_input.strip()
    if not clean:
        return [], []

    if os_type == "windows" and clean.startswith("& "):
        clean = clean[2:].strip()

    tokens = []
    single_unquoted = clean.strip('"').strip("'")
    if "*" not in single_unquoted and "?" not in single_unquoted:
        candidate = Path(single_unquoted).expanduser()
        if candidate.exists():
            tokens = [single_unquoted]

    if not tokens:
        matches = re.findall(r'"([^"]+)"|\'([^\']+)\'|([^\s,]+)', clean)
        tokens = [m[0] or m[1] or m[2] for m in matches if (m[0] or m[1] or m[2])]

    valid_files: list[Path] = []
    invalid_items: list[str] = []
    seen = set()

    for token in tokens:
        token_clean = token.strip().strip('"').strip("'")
        if not token_clean:
            continue

        expanded_str = os.path.expanduser(token_clean)

        if "*" in expanded_str or "?" in expanded_str:
            matched_paths = sorted(glob.glob(expanded_str))
            if not matched_paths:
                invalid_items.append(token_clean)
                continue
            for mp in matched_paths:
                p = Path(mp).resolve()
                if p.is_file() and p not in seen:
                    seen.add(p)
                    valid_files.append(p)
            continue

        p = Path(expanded_str).resolve()
        if p.is_file():
            if p not in seen:
                seen.add(p)
                valid_files.append(p)
        elif p.is_dir():
            dir_files = sorted([item for item in p.iterdir() if item.is_file()])
            if not dir_files:
                invalid_items.append(f"{token_clean} (folder kosong)")
            for df in dir_files:
                if df not in seen:
                    seen.add(df)
                    valid_files.append(df)
        else:
            invalid_items.append(token_clean)

    return valid_files, invalid_items


def parse_target_folder_file(arg: str):
    clean = arg.strip().strip('"').strip("'")
    if "/" not in clean and "\\" in clean:
        clean = clean.replace("\\", "/", 1)
    if "/" not in clean:
        return None
    folder_part, file_part = clean.split("/", 1)
    folder_part = folder_part.strip().strip('"').strip("'")
    file_part = file_part.strip().strip('"').strip("'")
    if not folder_part or not file_part:
        return None
    return folder_part, file_part


def format_ukuran(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"
