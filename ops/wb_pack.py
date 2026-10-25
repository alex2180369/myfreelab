"""Packs an unpacked docx directory into a docx, keeping the original file order.

Usage: python3 -I wb_pack.py <original.docx> <unpacked_dir> <out.docx>
"""
import sys
import zipfile
from pathlib import Path

original, folder, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
with zipfile.ZipFile(original) as zin:
    order = [i.filename for i in zin.infolist() if not i.filename.endswith("/")]

on_disk = sorted(
    str(p.relative_to(folder)).replace("\\", "/") for p in folder.rglob("*") if p.is_file() and not p.is_symlink()
)
names = [n for n in order if n in on_disk] + [n for n in on_disk if n not in order]

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
    for n in names:
        zout.write(folder / n, n)
print("packed", len(names), "files ->", out)
