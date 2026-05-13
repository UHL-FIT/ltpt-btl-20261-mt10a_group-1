"""
build.py
========
Script đóng gói ứng dụng thành file .exe cho Windows bằng PyInstaller.

Cách dùng:
    python build.py
"""

import subprocess
import sys
import os
import shutil

TEN_APP = "PatientManagement"
FILE_MAIN = "main.py"
THU_MUC_DATA = "data"
THU_MUC_ASSETS = "assets"
ICON_FILE = r"assets\app_icon.ico"


def kiem_tra_pyinstaller():
    """Kiểm tra PyInstaller đã cài chưa."""
    try:
        import PyInstaller
        print(f"  [OK] PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("  [..] Đang cài đặt PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build():
    """Chạy PyInstaller để đóng gói."""
    print("\n" + "=" * 50)
    print("  ĐÓNG GÓI ỨNG DỤNG QUẢN LÝ BỆNH NHÂN")
    print("=" * 50)

    kiem_tra_pyinstaller()

    # Xóa build cũ
    for folder in ["build", "dist", f"{TEN_APP}.spec"]:
        if os.path.exists(folder):
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            else:
                os.remove(folder)

    # Build GUI
    print(f"\n  Đang đóng gói {FILE_MAIN} -> {TEN_APP}.exe...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", TEN_APP,
        "--noconfirm", "--windowed", "--clean",
        "--add-data", f"{THU_MUC_ASSETS};{THU_MUC_ASSETS}",
        "--hidden-import", "pandas",
        "--hidden-import", "numpy",
        "--hidden-import", "matplotlib",
    ]

    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd.extend(["--icon", ICON_FILE])

    cmd.append(FILE_MAIN)
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode != 0:
        print("\n  [FAIL] Build thất bại!")
        return False

    exe_path = os.path.join("dist", TEN_APP, f"{TEN_APP}.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("\n" + "=" * 50)
        print(f"  [OK] BUILD THÀNH CÔNG!")
        print(f"  File: {os.path.abspath(exe_path)}")
        print(f"  Size: {size_mb:.1f} MB")
        print("=" * 50)
        return True

    print("\n  [FAIL] Không tìm thấy file exe!")
    return False


if __name__ == "__main__":
    build()
