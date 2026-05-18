import os
import shutil
import pathlib

def clean_pycache(root_dir='.'):
    print("===================================================")
    print("Đang dọn dẹp __pycache__ và file .pyc/.pyo...")
    print("===================================================")
    
    count_dirs = 0
    count_files = 0
    
    # Xóa các thư mục __pycache__
    for path in pathlib.Path(root_dir).rglob('__pycache__'):
        if path.is_dir():
            print(f"Xóa thư mục: {path}")
            shutil.rmtree(path)
            count_dirs += 1
            
    # Xóa các file .pyc và .pyo lẻ loi
    for ext in ('*.pyc', '*.pyo'):
        for path in pathlib.Path(root_dir).rglob(ext):
            if path.is_file():
                path.unlink()
                count_files += 1
                
    print("===================================================")
    print(f"Hoàn thành! Đã xóa {count_dirs} thư mục và {count_files} file.")
    print("===================================================")

if __name__ == '__main__':
    clean_pycache()