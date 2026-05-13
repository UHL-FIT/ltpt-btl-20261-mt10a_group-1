"""
views/examination_view.py
=========================
Giao diện hiển thị lịch sử khám bệnh của bệnh nhân đang chọn.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from views.main_window import (COLOR_BG, COLOR_WHITE, COLOR_PRIMARY,
                                COLOR_TEXT, COLOR_BORDER, COLOR_SUCCESS,
                                COLOR_DANGER, COLOR_TEXT_LIGHT)
from utils.validators import kiem_tra_ngay, kiem_tra_huyet_ap, kiem_tra_nhiet_do


def tao_examination_view(parent_frame):
    """
    Tạo giao diện lịch sử khám bên trong content frame.

    Args:
        parent_frame (tk.Frame): Frame cha.

    Returns:
        dict: Tham chiếu tới các widget.
    """
    ev = {}

    # ─── Patient Selection ───
    select_frame = tk.Frame(parent_frame, bg=COLOR_WHITE, pady=8, padx=10)
    select_frame.pack(fill=tk.X, pady=(0, 8))

    tk.Label(select_frame, text="Mã BN:", font=('Segoe UI', 10, 'bold'),
             bg=COLOR_WHITE, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=(0, 5))

    ev['ent_ma_bn'] = ttk.Entry(select_frame, width=15, font=('Segoe UI', 10))
    ev['ent_ma_bn'].pack(side=tk.LEFT, padx=3)

    ev['btn_load'] = tk.Button(
        select_frame, text="🔍 Xem lịch sử", font=('Segoe UI', 10),
        bg=COLOR_PRIMARY, fg=COLOR_WHITE, bd=0, padx=12, pady=5, cursor="hand2"
    )
    ev['btn_load'].pack(side=tk.LEFT, padx=5)

    ev['lbl_patient_name'] = tk.Label(
        select_frame, text="", font=('Segoe UI', 10, 'italic'),
        bg=COLOR_WHITE, fg=COLOR_TEXT_LIGHT
    )
    ev['lbl_patient_name'].pack(side=tk.LEFT, padx=10)

    # Buttons
    ev['btn_them_kham'] = tk.Button(
        select_frame, text="➕ Thêm lần khám", font=('Segoe UI', 10),
        bg=COLOR_SUCCESS, fg=COLOR_WHITE, bd=0, padx=12, pady=5, cursor="hand2"
    )
    ev['btn_them_kham'].pack(side=tk.RIGHT, padx=3)

    ev['btn_xoa_kham'] = tk.Button(
        select_frame, text="🗑️ Xóa", font=('Segoe UI', 10),
        bg=COLOR_DANGER, fg=COLOR_WHITE, bd=0, padx=12, pady=5, cursor="hand2"
    )
    ev['btn_xoa_kham'].pack(side=tk.RIGHT, padx=3)

    # ─── TREEVIEW ───
    tree_frame = tk.Frame(parent_frame, bg=COLOR_WHITE)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    scroll_y = ttk.Scrollbar(tree_frame)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    cols = ["ID", "Ngày khám", "Triệu chứng", "Chẩn đoán", "Huyết áp", "Nhiệt độ", "Bác sĩ", "Ghi chú"]
    ev['cols'] = cols

    tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                         yscrollcommand=scroll_y.set)
    ev['tree'] = tree
    scroll_y.config(command=tree.yview)

    col_widths = {"ID": 50, "Ngày khám": 110, "Triệu chứng": 200, "Chẩn đoán": 200,
                  "Huyết áp": 80, "Nhiệt độ": 70, "Bác sĩ": 120, "Ghi chú": 150}

    for col in cols:
        tree.heading(col, text=col)
        w = col_widths.get(col, 100)
        anchor = tk.W if col in ["Triệu chứng", "Chẩn đoán", "Ghi chú"] else tk.CENTER
        tree.column(col, width=w, anchor=anchor)

    tree.pack(fill=tk.BOTH, expand=True)

    return ev


def hien_thi_lich_su_kham(ev, df):
    """
    Hiển thị dữ liệu lịch sử khám lên TreeView.

    Args:
        ev (dict): Dictionary UI widgets.
        df (pandas.DataFrame): Dữ liệu lịch sử khám.
    """
    tree = ev['tree']
    for row in tree.get_children():
        tree.delete(row)

    if df.empty:
        return

    for _, row in df.iterrows():
        values = [
            row.get("id", ""),
            row.get("ngay_kham", ""),
            row.get("trieu_chung", ""),
            row.get("chan_doan", ""),
            row.get("huyet_ap", ""),
            f"{float(row.get('nhiet_do', 0)):.1f}" if row.get("nhiet_do") else "",
            row.get("bac_si", ""),
            row.get("ghi_chu", "")
        ]
        tree.insert("", tk.END, values=values)


def hien_thi_form_kham(parent_root):
    """
    Popup form thêm lần khám mới.

    Args:
        parent_root (tk.Tk): Cửa sổ cha.

    Returns:
        dict/None: Dữ liệu lần khám hoặc None.
    """
    top = tk.Toplevel(parent_root)
    top.title("➕ Thêm lần khám")
    top.configure(bg=COLOR_BG)
    top.resizable(False, False)
    top.grab_set()

    result = []

    # Header
    header = tk.Frame(top, bg=COLOR_PRIMARY, height=45)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    tk.Label(header, text="🩺 Thêm lần khám mới", font=('Segoe UI', 12, 'bold'),
             bg=COLOR_PRIMARY, fg=COLOR_WHITE, padx=15).pack(side=tk.LEFT, fill=tk.Y)

    form = tk.Frame(top, bg=COLOR_BG, padx=20, pady=15)
    form.pack(fill=tk.BOTH, expand=True)

    from datetime import datetime
    fields = {}

    def add_entry(label, key, row, width=30):
        tk.Label(form, text=f"{label}:", font=('Segoe UI', 10),
                 bg=COLOR_BG, fg=COLOR_TEXT).grid(row=row, column=0, padx=(0, 10), pady=7, sticky=tk.E)
        ent = ttk.Entry(form, width=width, font=('Segoe UI', 10))
        ent.grid(row=row, column=1, pady=7, sticky=tk.W)
        fields[key] = ent
        return ent

    add_entry("Ngày khám (*)", "ngay_kham", 0)
    fields["ngay_kham"].insert(0, datetime.now().strftime("%d/%m/%Y"))
    add_entry("Triệu chứng", "trieu_chung", 1)
    add_entry("Chẩn đoán", "chan_doan", 2)
    add_entry("Huyết áp (VD: 120/80)", "huyet_ap", 3)
    add_entry("Nhiệt độ (°C)", "nhiet_do", 4)
    add_entry("Bác sĩ", "bac_si", 5)
    add_entry("Ghi chú", "ghi_chu", 6)

    def on_save():
        ngay_kham = fields["ngay_kham"].get().strip()
        ok_ngay, _ = kiem_tra_ngay(ngay_kham)
        if not ngay_kham or not ok_ngay:
            messagebox.showwarning("Lỗi", "Ngày khám không hợp lệ (dd/mm/yyyy)!", parent=top)
            return

        ha = fields["huyet_ap"].get().strip()
        if ha and not kiem_tra_huyet_ap(ha):
            messagebox.showwarning("Lỗi", "Huyết áp không hợp lệ (VD: 120/80)!", parent=top)
            return

        nd_str = fields["nhiet_do"].get().strip()
        ok_nd, nhiet_do = kiem_tra_nhiet_do(nd_str)
        if not ok_nd:
            messagebox.showwarning("Lỗi", "Nhiệt độ không hợp lệ (30-45°C)!", parent=top)
            return

        result.append({
            "ngay_kham": ngay_kham,
            "trieu_chung": fields["trieu_chung"].get().strip(),
            "chan_doan": fields["chan_doan"].get().strip(),
            "huyet_ap": ha,
            "nhiet_do": nhiet_do,
            "bac_si": fields["bac_si"].get().strip(),
            "ghi_chu": fields["ghi_chu"].get().strip()
        })
        top.destroy()

    btn_frame = tk.Frame(form, bg=COLOR_BG)
    btn_frame.grid(row=7, column=0, columnspan=2, pady=(15, 5))

    tk.Button(btn_frame, text="💾 Lưu", font=('Segoe UI', 11, 'bold'),
              bg=COLOR_SUCCESS, fg=COLOR_WHITE, bd=0, padx=20, pady=6,
              command=on_save, cursor="hand2").pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="❌ Hủy", font=('Segoe UI', 11),
              bg="#9E9E9E", fg=COLOR_WHITE, bd=0, padx=20, pady=6,
              command=top.destroy, cursor="hand2").pack(side=tk.LEFT, padx=8)

    top.update_idletasks()
    x = parent_root.winfo_x() + (parent_root.winfo_width() - top.winfo_reqwidth()) // 2
    y = parent_root.winfo_y() + (parent_root.winfo_height() - top.winfo_reqheight()) // 2
    top.geometry(f"+{x}+{y}")

    top.wait_window()
    return result[0] if result else None
