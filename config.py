import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / ".gh_cloud_config.json"


def simpan_config(os_type: str, token: str, owner: str, repo: str) -> dict:
    data = {
        "os": os_type,
        "token": token,
        "owner": owner,
        "repo": repo,
    }
    CONFIG_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")
    return data


def muat_config():
    if not CONFIG_FILE.exists():
        return None
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None