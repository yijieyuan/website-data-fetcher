import os
import json
import shutil
import time

import requests


def download_avatar(url, dest):
    """Download an image URL to dest. Archive the previous file if the bytes changed.

    Returns True if the image was written (new or changed), False otherwise.
    """
    if not url:
        return False
    base_dir = os.path.dirname(dest)
    name = os.path.splitext(os.path.basename(dest))[0]      # e.g. "kaggle-avatar"
    ext = os.path.splitext(dest)[1] or ".png"
    archive_dir = os.path.join(base_dir, "archive", name)

    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        resp.raise_for_status()
        new_bytes = resp.content
    except Exception as e:
        print(f"   [Avatar] Download failed: {e}")
        return False

    changed = True
    if os.path.exists(dest):
        try:
            with open(dest, "rb") as f:
                changed = f.read() != new_bytes
        except OSError:
            changed = True
    if not changed:
        return False

    # Archive the old version before overwriting
    if os.path.exists(dest):
        os.makedirs(archive_dir, exist_ok=True)
        timestamp = time.strftime("%Y-%m-%d_%H%M%S")
        shutil.copy2(dest, os.path.join(archive_dir, f"{name}_{timestamp}{ext}"))

    # Atomic save
    os.makedirs(base_dir, exist_ok=True)
    temp_file = dest + ".tmp"
    with open(temp_file, "wb") as f:
        f.write(new_bytes)
    os.replace(temp_file, dest)
    return True


def archive_and_save(output_file, new_data):
    """Compare new data with existing file. If changed, archive the old version, then save.

    Archive structure:
        data/
          kaggle.json              <- current
          archive/
            kaggle/
              kaggle_2026-04-11_013000.json
              kaggle_2026-04-09_220000.json
    """
    base_dir = os.path.dirname(output_file)
    name = os.path.splitext(os.path.basename(output_file))[0]  # e.g. "kaggle"
    archive_dir = os.path.join(base_dir, "archive", name)

    # Load existing data (minus last_updated) for comparison
    changed = True
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            # Compare without last_updated / last_active (these always change)
            old_cmp = {k: v for k, v in old_data.items() if k not in ("last_updated", "last_active")}
            new_cmp = {k: v for k, v in new_data.items() if k not in ("last_updated", "last_active")}
            changed = old_cmp != new_cmp
        except (json.JSONDecodeError, OSError):
            changed = True

    if changed and os.path.exists(output_file):
        # Archive the old version
        os.makedirs(archive_dir, exist_ok=True)
        timestamp = time.strftime("%Y-%m-%d_%H%M%S")
        archive_file = os.path.join(archive_dir, f"{name}_{timestamp}.json")
        shutil.copy2(output_file, archive_file)
        print(f"   [Archive] Saved previous version to {archive_file}")

    # Atomic save
    os.makedirs(base_dir, exist_ok=True)
    temp_file = output_file + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=4)
    os.replace(temp_file, output_file)

    return changed
