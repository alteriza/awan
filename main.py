import math
import sys
from pathlib import Path
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich import box

from config import muat_config, simpan_config, CONFIG_FILE
from github_api import GitHubCloudClient
from utils import (
    console,
    clear_screen,
    pause_dan_clear,
    tampilkan_dan_konfirmasi_sk,
    tampilkan_panduan_help,
    get_default_download_dir,
    bersihkan_path,
    pecah_argumen_multi,
    ekstrak_daftar_file,
    parse_target_folder_file,
    format_ukuran,
)

PAGE_SIZE = 8
MAX_GITHUB_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB


def pilih_os() -> str:
    console.print("\n[bold cyan]Pilih Sistem Operasi:[/bold cyan]")
    console.print("  [bold]1.[/bold] Windows")
    console.print("  [bold]2.[/bold] Linux")
    console.print("  [bold]3.[/bold] Termux (Android)")

    mapping = {"1": "windows", "2": "linux", "3": "termux"}
    while True:
        pilihan = console.input("[bold yellow]Pilihan (1/2/3): [/bold yellow]").strip().lower()
        if pilihan in mapping:
            return mapping[pilihan]
        if pilihan in mapping.values():
            return pilihan
        console.print("[red]Pilihan tidak valid. Ketik 1, 2, atau 3.[/red]")


def setup_awal() -> dict:
    clear_screen()
    console.print(
        Panel(
            "Masukkan detail akun GitHub. Data disimpan lokal dan hanya diminta sekali.",
            title="[bold cyan]SETUP KONFIGURASI AWAL[/bold cyan]",
            box=box.ROUNDED,
        )
    )
    os_type = pilih_os()
    while True:
        token = console.input("[bold]GitHub Token (ghp_...): [/bold]").strip()
        owner = console.input("[bold]Username GitHub: [/bold]").strip()
        repo = console.input("[bold]Nama Repository: [/bold]").strip()
        if token and owner and repo:
            break
        console.print("[red]Token, Username, dan Nama Repository tidak boleh kosong.[/red]\n")

    cfg = simpan_config(os_type, token, owner, repo)
    clear_screen()
    console.print(f"[bold green]✔ Konfigurasi tersimpan di {CONFIG_FILE}[/bold green]\n")
    tampilkan_panduan_help(di_dalam_folder=False)
    pause_dan_clear("Tekan [bold white]Enter[/bold white] untuk masuk ke dashboard...")
    return cfg


def render_header(cfg: dict, current_folder: str = None):
    default_dl = get_default_download_dir(cfg["os"])
    lokasi = f"/{current_folder}" if current_folder else "/ (Root)"
    header_info = (
        f"[bold cyan]Repository  :[/bold cyan] [white]{cfg['owner']}/{cfg['repo']}[/white]\n"
        f"[bold cyan]Lokasi Aktif:[/bold cyan] [bold yellow]{lokasi}[/bold yellow]\n"
        f"[bold cyan]Platform    :[/bold cyan] [green]{cfg['os'].upper()}[/green]  •  "
        f"[bold cyan]Unduh:[/bold cyan] [dim]{default_dl}[/dim]"
    )
    console.print(
        Panel(
            header_info,
            title="[bold white]☁  AWAN CLI — GITHUB RELEASE STORAGE[/bold white]",
            border_style="bright_blue",
            box=box.ROUNDED,
        )
    )


def render_folder_table(folders: list, page: int, page_size: int = PAGE_SIZE):
    total = len(folders)
    if total == 0:
        console.print(
            Panel(
                "[yellow]Belum ada folder di repository ini.[/yellow]\n"
                "[dim]Ketik [bold white]up[/bold white] untuk mulai mengunggah file pertama.[/dim]",
                title="[bold cyan]DAFTAR FOLDER[/bold cyan]",
                border_style="dim",
                box=box.ROUNDED,
            )
        )
        return

    total_pages = max(1, math.ceil(total / page_size))
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    subset = folders[start_idx:end_idx]

    caption = f"Halaman {page}/{total_pages} • Total: {total} folder"
    if total_pages > 1:
        caption += "  |  [n] Next  [p] Prev  [page N] Lompat"

    table = Table(
        title="[bold cyan]DAFTAR FOLDER PENYIMPANAN[/bold cyan]",
        caption=caption,
        box=box.ROUNDED,
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("Nama Folder", style="bold white")
    table.add_column("Isi", style="green", width=12, justify="center")
    table.add_column("Update", style="dim cyan", width=14, justify="center")

    for item in subset:
        table.add_row(
            f"📁 {item['folder']}",
            f"{item['jumlah_file']} file",
            item["tanggal"],
        )

    console.print(table)


def tampilkan_tabel_file(folder: str, files: list, page: int = 1, page_size: int = PAGE_SIZE):
    total = len(files)
    if total == 0:
        console.print(
            Panel(
                f"[yellow]Folder '{folder}' masih kosong.[/yellow]\n"
                "[dim]Ketik [bold white]up[/bold white] untuk mengunggah file ke folder ini, atau [bold white]..[/bold white] untuk kembali.[/dim]",
                title=f"[bold cyan]ISI FOLDER: {folder}[/bold cyan]",
                border_style="dim",
                box=box.ROUNDED,
            )
        )
        return

    total_pages = max(1, math.ceil(total / page_size))
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    subset = files[start_idx:end_idx]

    caption = f"Halaman {page}/{total_pages} • Total: {total} file"
    if total_pages > 1:
        caption += "  |  [n] Next  [p] Prev  [page N] Lompat"

    table = Table(
        title=f"[bold cyan]ISI FOLDER: {folder}[/bold cyan]",
        caption=caption,
        box=box.ROUNDED,
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("Nama File", style="bold white")
    table.add_column("Ukuran", style="green", width=14, justify="right")

    for item in subset:
        table.add_row(f"📄 {item['nama']}", format_ukuran(item["ukuran"]))

    console.print(table)


def tampilkan_antrean_upload(queue_files: list[Path]):
    total_size = sum(f.stat().st_size for f in queue_files)
    table = Table(
        title=f"[bold cyan]ANTREAN UPLOAD ({len(queue_files)} File • Total: {format_ukuran(total_size)})[/bold cyan]",
        box=box.ROUNDED,
        header_style="bold yellow",
        expand=True,
    )
    table.add_column("Nama File", style="bold white")
    table.add_column("Ukuran", style="green", width=14, justify="right")

    for f in queue_files:
        size = f.stat().st_size
        size_str = format_ukuran(size)
        if size > MAX_GITHUB_FILE_SIZE:
            size_str = f"[red]{size_str} (>2GB!)[/red]"
        table.add_row(f"📄 {f.name}", size_str)

    console.print(table)


def resolve_folder_name(raw_folder: str, folders_cache: list) -> str:
    clean = raw_folder.strip()
    ci_match = next((f["folder"] for f in folders_cache if f["folder"].lower() == clean.lower()), None)
    if ci_match:
        return ci_match
    return clean.replace(" ", "-")


def cari_folder_objek(raw_folder: str, folders_cache: list) -> dict | None:
    clean = raw_folder.strip()
    formatted = clean.replace(" ", "-").lower()
    return next(
        (f for f in folders_cache if f["folder"].lower() in (clean.lower(), formatted)),
        None,
    )


def cocokkan_file_by_nama(files: list, query: str) -> tuple[dict | None, str | None]:
    q = query.strip()
    if not q:
        return None, None

    exact = next((f for f in files if f["nama"] == q), None)
    if exact:
        return exact, None

    ci_exact = next((f for f in files if f["nama"].lower() == q.lower()), None)
    if ci_exact:
        return ci_exact, None

    partial_matches = [f for f in files if q.lower() in f["nama"].lower()]
    if len(partial_matches) == 1:
        return partial_matches[0], None
    if len(partial_matches) > 1:
        daftar_mirip = ", ".join(m["nama"] for m in partial_matches[:5])
        return None, f"Ditemukan beberapa file mirip untuk '{q}' ({daftar_mirip}). Ketik nama lebih lengkap."

    return None, f"File '{q}' tidak ditemukan."


def selesaikan_konflik_upload(
    queue_files: list[Path],
    existing_assets: list[dict],
    tag_resmi: str,
) -> tuple[list[tuple[Path, str, dict | None]], list[str]]:
    """
    Memeriksa nama file yang sudah ada di folder GitHub.
    Jika ada yang sama, menanyakan pilihan: Timpa, Rename, atau Cancel.
    """
    existing_map = {a["nama"].lower(): a for a in existing_assets}
    reserved_names = set(existing_map.keys())

    # Rencana upload: (file_path, nama_tujuan, aset_lama_untuk_ditimpa_atau_None)
    upload_plan: list[tuple[Path, str, dict | None]] = []
    dibatalkan: list[str] = []

    for file_path in queue_files:
        orig_name = file_path.name
        orig_lower = orig_name.lower()

        if orig_lower not in reserved_names:
            reserved_names.add(orig_lower)
            upload_plan.append((file_path, orig_name, None))
            continue

        # Terdeteksi duplikat!
        aset_lama = existing_map.get(orig_lower)
        ukuran_lama = format_ukuran(aset_lama["ukuran"]) if aset_lama else "Antrean saat ini"
        ukuran_baru = format_ukuran(file_path.stat().st_size)

        console.print(
            Panel(
                f"File [bold yellow]{orig_name}[/bold yellow] sudah ada di folder [bold cyan]{tag_resmi}[/bold cyan]!\n"
                f"• Ukuran file lama : [dim]{ukuran_lama}[/dim]\n"
                f"• Ukuran file baru : [green]{ukuran_baru}[/green]\n\n"
                f"Pilih tindakan:\n"
                f"  [bold cyan][t] Timpa[/bold cyan]  — Ganti file lama dengan file baru ini\n"
                f"  [bold yellow][r] Rename[/bold yellow] — Simpan dengan nama baru\n"
                f"  [bold red][c] Cancel[/bold red] — Batalkan upload file ini",
                title="[bold yellow]⚠ NAMA FILE SUDAH ADA[/bold yellow]",
                border_style="yellow",
                box=box.ROUNDED,
            )
        )

        while True:
            aksi = console.input("[bold]Pilihan (timpa / rename / cancel): [/bold]").strip().lower()

            if aksi in ("t", "timpa", "overwrite", "1"):
                if aset_lama:
                    upload_plan.append((file_path, orig_name, aset_lama))
                    break
                else:
                    console.print("[red]File bentrok dengan sesama antrean baru, silakan pilih 'rename' atau 'cancel'.[/red]")

            elif aksi in ("r", "rename", "2"):
                ekstensi_asli = file_path.suffix
                while True:
                    nama_baru = console.input(f"Masukkan nama baru [dim](ekstensi asli: {ekstensi_asli or 'tanpa ekstensi'})[/dim]: ").strip()
                    if not nama_baru:
                        console.print("[red]Nama file baru tidak boleh kosong.[/red]")
                        continue
                    # Pertahankan ekstensi asli jika user tidak menuliskannya
                    if ekstensi_asli and not Path(nama_baru).suffix:
                        nama_baru = f"{nama_baru}{ekstensi_asli}"
                    if "/" in nama_baru or "\\" in nama_baru:
                        console.print("[red]Nama file tidak boleh mengandung karakter '/' atau '\\'.[/red]")
                        continue
                    if nama_baru.lower() in reserved_names:
                        console.print(f"[red]Nama '{nama_baru}' juga sudah dipakai di folder '{tag_resmi}'. Gunakan nama lain.[/red]")
                        continue

                    reserved_names.add(nama_baru.lower())
                    upload_plan.append((file_path, nama_baru, None))
                    break
                break

            elif aksi in ("c", "cancel", "batal", "3"):
                dibatalkan.append(orig_name)
                break

            else:
                console.print("[red]Pilihan tidak valid. Ketik 'timpa' (t), 'rename' (r), atau 'cancel' (c).[/red]")

    return upload_plan, dibatalkan


def eksekusi_batch_upload(client: GitHubCloudClient, queue_files: list[Path], folder_tujuan: str) -> bool:
    try:
        with console.status(f"[cyan]Menyiapkan folder '{folder_tujuan}' di GitHub...[/cyan]"):
            release_id, tag_resmi = client.get_or_create_folder(folder_tujuan)
            existing_assets = client.list_files_by_release_id(release_id)
    except Exception as e:
        console.print(Panel(f"[bold red]✘ Gagal mengakses folder GitHub:[/bold red] {e}", border_style="red"))
        return False

    # Cek duplikat sebelum memulai progress bar
    upload_plan, dibatalkan = selesaikan_konflik_upload(queue_files, existing_assets, tag_resmi)

    hasil_upload = [(nama, "[bold yellow]⚠ Dibatalkan[/bold yellow]", "Upload dibatalkan oleh pengguna") for nama in dibatalkan]
    sukses_count = 0

    if upload_plan:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}[/bold cyan]"),
            BarColumn(bar_width=28),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Mengunggah...", total=len(upload_plan))

            for idx, (file_path, final_name, aset_lama) in enumerate(upload_plan, 1):
                progress.update(task, description=f"[{idx}/{len(upload_plan)}] {final_name}")

                if file_path.stat().st_size > MAX_GITHUB_FILE_SIZE:
                    hasil_upload.append((final_name, "[bold red]✘ Gagal[/bold red]", "Ukuran melebihi batas 2 GB"))
                    progress.advance(task)
                    continue

                try:
                    if aset_lama:
                        client.delete_file(aset_lama["id"])

                    url = client.upload_file(
                        file_path,
                        tag_resmi,
                        release_id=release_id,
                        custom_name=final_name,
                    )
                    sukses_count += 1

                    if aset_lama:
                        status_label = "[bold green]✔ Ditimpa[/bold green]"
                    elif final_name != file_path.name:
                        status_label = "[bold green]✔ Renamed[/bold green]"
                    else:
                        status_label = "[bold green]✔ Sukses[/bold green]"

                    hasil_upload.append((final_name, status_label, url))
                except Exception as e:
                    hasil_upload.append((final_name, "[bold red]✘ Gagal[/bold red]", str(e)))

                progress.advance(task)

    res_table = Table(
        title=f"[bold cyan]HASIL UPLOAD KE FOLDER: {tag_resmi} ({sukses_count}/{len(queue_files)} Berhasil)[/bold cyan]",
        box=box.ROUNDED,
        header_style="bold magenta",
        expand=True,
    )
    res_table.add_column("Nama File", style="bold white", width=26)
    res_table.add_column("Status", width=15, justify="center")
    res_table.add_column("Keterangan / URL", style="dim cyan")

    for nama, status, info in hasil_upload:
        res_table.add_row(nama, status, info)

    console.print()
    console.print(res_table)
    return sukses_count > 0


def alur_upload_interaktif(
    client: GitHubCloudClient,
    os_type: str,
    folders_cache: list,
    arg: str = "",
    fixed_folder: str = None,
) -> bool:
    queue_files: list[Path] = []
    seen_paths = set()

    def tambah_ke_antrean(raw_text: str):
        valid, invalid = ekstrak_daftar_file(raw_text, os_type)
        for v in valid:
            if v not in seen_paths:
                seen_paths.add(v)
                queue_files.append(v)
        if invalid:
            console.print(f"[yellow]⚠ Tidak ditemukan / diabaikan: {', '.join(invalid)}[/yellow]")

    if arg:
        tambah_ke_antrean(arg)

    while True:
        if not queue_files:
            console.print("[dim]Bisa drag & drop banyak file, pakai wildcard (*.jpg), atau masukkan path folder lokal.[/dim]")
            raw_inp = console.input("Lokasi file [dim]('batal' = keluar)[/dim]: ").strip()
            if raw_inp.lower() in ("batal", "cancel", "0"):
                return False
            tambah_ke_antrean(raw_inp)
            continue

        clear_screen()
        target_label = f" (Folder: {fixed_folder})" if fixed_folder else ""
        console.print(f"[bold cyan]=== MULTI-FILE UPLOAD{target_label} ===[/bold cyan]")
        tampilkan_antrean_upload(queue_files)
        opsi = console.input(
            "\nTekan [bold green]Enter[/bold green] untuk lanjut, ketik [bold yellow]+[/bold yellow] tambah file, atau [bold red]batal[/bold red]: "
        ).strip()

        if opsi.lower() in ("batal", "cancel", "0"):
            return False
        if opsi == "+":
            extra = console.input("Masukkan tambahan file/folder/wildcard: ").strip()
            if extra:
                tambah_ke_antrean(extra)
            continue
        if opsi == "":
            break
        tambah_ke_antrean(opsi)

    if fixed_folder:
        folder_tujuan = fixed_folder
    else:
        inp_folder = console.input("Nama folder tujuan [dim](Enter = utama, 'batal' = keluar)[/dim]: ").strip()
        if inp_folder.lower() in ("batal", "cancel", "0"):
            return False
        folder_tujuan = resolve_folder_name(inp_folder or "utama", folders_cache)

    console.print()
    berhasil = eksekusi_batch_upload(client, queue_files, folder_tujuan)
    pause_dan_clear()
    return berhasil


def alur_hapus_di_root(client: GitHubCloudClient, folders_cache: list, arg: str = "") -> bool:
    """
    Menghapus satu atau banyak target di level Root:
    - Target tanpa '/' dianggap nama FOLDER (Release), misal: del GITUS, folder2
    - Target dengan '/' dianggap FILE spesifik, misal: del utama/a.txt, utama/b.txt
    """
    if not folders_cache:
        console.print("[yellow]Belum ada folder di repository ini.[/yellow]")
        pause_dan_clear()
        return False

    raw_targets = arg
    while True:
        if not raw_targets:
            render_folder_table(folders_cache, page=1, page_size=len(folders_cache))
            console.print(
                "[dim]Masukkan nama [bold]folder[/bold] atau [bold]folder/file[/bold] "
                "(pisahkan dengan spasi atau koma, 'batal' = keluar)[/dim]"
            )
            raw_targets = console.input("Target hapus: ").strip()
            if raw_targets.lower() in ("batal", "cancel", "0"):
                return False

        tokens = pecah_argumen_multi(raw_targets)
        if not tokens:
            raw_targets = ""
            continue

        # Daftar item valid: dict berisi tipe ('folder' atau 'file'), info objek, dan label tampilan
        valid_targets = []
        seen_keys = set()
        errors = []
        folder_files_cache = {}

        with console.status("[cyan]Memvalidasi target penghapusan...[/cyan]"):
            for tok in tokens:
                parsed_ff = parse_target_folder_file(tok)

                if parsed_ff:
                    # Target berupa folder/file
                    f_raw, file_q = parsed_ff
                    folder_obj = cari_folder_objek(f_raw, folders_cache)
                    if not folder_obj:
                        errors.append(f"Folder '{f_raw}' pada '{tok}' tidak ditemukan.")
                        continue

                    f_name = folder_obj["folder"]
                    if f_name not in folder_files_cache:
                        try:
                            folder_files_cache[f_name] = client.list_files(f_name)
                        except Exception as e:
                            errors.append(f"Gagal membaca folder '{f_name}': {e}")
                            continue

                    asset_obj, err_msg = cocokkan_file_by_nama(folder_files_cache[f_name], file_q)
                    if not asset_obj:
                        errors.append(f"[{f_name}] {err_msg}")
                        continue

                    key = ("file", asset_obj["id"])
                    if key not in seen_keys:
                        seen_keys.add(key)
                        valid_targets.append({
                            "tipe": "file",
                            "folder": f_name,
                            "nama": asset_obj["nama"],
                            "detail": format_ukuran(asset_obj["ukuran"]),
                            "asset_id": asset_obj["id"],
                        })
                else:
                    # Target berupa nama folder langsung (misal: del GITUS)
                    folder_obj = cari_folder_objek(tok, folders_cache)
                    if not folder_obj:
                        errors.append(f"Folder '{tok}' tidak ditemukan.")
                        continue

                    key = ("folder", folder_obj["id"])
                    if key not in seen_keys:
                        seen_keys.add(key)
                        valid_targets.append({
                            "tipe": "folder",
                            "folder": folder_obj["folder"],
                            "nama": folder_obj["folder"],
                            "detail": f"Seluruh folder ({folder_obj['jumlah_file']} file)",
                            "release_id": folder_obj["id"],
                        })

        if errors:
            for err in errors:
                console.print(f"[yellow]⚠ {err}[/yellow]")

        if not valid_targets:
            console.print("[red]Tidak ada target valid yang bisa dihapus. Silakan periksa kembali.[/red]\n")
            raw_targets = ""
            continue

        break

    # Tampilkan tabel konfirmasi hapus massal
    conf_table = Table(
        title=f"[bold red]KONFIRMASI HAPUS MASSAL ({len(valid_targets)} Item)[/bold red]",
        box=box.ROUNDED,
        border_style="red",
        header_style="bold yellow",
        expand=True,
    )
    conf_table.add_column("Tipe", width=10, justify="center")
    conf_table.add_column("Target", style="bold white")
    conf_table.add_column("Keterangan", style="dim white", width=26, justify="right")

    for item in valid_targets:
        if item["tipe"] == "folder":
            conf_table.add_row("[bold red]📁 FOLDER[/bold red]", item["nama"], item["detail"])
        else:
            conf_table.add_row("[yellow]📄 FILE[/yellow]", f"{item['folder']}/{item['nama']}", item["detail"])

    console.print()
    console.print(conf_table)

    while True:
        yakin = console.input("[bold red]Yakin hapus permanen semua item di atas? (y/n): [/bold red]").strip().lower()
        if yakin in ("y", "ya"):
            sukses = 0
            with console.status("[red]Menghapus target dari GitHub...[/red]"):
                for item in valid_targets:
                    try:
                        if item["tipe"] == "folder":
                            client.delete_folder(item["release_id"], item["folder"])
                            console.print(f"[bold green]✔ Folder '{item['folder']}' berhasil dihapus.[/bold green]")
                        else:
                            client.delete_file(item["asset_id"])
                            console.print(f"[bold green]✔ File '{item['folder']}/{item['nama']}' berhasil dihapus.[/bold green]")
                        sukses += 1
                    except Exception as e:
                        console.print(f"[bold red]✘ Gagal menghapus '{item['nama']}': {e}[/bold red]")

            pause_dan_clear()
            return sukses > 0

        if yakin in ("n", "no", "tidak", "batal"):
            console.print("[dim]Penghapusan dibatalkan.[/dim]")
            pause_dan_clear()
            return False

        console.print("[red]Ketik 'y' untuk menghapus atau 'n' untuk membatalkan.[/red]")


def alur_hapus_di_folder(
    client: GitHubCloudClient,
    folder_name: str,
    files_cache: list,
    arg: str = "",
) -> bool:
    """
    Menghapus satu atau banyak file sekaligus di dalam folder aktif.
    Pemisah argumen bisa spasi atau koma.
    """
    if not files_cache:
        console.print(f"[yellow]Folder '{folder_name}' kosong, tidak ada file yang bisa dihapus.[/yellow]")
        pause_dan_clear()
        return False

    raw_targets = arg
    while True:
        if not raw_targets:
            tampilkan_tabel_file(folder_name, files_cache, page=1, page_size=len(files_cache))
            console.print(
                "[dim]Masukkan nama file yang akan dihapus (pisahkan dengan spasi atau koma, 'batal' = keluar)[/dim]"
            )
            raw_targets = console.input("Nama file: ").strip()
            if raw_targets.lower() in ("batal", "cancel", "0"):
                return False

        tokens = pecah_argumen_multi(raw_targets)
        if not tokens:
            raw_targets = ""
            continue

        valid_assets = []
        seen_ids = set()
        errors = []

        for tok in tokens:
            asset_obj, err_msg = cocokkan_file_by_nama(files_cache, tok)
            if not asset_obj:
                errors.append(err_msg)
                continue
            if asset_obj["id"] not in seen_ids:
                seen_ids.add(asset_obj["id"])
                valid_assets.append(asset_obj)

        if errors:
            for err in errors:
                console.print(f"[yellow]⚠ {err}[/yellow]")

        if not valid_assets:
            console.print("[red]Tidak ada file valid yang cocok. Silakan coba lagi.[/red]\n")
            raw_targets = ""
            continue

        break

    conf_table = Table(
        title=f"[bold red]KONFIRMASI HAPUS {len(valid_assets)} FILE DI /{folder_name}[/bold red]",
        box=box.ROUNDED,
        border_style="red",
        header_style="bold yellow",
        expand=True,
    )
    conf_table.add_column("Nama File", style="bold white")
    conf_table.add_column("Ukuran", style="green", width=14, justify="right")

    for asset in valid_assets:
        conf_table.add_row(f"📄 {asset['nama']}", format_ukuran(asset["ukuran"]))

    console.print()
    console.print(conf_table)

    while True:
        yakin = console.input("[bold red]Yakin hapus permanen semua file di atas? (y/n): [/bold red]").strip().lower()
        if yakin in ("y", "ya"):
            sukses = 0
            with console.status("[red]Menghapus file dari GitHub...[/red]"):
                for asset in valid_assets:
                    try:
                        client.delete_file(asset["id"])
                        console.print(f"[bold green]✔ File '{asset['nama']}' berhasil dihapus.[/bold green]")
                        sukses += 1
                    except Exception as e:
                        console.print(f"[bold red]✘ Gagal menghapus '{asset['nama']}': {e}[/bold red]")

            pause_dan_clear()
            return sukses > 0

        if yakin in ("n", "no", "tidak", "batal"):
            console.print("[dim]Penghapusan dibatalkan.[/dim]")
            pause_dan_clear()
            return False

        console.print("[red]Ketik 'y' untuk menghapus atau 'n' untuk membatalkan.[/red]")


def alur_download_file(
    client: GitHubCloudClient,
    os_type: str,
    folders_cache: list,
    arg: str = "",
    fixed_folder: str = None,
    files_cache: list = None,
):
    folder_name = fixed_folder
    file_query = arg.strip() if (fixed_folder and arg) else None

    if not fixed_folder and arg:
        parsed = parse_target_folder_file(arg)
        if not parsed:
            console.print("[yellow]Format tidak sesuai. Gunakan: [bold]dl folder/nama_file[/bold][/yellow]")
            pause_dan_clear()
            return
        folder_raw, file_query = parsed
        folder_name = resolve_folder_name(folder_raw, folders_cache)

    while True:
        if not folder_name:
            inp = console.input("Nama folder [dim](Enter = utama, 'batal' = keluar)[/dim]: ").strip()
            if inp.lower() in ("batal", "cancel", "0"):
                return
            folder_name = resolve_folder_name(inp or "utama", folders_cache)

        try:
            if fixed_folder and files_cache is not None:
                files = files_cache
            else:
                with console.status(f"[cyan]Memuat isi folder '{folder_name}'...[/cyan]"):
                    files = client.list_files(folder_name)
            break
        except FileNotFoundError:
            console.print(f"[red]Folder '{folder_name}' tidak ditemukan. Coba lagi.[/red]")
            folder_name = None
            file_query = None
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            pause_dan_clear()
            return

    if not files:
        console.print(f"[yellow]Folder '{folder_name}' kosong.[/yellow]")
        pause_dan_clear()
        return

    target_asset = None
    pesan_err = None
    if file_query:
        target_asset, pesan_err = cocokkan_file_by_nama(files, file_query)

    while not target_asset:
        if pesan_err:
            console.print(f"[yellow]{pesan_err}[/yellow]")
        tampilkan_tabel_file(folder_name, files, page=1, page_size=len(files))
        pilih = console.input("\nMasukkan [bold]Nama File[/bold] ('batal' = keluar): ").strip()
        if pilih.lower() in ("batal", "cancel", "0"):
            return

        target_asset, pesan_err = cocokkan_file_by_nama(files, pilih)

    default_dir = get_default_download_dir(os_type)
    custom_dir = console.input(f"Simpan ke folder [dim](Enter = {default_dir})[/dim]: ").strip()
    dest_dir = bersihkan_path(custom_dir, os_type) if custom_dir else default_dir

    try:
        with console.status(f"[bold cyan]Mengunduh '{target_asset['nama']}'...[/bold cyan]"):
            saved_path = client.download_file(target_asset, dest_dir)
        console.print(
            Panel(
                f"[bold green]✔ Unduhan selesai![/bold green]\n"
                f"[bold]Tersimpan di:[/bold] [cyan]{saved_path}[/cyan]",
                border_style="green",
                box=box.ROUNDED,
            )
        )
    except Exception as e:
        console.print(Panel(f"[bold red]✘ Gagal Unduh:[/bold red] {e}", border_style="red"))

    pause_dan_clear()


def masuk_ke_folder(client: GitHubCloudClient, cfg: dict, folder_name: str) -> tuple[bool, bool]:
    os_type = cfg["os"]
    files_cache = []
    need_refresh = True
    ada_perubahan = False
    current_page = 1

    while True:
        if need_refresh:
            try:
                with console.status(f"[cyan]Membuka folder '{folder_name}'...[/cyan]"):
                    files_cache = client.list_files(folder_name)
                need_refresh = False
            except FileNotFoundError:
                console.print(f"[red]Folder '{folder_name}' tidak ditemukan.[/red]")
                pause_dan_clear()
                return ada_perubahan, False
            except Exception as e:
                console.print(f"[red]Gagal memuat isi folder: {e}[/red]")
                pause_dan_clear()
                return ada_perubahan, False

        total_pages = max(1, math.ceil(len(files_cache) / PAGE_SIZE))
        current_page = max(1, min(current_page, total_pages))

        clear_screen()
        render_header(cfg, current_folder=folder_name)
        tampilkan_tabel_file(folder_name, files_cache, page=current_page, page_size=PAGE_SIZE)

        console.print(
            "[dim]Perintah: [bold white]up[/bold white] upload  •  [bold white]dl[/bold white] unduh  •  "
            "[bold white]del[/bold white] hapus  •  [bold white]..[/bold white] kembali  •  "
            "[bold white]h[/bold white] bantuan[/dim]"
        )
        raw_input = console.input(f"[bold cyan]/{folder_name} ❯ [/bold cyan]").strip()

        if not raw_input:
            continue

        parts = raw_input.split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ("..", "back", "kembali") or raw_input.lower() in ("cd ..", "cd.."):
            return ada_perubahan, False

        elif cmd in ("h", "help", "?"):
            clear_screen()
            tampilkan_panduan_help(di_dalam_folder=True)
            pause_dan_clear()

        elif cmd in ("n", "next", ">"):
            if current_page < total_pages:
                current_page += 1
            else:
                console.print("[yellow]Sudah berada di halaman terakhir.[/yellow]")
                pause_dan_clear()

        elif cmd in ("p", "prev", "<"):
            if current_page > 1:
                current_page -= 1
            else:
                console.print("[yellow]Sudah berada di halaman pertama.[/yellow]")
                pause_dan_clear()

        elif cmd in ("page", "pg"):
            if arg.isdigit() and 1 <= int(arg) <= total_pages:
                current_page = int(arg)
            else:
                console.print(f"[red]Halaman tidak valid (tersedia: 1 - {total_pages}).[/red]")
                pause_dan_clear()

        elif cmd in ("r", "refresh"):
            need_refresh = True

        elif cmd in ("up", "upload"):
            clear_screen()
            console.print(f"[bold cyan]=== UPLOAD KE FOLDER: {folder_name} ===[/bold cyan]")
            if alur_upload_interaktif(client, os_type, [], arg=arg, fixed_folder=folder_name):
                need_refresh = True
                ada_perubahan = True

        elif cmd in ("dl", "download"):
            clear_screen()
            console.print(f"[bold cyan]=== DOWNLOAD DARI: {folder_name} ===[/bold cyan]")
            alur_download_file(client, os_type, [], arg=arg, fixed_folder=folder_name, files_cache=files_cache)

        elif cmd in ("del", "delete", "rm"):
            clear_screen()
            console.print(f"[bold red]=== HAPUS FILE DI: {folder_name} ===[/bold red]")
            if alur_hapus_di_folder(client, folder_name, files_cache, arg=arg):
                need_refresh = True
                ada_perubahan = True

        elif cmd in ("0", "exit", "quit", "q", "keluar"):
            return ada_perubahan, True

        else:
            matched, _ = cocokkan_file_by_nama(files_cache, raw_input)
            if matched:
                console.print(f"\nFile [bold yellow]{matched['nama']}[/bold yellow] dipilih. Ketik [bold cyan]dl[/bold cyan] untuk unduh atau [bold red]del[/bold red] untuk hapus:")
                aksi = console.input("[bold]Aksi (dl/del/batal): [/bold]").strip().lower()
                if aksi in ("dl", "download"):
                    clear_screen()
                    alur_download_file(client, os_type, [], arg=matched["nama"], fixed_folder=folder_name, files_cache=files_cache)
                elif aksi in ("del", "delete"):
                    clear_screen()
                    if alur_hapus_di_folder(client, folder_name, files_cache, arg=matched["nama"]):
                        need_refresh = True
                        ada_perubahan = True
            else:
                console.print(f"[red]Perintah atau file '{raw_input}' tidak dikenali.[/red] Ketik [bold]h[/bold] untuk panduan.")
                pause_dan_clear()


def menu_interaktif(client: GitHubCloudClient, cfg: dict):
    os_type = cfg["os"]
    folders_cache = []
    need_refresh = True
    current_page = 1

    while True:
        if need_refresh:
            try:
                with console.status("[cyan]Memuat daftar folder...[/cyan]"):
                    folders_cache = client.list_folders()
                need_refresh = False
            except Exception as e:
                folders_cache = []
                need_refresh = False
                console.print(f"[red]Gagal memuat folder: {e}[/red]")

        total_pages = max(1, math.ceil(len(folders_cache) / PAGE_SIZE))
        current_page = max(1, min(current_page, total_pages))

        clear_screen()
        render_header(cfg, current_folder=None)
        render_folder_table(folders_cache, current_page, PAGE_SIZE)

        console.print("[dim]Ketik [bold white]nama folder[/bold white] untuk masuk  •  [bold white]h[/bold white] / [bold white]help[/bold white] panduan  •  [bold white]0[/bold white] keluar[/dim]")
        raw_input = console.input("[bold cyan]❯ [/bold cyan]").strip()

        if not raw_input:
            continue

        parts = raw_input.split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ("h", "help", "?"):
            clear_screen()
            tampilkan_panduan_help(di_dalam_folder=False)
            pause_dan_clear()

        elif cmd in ("n", "next", ">"):
            if current_page < total_pages:
                current_page += 1
            else:
                console.print("[yellow]Sudah berada di halaman terakhir.[/yellow]")
                pause_dan_clear()

        elif cmd in ("p", "prev", "<"):
            if current_page > 1:
                current_page -= 1
            else:
                console.print("[yellow]Sudah berada di halaman pertama.[/yellow]")
                pause_dan_clear()

        elif cmd in ("page", "pg"):
            if arg.isdigit() and 1 <= int(arg) <= total_pages:
                current_page = int(arg)
            else:
                console.print(f"[red]Halaman tidak valid (tersedia: 1 - {total_pages}).[/red]")
                pause_dan_clear()

        elif cmd in ("r", "refresh"):
            need_refresh = True

        elif cmd in ("open", "files", "ls", "cd"):
            target_name = arg or console.input("Nama folder tujuan: ").strip()
            if target_name:
                resolved = resolve_folder_name(target_name, folders_cache)
                berubah, keluar = masuk_ke_folder(client, cfg, resolved)
                if berubah:
                    need_refresh = True
                if keluar:
                    clear_screen()
                    console.print("[bold cyan]Keluar dari Awan CLI. Sampai jumpa![/bold cyan]")
                    break

        elif cmd in ("up", "upload"):
            clear_screen()
            console.print("[bold cyan]=== MULTI-FILE UPLOAD ===[/bold cyan]")
            if alur_upload_interaktif(client, os_type, folders_cache, arg=arg):
                need_refresh = True

        elif cmd in ("dl", "download"):
            clear_screen()
            console.print("[bold cyan]=== DOWNLOAD FILE ===[/bold cyan]")
            alur_download_file(client, os_type, folders_cache, arg=arg)

        elif cmd in ("del", "delete", "rm"):
            clear_screen()
            console.print("[bold red]=== HAPUS FOLDER / FILE ===[/bold red]")
            if alur_hapus_di_root(client, folders_cache, arg=arg):
                need_refresh = True

        elif cmd == "reset":
            cfg = setup_awal()
            os_type = cfg["os"]
            client = GitHubCloudClient(cfg["token"], cfg["owner"], cfg["repo"])
            need_refresh = True
            current_page = 1

        elif cmd in ("0", "exit", "quit", "q", "keluar"):
            clear_screen()
            console.print("[bold cyan]Keluar dari Awan CLI. Sampai jumpa![/bold cyan]")
            break

        else:
            folder_obj = cari_folder_objek(raw_input, folders_cache)
            if folder_obj:
                berubah, keluar = masuk_ke_folder(client, cfg, folder_obj["folder"])
                if berubah:
                    need_refresh = True
                if keluar:
                    clear_screen()
                    console.print("[bold cyan]Keluar dari Awan CLI. Sampai jumpa![/bold cyan]")
                    break
            else:
                console.print(f"[red]Folder atau perintah '{raw_input}' tidak ditemukan.[/red] Ketik [bold]h[/bold] untuk bantuan.")
                pause_dan_clear()


def main():
    tampilkan_dan_konfirmasi_sk()

    cfg = muat_config()
    if not cfg:
        cfg = setup_awal()

    client = GitHubCloudClient(cfg["token"], cfg["owner"], cfg["repo"])

    if len(sys.argv) >= 2:
        clear_screen()
        raw_args = " ".join(f'"{a}"' if " " in a else a for a in sys.argv[1:])
        valid_files, invalid_items = ekstrak_daftar_file(raw_args, cfg["os"])
        if invalid_items:
            console.print(f"[yellow]⚠ Diabaikan: {', '.join(invalid_items)}[/yellow]")
        if valid_files:
            tampilkan_antrean_upload(valid_files)
            folder = console.input("Nama folder tujuan [dim](Enter = utama)[/dim]: ").strip() or "utama"
            eksekusi_batch_upload(client, valid_files, folder)
            pause_dan_clear()

    menu_interaktif(client, cfg)


if __name__ == "__main__":
    main()