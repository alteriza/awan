import glob
import os
import re
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()
SCRIPT_DIR = Path(__file__).resolve().parent
SK_FILE = SCRIPT_DIR / "S&K.txt"

DEFAULT_SK_CONTENT = """=================================================================
         SYARAT & KETENTUAN (S&K) - AWAN CLI STORAGE
=================================================================

[INFORMASI PENGEMBANG]
Penulis / Perancang : Zaidaan Ali Wirayudha & Leon Pratama Agustian Rachmad
Asal Sekolah        : SMA NEGERI 2 KOTA MADIUN
Asisten Pengembangan: Gemini 4 Hydrogen

[KETENTUAN PENGGUNAAN]
1. Batas maksimal ukuran per file adalah 2 GB sesuai kebijakan
   resmi GitHub Releases.
2. Gunakan repository berstatus PRIVATE untuk menyimpan data
   pribadi agar tidak dapat diakses oleh publik.
3. Dilarang mengunggah malware, file ilegal, konten berbahaya,
   atau materi yang melanggar hak cipta.
4. Hindari penggunaan sebagai CDN publik bertrafik tinggi agar
   akun GitHub tidak terkena pembatasan (suspend).
5. Kredensial token dan hasil unduhan disimpan secara lokal di
   direktori aplikasi pada perangkat kamu sendiri.

Dengan melanjutkan, kamu menyatakan telah membaca dan menyetujui
seluruh ketentuan di atas.
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


def tampilkan_dan_konfirmasi_sk() -> bool:
    clear_screen()
    isi_sk = pastikan_file_sk()
    console.print(
        Panel(
            f"[white]{isi_sk}[/white]",
            title="[bold white]SYARAT & KETENTUAN (S&K.txt)[/bold white]",
            subtitle=f"[dim]{SK_FILE.name}[/dim]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
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