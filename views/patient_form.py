"""
views/patient_form.py
=====================
Form popup (Toplevel) để Thêm hoặc Sửa thông tin bệnh nhân.
Bao gồm validation và auto-calculate BMI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.validators import (kiem_tra_tuoi, kiem_tra_sdt, kiem_tra_ngay,
                               kiem_tra_chieu_cao, kiem_tra_can_nang)
from utils.bmi_calculator import tinh_bmi, phan_loai_bmi
from views.main_window import (COLOR_PRIMARY, COLOR_WHITE, COLOR_BG,
                                COLOR_TEXT, COLOR_BORDER, COLOR_SUCCESS)
from datetime import datetime


def hien_thi_form_benh_nhan(parent_root, is_edit=False, current_data=None):
    """
    Hiển thị cửa sổ Pop-up để Thêm hoặc Sửa thông tin Bệnh nhân.

    Args:
        parent_root (tk.Tk): Cửa sổ cha.
        is_edit (bool): True = Sửa, False = Thêm mới.
        current_data (dict): Dữ liệu bệnh nhân hiện tại (khi sửa).

    Returns:
        dict/None: Dictionary dữ liệu hoặc None nếu Hủy.
    """
    top = tk.Toplevel(parent_root)
    top.title("✏️ Sửa Bệnh nhân" if is_edit else "➕ Thêm Bệnh nhân mới")
    top.configure(bg=COLOR_BG)
    top.resizable(False, False)
    top.grab_set()

    result = []

    # ─── Header ───
    header = tk.Frame(top, bg=COLOR_PRIMARY, height=50)
    header.pack(fill=tk.X)
    header.pack_propagate(False)

    title_text = "Sửa thông tin Bệnh nhân" if is_edit else "Thêm Bệnh nhân mới"
    tk.Label(header, text=f"🏥 {title_text}",
             font=('Segoe UI', 13, 'bold'), bg=COLOR_PRIMARY, fg=COLOR_WHITE,
             padx=15).pack(side=tk.LEFT, fill=tk.Y)

    # ─── Form Area ───
    form_frame = tk.Frame(top, bg=COLOR_BG, padx=25, pady=15)
    form_frame.pack(fill=tk.BOTH, expand=True)

    # Helper function to create labeled entries
    entries = {}
    row_idx = 0

    def add_field(label, key, width=35, required=False, row=None):
        nonlocal row_idx
        if row is not None:
            row_idx = row

        lbl_text = f"{label} (*):" if required else f"{label}:"
        lbl = tk.Label(form_frame, text=lbl_text, font=('Segoe UI', 10),
                       bg=COLOR_BG, fg=COLOR_TEXT, anchor=tk.E)
        lbl.grid(row=row_idx, column=0, padx=(0, 10), pady=7, sticky=tk.E)

        ent = ttk.Entry(form_frame, width=width, font=('Segoe UI', 10))
        ent.grid(row=row_idx, column=1, pady=7, sticky=tk.W, columnspan=2)
        entries[key] = ent
        row_idx += 1
        return ent

    def add_combo(label, key, values, default="Nam"):
        nonlocal row_idx
        lbl = tk.Label(form_frame, text=f"{label}:", font=('Segoe UI', 10),
                       bg=COLOR_BG, fg=COLOR_TEXT, anchor=tk.E)
        lbl.grid(row=row_idx, column=0, padx=(0, 10), pady=7, sticky=tk.E)

        cbo = ttk.Combobox(form_frame, values=values, state="readonly",
                           width=33, font=('Segoe UI', 10))
        cbo.set(default)
        cbo.grid(row=row_idx, column=1, pady=7, sticky=tk.W, columnspan=2)
        entries[key] = cbo
        row_idx += 1
        return cbo

    # ─── Form Fields ───
    add_field("Họ tên", "ho_ten", required=True)
    add_field("Tuổi", "tuoi", required=True)
    add_combo("Giới tính", "gioi_tinh", ["Nam", "Nữ", "Khác"], "Nam")
    add_field("Số điện thoại", "sdt")
    add_field("Địa chỉ", "dia_chi")

    # Chiều cao & Cân nặng trên cùng dòng
    tk.Label(form_frame, text="Chiều cao (cm):", font=('Segoe UI', 10),
             bg=COLOR_BG, fg=COLOR_TEXT).grid(row=row_idx, column=0, padx=(0, 10), pady=7, sticky=tk.E)
    ent_cc = ttk.Entry(form_frame, width=14, font=('Segoe UI', 10))
    ent_cc.grid(row=row_idx, column=1, pady=7, sticky=tk.W)
    entries["chieu_cao"] = ent_cc

    tk.Label(form_frame, text="Cân nặng (kg):", font=('Segoe UI', 10),
             bg=COLOR_BG, fg=COLOR_TEXT).grid(row=row_idx, column=2, padx=(15, 5), pady=7, sticky=tk.W)
    row_idx += 1

    ent_cn = ttk.Entry(form_frame, width=14, font=('Segoe UI', 10))
    ent_cn.grid(row=row_idx - 1, column=2, pady=7, sticky=tk.E)
    entries["can_nang"] = ent_cn

    # BMI display
    lbl_bmi = tk.Label(form_frame, text="BMI: —", font=('Segoe UI', 10, 'italic'),
                       bg=COLOR_BG, fg=COLOR_PRIMARY)
    lbl_bmi.grid(row=row_idx, column=1, columnspan=2, pady=2, sticky=tk.W)
    row_idx += 1

    # Auto-calculate BMI
    def update_bmi(*args):
        cc = ent_cc.get().strip()
        cn = ent_cn.get().strip()
        if cc and cn:
            bmi = tinh_bmi(cc, cn)
            if bmi > 0:
                pl = phan_loai_bmi(bmi)
                lbl_bmi.config(text=f"BMI: {bmi:.1f} — {pl}")
            else:
                lbl_bmi.config(text="BMI: —")
        else:
            lbl_bmi.config(text="BMI: —")

    ent_cc.bind("<KeyRelease>", update_bmi)
    ent_cn.bind("<KeyRelease>", update_bmi)

    # Ngày tiếp nhận
    add_field("Ngày tiếp nhận (dd/mm/yyyy)", "ngay_tiep_nhan")
    add_field("Bệnh chính", "benh_chinh", required=True)
    add_field("Bệnh phụ", "benh_phu")

    # Ghi chú (Text area)
    tk.Label(form_frame, text="Ghi chú:", font=('Segoe UI', 10),
             bg=COLOR_BG, fg=COLOR_TEXT).grid(row=row_idx, column=0, padx=(0, 10), pady=7, sticky=tk.NE)
    txt_ghi_chu = tk.Text(form_frame, width=35, height=3, font=('Segoe UI', 10),
                          relief=tk.SOLID, bd=1)
    txt_ghi_chu.grid(row=row_idx, column=1, columnspan=2, pady=7, sticky=tk.W)
    row_idx += 1

    # ─── Pre-fill dữ liệu khi Sửa ───
    if is_edit and current_data:
        entries["ho_ten"].insert(0, current_data.get("ho_ten", ""))
        entries["tuoi"].insert(0, str(current_data.get("tuoi", "")))
        entries["gioi_tinh"].set(current_data.get("gioi_tinh", "Nam"))
        entries["sdt"].insert(0, current_data.get("sdt", ""))
        entries["dia_chi"].insert(0, current_data.get("dia_chi", ""))
        entries["chieu_cao"].insert(0, str(current_data.get("chieu_cao", "") or ""))
        entries["can_nang"].insert(0, str(current_data.get("can_nang", "") or ""))
        entries["ngay_tiep_nhan"].insert(0, current_data.get("ngay_tiep_nhan", ""))
        entries["benh_chinh"].insert(0, current_data.get("benh_chinh", ""))
        entries["benh_phu"].insert(0, current_data.get("benh_phu", ""))
        txt_ghi_chu.insert("1.0", current_data.get("ghi_chu", ""))
        update_bmi()

    # Set ngày tiếp nhận mặc định = hôm nay khi Thêm mới
    if not is_edit:
        entries["ngay_tiep_nhan"].insert(0, datetime.now().strftime("%d/%m/%Y"))

    # ─── Buttons ───
    btn_frame = tk.Frame(form_frame, bg=COLOR_BG)
    btn_frame.grid(row=row_idx, column=0, columnspan=3, pady=(15, 5))

    def on_luu():
        # Lấy dữ liệu
        ho_ten = entries["ho_ten"].get().strip()
        tuoi_str = entries["tuoi"].get().strip()
        gioi_tinh = entries["gioi_tinh"].get()
        sdt = entries["sdt"].get().strip()
        dia_chi = entries["dia_chi"].get().strip()
        chieu_cao_str = entries["chieu_cao"].get().strip()
        can_nang_str = entries["can_nang"].get().strip()
        ngay_tiep_nhan = entries["ngay_tiep_nhan"].get().strip()
        benh_chinh = entries["benh_chinh"].get().strip()
        benh_phu = entries["benh_phu"].get().strip()
        ghi_chu = txt_ghi_chu.get("1.0", tk.END).strip()

        # ── Validation ──
        if not ho_ten:
            messagebox.showwarning("Lỗi", "Mời bạn nhập Họ tên bệnh nhân!", parent=top)
            entries["ho_ten"].focus_set()
            return

        ok_tuoi, tuoi = kiem_tra_tuoi(tuoi_str)
        if not ok_tuoi:
            messagebox.showwarning("Lỗi", "Mời bạn nhập lại số tuổi (0-150)!", parent=top)
            entries["tuoi"].focus_set()
            return

        if sdt and not kiem_tra_sdt(sdt):
            messagebox.showwarning("Lỗi", "Số điện thoại không hợp lệ!\nĐịnh dạng: 0xxxxxxxxx hoặc +84xxxxxxxxx", parent=top)
            entries["sdt"].focus_set()
            return

        ok_cc, chieu_cao = kiem_tra_chieu_cao(chieu_cao_str)
        if not ok_cc:
            messagebox.showwarning("Lỗi", "Chiều cao không hợp lệ (20-300 cm)!", parent=top)
            entries["chieu_cao"].focus_set()
            return

        ok_cn, can_nang = kiem_tra_can_nang(can_nang_str)
        if not ok_cn:
            messagebox.showwarning("Lỗi", "Cân nặng không hợp lệ (0.5-500 kg)!", parent=top)
            entries["can_nang"].focus_set()
            return

        ok_ngay, _ = kiem_tra_ngay(ngay_tiep_nhan)
        if not ok_ngay:
            messagebox.showwarning("Lỗi", "Ngày tiếp nhận không đúng định dạng dd/mm/yyyy!", parent=top)
            entries["ngay_tiep_nhan"].focus_set()
            return

        if not benh_chinh:
            messagebox.showwarning("Lỗi", "Mời bạn nhập bệnh chính!", parent=top)
            entries["benh_chinh"].focus_set()
            return

        result.append({
            "ho_ten": ho_ten,
            "tuoi": tuoi,
            "gioi_tinh": gioi_tinh,
            "sdt": sdt,
            "dia_chi": dia_chi,
            "chieu_cao": chieu_cao,
            "can_nang": can_nang,
            "ngay_tiep_nhan": ngay_tiep_nhan,
            "benh_chinh": benh_chinh,
            "benh_phu": benh_phu,
            "ghi_chu": ghi_chu
        })
        top.destroy()

    btn_luu = tk.Button(
        btn_frame, text="💾 Lưu", font=('Segoe UI', 11, 'bold'),
        bg=COLOR_SUCCESS, fg=COLOR_WHITE, bd=0, padx=25, pady=8,
        command=on_luu, cursor="hand2"
    )
    btn_luu.pack(side=tk.LEFT, padx=10)

    btn_huy = tk.Button(
        btn_frame, text="❌ Hủy", font=('Segoe UI', 11),
        bg="#9E9E9E", fg=COLOR_WHITE, bd=0, padx=25, pady=8,
        command=top.destroy, cursor="hand2"
    )
    btn_huy.pack(side=tk.LEFT, padx=10)

    # Canh giữa popup
    top.update_idletasks()
    x = parent_root.winfo_x() + (parent_root.winfo_width() - top.winfo_reqwidth()) // 2
    y = parent_root.winfo_y() + (parent_root.winfo_height() - top.winfo_reqheight()) // 2
    top.geometry(f"+{x}+{y}")

    top.wait_window()
    return result[0] if result else None
