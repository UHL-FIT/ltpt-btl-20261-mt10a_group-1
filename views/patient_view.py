"""
views/patient_view.py
=====================
Giao diện hiển thị danh sách bệnh nhân dạng TreeView.
Bao gồm toolbar thao tác và bộ lọc tìm kiếm.
"""

import tkinter as tk
from tkinter import ttk
from views.main_window import (COLOR_BG, COLOR_WHITE, COLOR_PRIMARY,
                                COLOR_TEXT, COLOR_BORDER, COLOR_ACCENT,
                                COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING)


def sort_treeview(tree, col, reverse):
    """
    Sắp xếp Treeview khi người dùng click vào tiêu đề cột.

    Args:
        tree (ttk.Treeview): Đối tượng bảng hiển thị.
        col (str): Tên cột cần sắp xếp.
        reverse (bool): True = Z-A, False = A-Z.
    """
    if col == "Chọn":
        return

    data_list = [(tree.set(k, col), k) for k in tree.get_children('')]

    try:
        data_list.sort(key=lambda t: float(str(t[0]).split(" ")[0]), reverse=reverse)
    except ValueError:
        data_list.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)

    for index, (val, k) in enumerate(data_list):
        tree.move(k, '', index)

    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


def tao_patient_view(parent_frame):
    """
    Tạo giao diện danh sách bệnh nhân bên trong content frame.

    Args:
        parent_frame (tk.Frame): Frame cha chứa nội dung.

    Returns:
        dict: Tham chiếu tới các widget bệnh nhân.
    """
    pv = {}

    # ─── TOOLBAR ───
    toolbar = tk.Frame(parent_frame, bg=COLOR_WHITE, pady=8, padx=10)
    toolbar.pack(fill=tk.X, pady=(0, 8))

    # Action buttons (left)
    action_frame = tk.Frame(toolbar, bg=COLOR_WHITE)
    action_frame.pack(side=tk.LEFT)

    pv['btn_them'] = tk.Button(
        action_frame, text="➕ Thêm BN", font=('Segoe UI', 10),
        bg=COLOR_SUCCESS, fg=COLOR_WHITE, bd=0, padx=12, pady=6,
        activebackground="#388E3C", activeforeground=COLOR_WHITE, cursor="hand2"
    )
    pv['btn_them'].pack(side=tk.LEFT, padx=(0, 5))

    pv['btn_sua'] = tk.Button(
        action_frame, text="✏️ Sửa", font=('Segoe UI', 10),
        bg=COLOR_PRIMARY, fg=COLOR_WHITE, bd=0, padx=12, pady=6,
        activebackground="#0D47A1", activeforeground=COLOR_WHITE, cursor="hand2"
    )
    pv['btn_sua'].pack(side=tk.LEFT, padx=3)

    pv['btn_xoa'] = tk.Button(
        action_frame, text="🗑️ Xóa", font=('Segoe UI', 10),
        bg=COLOR_DANGER, fg=COLOR_WHITE, bd=0, padx=12, pady=6,
        activebackground="#B71C1C", activeforeground=COLOR_WHITE, cursor="hand2"
    )
    pv['btn_xoa'].pack(side=tk.LEFT, padx=3)

    # Separator
    sep = tk.Frame(action_frame, bg=COLOR_BORDER, width=2)
    sep.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=2)

    pv['btn_import'] = tk.Button(
        action_frame, text="📂 Import CSV", font=('Segoe UI', 10),
        bg=COLOR_ACCENT, fg=COLOR_WHITE, bd=0, padx=10, pady=6,
        activebackground="#1976D2", activeforeground=COLOR_WHITE, cursor="hand2"
    )
    pv['btn_import'].pack(side=tk.LEFT, padx=3)

    pv['btn_export'] = tk.Button(
        action_frame, text="💾 Export CSV", font=('Segoe UI', 10),
        bg=COLOR_ACCENT, fg=COLOR_WHITE, bd=0, padx=10, pady=6,
        activebackground="#1976D2", activeforeground=COLOR_WHITE, cursor="hand2"
    )
    pv['btn_export'].pack(side=tk.LEFT, padx=3)

    # Search area (right)
    search_frame = tk.Frame(toolbar, bg=COLOR_WHITE)
    search_frame.pack(side=tk.RIGHT)

    tk.Label(search_frame, text="Tìm theo:", font=('Segoe UI', 10),
             bg=COLOR_WHITE, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=(10, 4))

    pv['cbo_search_by'] = ttk.Combobox(
        search_frame,
        values=["Tất cả", "Mã BN", "Họ tên", "Giới tính", "SĐT", "Bệnh chính"],
        state="readonly", width=12, font=('Segoe UI', 10)
    )
    pv['cbo_search_by'].set("Tất cả")
    pv['cbo_search_by'].pack(side=tk.LEFT, padx=3)

    pv['ent_search'] = ttk.Entry(search_frame, width=20, font=('Segoe UI', 10))
    pv['ent_search'].pack(side=tk.LEFT, padx=3)

    pv['btn_search'] = tk.Button(
        search_frame, text="🔍 Tìm", font=('Segoe UI', 10),
        bg=COLOR_PRIMARY, fg=COLOR_WHITE, bd=0, padx=10, pady=4,
        cursor="hand2"
    )
    pv['btn_search'].pack(side=tk.LEFT, padx=3)

    pv['btn_clear_search'] = tk.Button(
        search_frame, text="✖ Hủy", font=('Segoe UI', 10),
        bg="#9E9E9E", fg=COLOR_WHITE, bd=0, padx=10, pady=4,
        cursor="hand2"
    )
    pv['btn_clear_search'].pack(side=tk.LEFT, padx=3)

    # ─── TREEVIEW ───
    tree_frame = tk.Frame(parent_frame, bg=COLOR_WHITE)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    # Scrollbars
    scroll_y = ttk.Scrollbar(tree_frame)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
    scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    # Columns
    cols = ["Chọn", "STT", "Mã BN", "Họ tên", "Tuổi", "Giới tính",
            "SĐT", "Ngày tiếp nhận", "Bệnh chính", "Bệnh phụ", "BMI", "Phân loại"]
    pv['cols'] = cols

    tree = ttk.Treeview(
        tree_frame, columns=cols, show="headings",
        yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
    )
    pv['tree'] = tree

    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)

    # Configure columns
    col_widths = {
        "Chọn": 45, "STT": 45, "Mã BN": 90, "Họ tên": 180,
        "Tuổi": 55, "Giới tính": 75, "SĐT": 110,
        "Ngày tiếp nhận": 120, "Bệnh chính": 150, "Bệnh phụ": 130,
        "BMI": 60, "Phân loại": 100
    }

    for col in cols:
        heading_text = "☐" if col == "Chọn" else col
        if col != "Chọn":
            tree.heading(col, text=heading_text,
                         command=lambda _col=col: sort_treeview(tree, _col, False))
        else:
            tree.heading(col, text=heading_text)

        w = col_widths.get(col, 100)
        anchor = tk.W if col in ["Họ tên", "Bệnh chính", "Bệnh phụ"] else tk.CENTER
        tree.column(col, width=w, anchor=anchor, minwidth=40)

    tree.pack(fill=tk.BOTH, expand=True)

    return pv


def hien_thi_bang(pv, df):
    """
    Xóa dữ liệu cũ trên bảng và nạp lại toàn bộ từ DataFrame.

    Args:
        pv (dict): Dictionary UI widgets.
        df (pandas.DataFrame): Bảng dữ liệu bệnh nhân.
    """
    tree = pv['tree']
    tree.heading("Chọn", text="☐")

    for row in tree.get_children():
        tree.delete(row)

    if df.empty:
        return

    for idx, (_, row) in enumerate(df.iterrows(), start=1):
        bmi_val = row.get("bmi", 0)
        phan_loai = row.get("phan_loai_bmi", "N/A")

        values = [
            "☐",
            str(idx),
            row.get("ma_bn", ""),
            row.get("ho_ten", ""),
            int(row.get("tuoi", 0)) if row.get("tuoi", 0) else "",
            row.get("gioi_tinh", ""),
            row.get("sdt", ""),
            row.get("ngay_tiep_nhan", ""),
            row.get("benh_chinh", ""),
            row.get("benh_phu", ""),
            f"{float(bmi_val):.1f}" if bmi_val > 0 else "",
            phan_loai if phan_loai != "N/A" else ""
        ]

        item_id = tree.insert("", tk.END, values=values)

        # Color coding theo BMI
        if phan_loai in ["Béo phì độ I", "Béo phì độ II"]:
            tree.item(item_id, tags=('bmi_cao',))
        elif phan_loai == "Thiếu cân":
            tree.item(item_id, tags=('bmi_thap',))

    tree.tag_configure('bmi_cao', foreground=COLOR_DANGER)
    tree.tag_configure('bmi_thap', foreground=COLOR_WARNING)
