from pathlib import Path
import requests


class GitHubCloudClient:
    def __init__(self, token: str, owner: str, repo: str):
        self.owner = owner
        self.repo = repo
        self.api_base = f"https://api.github.com/repos/{owner}/{repo}"
        self.upload_base = f"https://uploads.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def format_tag(self, nama_folder: str) -> str:
        return nama_folder.strip().replace(" ", "-")

    def get_or_create_folder(self, nama_folder: str):
        tag = self.format_tag(nama_folder)
        resp = requests.get(f"{self.api_base}/releases/tags/{tag}", headers=self.headers)

        if resp.status_code == 401:
            raise PermissionError("Token GitHub tidak valid atau kedaluwarsa.")
        if resp.status_code == 200:
            return resp.json()["id"], tag

        payload = {
            "tag_name": tag,
            "name": f"Folder: {nama_folder}",
            "body": f"Direktori penyimpanan cloud: {nama_folder}",
            "draft": False,
            "prerelease": False,
        }
        create_resp = requests.post(f"{self.api_base}/releases", json=payload, headers=self.headers)
        create_resp.raise_for_status()
        return create_resp.json()["id"], tag

    def upload_file(
        self,
        file_path: Path,
        nama_folder: str,
        release_id: int = None,
        custom_name: str = None,
    ) -> str:
        if not file_path.is_file():
            raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

        if release_id is None:
            release_id, tag = self.get_or_create_folder(nama_folder)
        else:
            tag = self.format_tag(nama_folder)

        target_filename = custom_name if custom_name else file_path.name
        upload_url = f"{self.upload_base}/releases/{release_id}/assets"
        upload_headers = self.headers.copy()
        upload_headers["Content-Type"] = "application/octet-stream"

        with file_path.open("rb") as f:
            resp = requests.post(
                upload_url,
                headers=upload_headers,
                params={"name": target_filename},
                data=f,
            )

        if resp.status_code == 422:
            raise FileExistsError(f"File '{target_filename}' sudah ada di folder '{tag}'.")

        resp.raise_for_status()
        return resp.json()["browser_download_url"]

    def list_folders(self) -> list:
        resp = requests.get(
            f"{self.api_base}/releases",
            headers=self.headers,
            params={"per_page": 100},
        )
        if resp.status_code == 401:
            raise PermissionError("Token GitHub tidak valid. Ketik 'reset' untuk memperbarui.")
        resp.raise_for_status()
        return [
            {
                "id": item["id"],
                "folder": item["tag_name"],
                "jumlah_file": len(item.get("assets", [])),
                "tanggal": (item.get("published_at") or item.get("created_at") or "-")[:10],
            }
            for item in resp.json()
        ]

    def list_files(self, nama_folder: str) -> list:
        tag = self.format_tag(nama_folder)
        resp = requests.get(f"{self.api_base}/releases/tags/{tag}", headers=self.headers)
        if resp.status_code == 404:
            raise FileNotFoundError(f"Folder '{tag}' tidak ditemukan.")
        resp.raise_for_status()

        return [
            {
                "id": asset["id"],
                "nama": asset["name"],
                "ukuran": asset["size"],
                "url": asset["browser_download_url"],
                "api_url": asset["url"],
            }
            for asset in resp.json().get("assets", [])
        ]

    def list_files_by_release_id(self, release_id: int) -> list:
        resp = requests.get(f"{self.api_base}/releases/{release_id}/assets", headers=self.headers)
        resp.raise_for_status()
        return [
            {
                "id": asset["id"],
                "nama": asset["name"],
                "ukuran": asset["size"],
                "url": asset["browser_download_url"],
                "api_url": asset["url"],
            }
            for asset in resp.json()
        ]

    def download_file(self, asset: dict, dest_dir: Path) -> Path:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / asset["nama"]

        dl_headers = self.headers.copy()
        dl_headers["Accept"] = "application/octet-stream"

        with requests.get(asset["api_url"], headers=dl_headers, stream=True) as resp:
            resp.raise_for_status()
            with dest_path.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)

        return dest_path

    def delete_file(self, asset_id: int) -> bool:
        resp = requests.delete(
            f"{self.api_base}/releases/assets/{asset_id}",
            headers=self.headers,
        )
        resp.raise_for_status()
        return True

    def delete_folder(self, release_id: int, tag_name: str) -> bool:
        # 1. Hapus objek Release
        resp = requests.delete(
            f"{self.api_base}/releases/{release_id}",
            headers=self.headers,
        )
        if resp.status_code != 404:
            resp.raise_for_status()

        # 2. Hapus Git Tag agar tidak tertinggal sebagai tag kosong di repository
        tag_resp = requests.delete(
            f"{self.api_base}/git/refs/tags/{tag_name}",
            headers=self.headers,
        )
        if tag_resp.status_code not in (200, 204, 404, 422):
            tag_resp.raise_for_status()
        return True