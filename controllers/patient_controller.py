"""
controllers/patient_controller.py
=================================
Controller GUI chính điều phối luồng xử lý giữa View và Model.
Quản lý toàn bộ sự kiện giao diện, navigation sidebar, và CRUD bệnh nhân.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd

from models import patient as patient_model
from models import examination as exam_model
from models import medication as med_model
import views.main_window as main_window
import views.patient_view as patient_view
import views.patient_form as patient_form
import views.examination_view as examination_view
import views.medication_view as medication_view
import views.stats_view as stats_view
from utils.logger import setup_logger

logger = setup_logger()

# Module-level state
app_root = None
app_ui = {}
app_pv = {}      # Patient view widgets
app_ev = {}      # Examination view widgets
app_mv = {}      # Medication view widgets
app_sv = {}      # Stats view widgets
current_page = "benh_nhan"


# ═══════════════════════════════════════════════════════
# NAVIGATION
# ═══════════════════════════════════════════════════════

def _clear_content():
    """Xóa nội dung trong content frame."""
    for widget in app_ui['content_frame'].winfo_children():
        widget.destroy()


def _show_page(page_key):
    """Hiển thị trang tương ứng."""
    global current_page, app_pv, app_ev, app_mv, app_sv
    current_page = page_key
    _clear_content()
    main_window.set_active_nav(app_ui, page_key)

    if page_key == "benh_nhan":
        app_pv = patient_view.tao_patient_view(app_ui['content_frame'])
        _bind_patient_events()
        _tai_du_lieu()

    elif page_key == "lich_su_kham":
        app_ev = examination_view.tao_examination_view(app_ui['content_frame'])
        _bind_exam_events()

    elif page_key == "thuoc":
        app_mv = medication_view.tao_medication_view(app_ui['content_frame'])
        _bind_med_events()

    elif page_key == "thong_ke":
        app_sv = stats_view.tao_stats_view(app_ui['content_frame'])
        _bind_stats_events()
        _refresh_stats()


# ═══════════════════════════════════════════════════════
# PATIENT PAGE
# ═══════════════════════════════════════════════════════

def _tai_du_lieu():
    """Tải và hiển thị danh sách bệnh nhân."""
    search_text = app_pv.get('ent_search')
    search_by = app_pv.get('cbo_search_by')

    keyword = search_text.get().strip() if search_text else ""
    field_map = {
        "Tất cả": "tat_ca", "Mã BN": "ma_bn", "Họ tên": "ho_ten",
        "Giới tính": "gioi_tinh", "SĐT": "sdt", "Bệnh chính": "benh_chinh"
    }
    field = field_map.get(search_by.get() if search_by else "Tất cả", "tat_ca")

    if keyword:
        df, ok = patient_model.tim_kiem(keyword, field)
    else:
        df, ok = patient_model.lay_danh_sach()

    if not ok:
        messagebox.showerror("Lỗi", "Không thể tải dữ liệu bệnh nhân!")
        return

    patient_view.hien_thi_bang(app_pv, df)

    # Cập nhật status bar
    stats = patient_model.thong_ke(df)
    main_window.cap_nhat_status_bar(app_ui, stats)


def on_them_bn():
    """Thêm bệnh nhân mới."""
    logger.info("Người dùng click Thêm Bệnh nhân.")
    data = patient_form.hien_thi_form_benh_nhan(app_root, is_edit=False)
    if data:
        ok, msg, ma_bn = patient_model.them_benh_nhan(data)
        if ok:
            messagebox.showinfo("Thành công", msg)
            _tai_du_lieu()
        else:
            messagebox.showerror("Lỗi", msg)


def on_sua_bn():
    """Sửa bệnh nhân đã chọn."""
    logger.info("Người dùng click Sửa Bệnh nhân.")
    tree = app_pv['tree']

    # Tìm các dòng được tick checkbox
    selected = []
    for item_id in tree.get_children():
        values = tree.item(item_id, 'values')
        if values[0] == "☑":
            selected.append(item_id)

    # Fallback: lấy dòng highlight
    if not selected:
        selected = list(tree.selection())

    if not selected:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn 1 bệnh nhân để sửa!")
        return

    if len(selected) > 1:
        messagebox.showwarning("Cảnh báo", "Chỉ được chọn 1 bệnh nhân để sửa thông tin!")
        return

    item = tree.item(selected[0])
    vals = item['values']
    ma_bn = vals[2]

    # Lấy dữ liệu hiện tại từ DB
    df, ok = patient_model.lay_danh_sach()
    if not ok:
        return
    row = df[df['ma_bn'] == ma_bn]
    if row.empty:
        messagebox.showerror("Lỗi", f"Không tìm thấy {ma_bn}!")
        return

    current_data = row.iloc[0].to_dict()

    data = patient_form.hien_thi_form_benh_nhan(app_root, is_edit=True, current_data=current_data)
    if data:
        ok, msg = patient_model.sua_benh_nhan(ma_bn, data)
        if ok:
            messagebox.showinfo("Thành công", msg)
            _tai_du_lieu()
        else:
            messagebox.showerror("Lỗi", msg)


def on_xoa_bn():
    """Xóa các bệnh nhân được tick chọn."""
    logger.info("Người dùng click Xóa Bệnh nhân.")
    tree = app_pv['tree']
    ma_bn_list = []

    for item_id in tree.get_children():
        values = tree.item(item_id, 'values')
        if values[0] == "☑":
            ma_bn_list.append(values[2])

    if not ma_bn_list:
        messagebox.showwarning("Cảnh báo", "Vui lòng tick chọn (☑) ít nhất 1 bệnh nhân để xóa!")
        return

    if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa {len(ma_bn_list)} bệnh nhân?\n"
                                        f"(Dữ liệu khám và thuốc liên quan cũng sẽ bị xóa)"):
        ok, msg = patient_model.xoa_nhieu_benh_nhan(ma_bn_list)
        if ok:
            messagebox.showinfo("Thành công", msg)
            _tai_du_lieu()
        else:
            messagebox.showerror("Lỗi", msg)


def on_import():
    """Import bệnh nhân từ file CSV."""
    logger.info("Người dùng click Import CSV.")
    filepath = filedialog.askopenfilename(
        title="Chọn file CSV danh sách bệnh nhân",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if not filepath:
        return

    try:
        df_import = pd.read_csv(filepath, dtype=str)
        required_cols = ["ho_ten"]
        for col in required_cols:
            if col not in df_import.columns:
                messagebox.showerror("Lỗi", f"File CSV phải có cột '{col}'.")
                return

        count = 0
        for _, row in df_import.iterrows():
            data = {
                "ho_ten": row.get("ho_ten", ""),
                "tuoi": int(row.get("tuoi", 0)) if row.get("tuoi") else None,
                "gioi_tinh": row.get("gioi_tinh", "Nam"),
                "sdt": row.get("sdt", ""),
                "dia_chi": row.get("dia_chi", ""),
                "chieu_cao": float(row.get("chieu_cao", 0)) if row.get("chieu_cao") else None,
                "can_nang": float(row.get("can_nang", 0)) if row.get("can_nang") else None,
                "ngay_tiep_nhan": row.get("ngay_tiep_nhan", ""),
                "benh_chinh": row.get("benh_chinh", ""),
                "benh_phu": row.get("benh_phu", ""),
                "ghi_chu": row.get("ghi_chu", "")
            }
            ok, _, _ = patient_model.them_benh_nhan(data)
            if ok:
                count += 1

        _tai_du_lieu()
        messagebox.showinfo("Thành công", f"Đã import {count} bệnh nhân từ file.")
    except Exception as e:
        logger.error(f"Lỗi import: {e}", exc_info=True)
        messagebox.showerror("Lỗi", f"Không thể import file: {e}")


def on_export():
    """Export danh sách bệnh nhân ra CSV."""
    logger.info("Người dùng click Export CSV.")
    filepath = filedialog.asksaveasfilename(
        title="Lưu file danh sách bệnh nhân",
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        initialfile="danh_sach_benh_nhan.csv"
    )
    if not filepath:
        return

    try:
        df, ok = patient_model.lay_danh_sach()
        if ok:
            export_cols = ["ma_bn", "ho_ten", "tuoi", "gioi_tinh", "sdt", "dia_chi",
                           "chieu_cao", "can_nang", "ngay_tiep_nhan", "benh_chinh", "benh_phu", "ghi_chu"]
            df[export_cols].to_csv(filepath, index=False, encoding="utf-8-sig")
            messagebox.showinfo("Thành công", f"Đã lưu tại {filepath}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")


def on_search():
    """Tìm kiếm bệnh nhân."""
    logger.info("Người dùng tìm kiếm.")
    _tai_du_lieu()


def on_clear_search():
    """Xóa bộ lọc tìm kiếm."""
    app_pv['ent_search'].delete(0, tk.END)
    app_pv['cbo_search_by'].set("Tất cả")
    _tai_du_lieu()


def on_single_click(event):
    """Xử lý click checkbox trên TreeView."""
    tree = app_pv['tree']
    region = tree.identify_region(event.x, event.y)
    column_str = tree.identify_column(event.x)

    if not column_str:
        return

    col_idx = int(column_str.replace("#", "")) - 1
    col_name = app_pv['cols'][col_idx]

    if region == "heading" and col_name == "Chọn":
        current = tree.heading("Chọn", "text")
        new_val = "☑" if "☐" in current else "☐"
        tree.heading("Chọn", text=new_val)
        for item_id in tree.get_children():
            values = list(tree.item(item_id, "values"))
            values[0] = new_val
            tree.item(item_id, values=values)
        return

    if region == "cell" and col_name == "Chọn":
        item_id = tree.identify_row(event.y)
        if item_id:
            values = list(tree.item(item_id, 'values'))
            values[0] = "☑" if values[0] == "☐" else "☐"
            tree.item(item_id, values=values)


def _bind_patient_events():
    """Gán sự kiện cho patient view."""
    app_pv['btn_them'].config(command=on_them_bn)
    app_pv['btn_sua'].config(command=on_sua_bn)
    app_pv['btn_xoa'].config(command=on_xoa_bn)
    app_pv['btn_import'].config(command=on_import)
    app_pv['btn_export'].config(command=on_export)
    app_pv['btn_search'].config(command=on_search)
    app_pv['btn_clear_search'].config(command=on_clear_search)
    app_pv['ent_search'].bind("<Return>", lambda e: on_search())
    app_pv['tree'].bind("<ButtonRelease-1>", on_single_click)


# ═══════════════════════════════════════════════════════
# EXAMINATION PAGE
# ═══════════════════════════════════════════════════════

def _load_exam_history():
    """Tải lịch sử khám cho mã BN đã nhập."""
    ma_bn = app_ev['ent_ma_bn'].get().strip().upper()
    if not ma_bn:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập Mã BN!")
        return

    # Kiểm tra BN tồn tại
    df_patients, _ = patient_model.lay_danh_sach()
    bn_row = df_patients[df_patients['ma_bn'] == ma_bn]
    if bn_row.empty:
        messagebox.showwarning("Cảnh báo", f"Không tìm thấy bệnh nhân {ma_bn}!")
        app_ev['lbl_patient_name'].config(text="")
        return

    app_ev['lbl_patient_name'].config(text=f"👤 {bn_row.iloc[0]['ho_ten']}")

    df_exam, ok = exam_model.lay_lich_su_kham(ma_bn)
    if ok:
        examination_view.hien_thi_lich_su_kham(app_ev, df_exam)


def on_them_kham():
    """Thêm lần khám mới."""
    ma_bn = app_ev['ent_ma_bn'].get().strip().upper()
    if not ma_bn:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập Mã BN trước!")
        return

    data = examination_view.hien_thi_form_kham(app_root)
    if data:
        ok, msg = exam_model.them_lan_kham(ma_bn, data)
        if ok:
            messagebox.showinfo("Thành công", msg)
            _load_exam_history()
        else:
            messagebox.showerror("Lỗi", msg)


def on_xoa_kham():
    """Xóa lần khám đã chọn."""
    tree = app_ev['tree']
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn lần khám cần xóa!")
        return

    exam_id = tree.item(selected[0], 'values')[0]
    if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa lần khám này?"):
        ok, msg = exam_model.xoa_lan_kham(exam_id)
        if ok:
            _load_exam_history()
        else:
            messagebox.showerror("Lỗi", msg)


def _bind_exam_events():
    """Gán sự kiện cho examination view."""
    app_ev['btn_load'].config(command=_load_exam_history)
    app_ev['btn_them_kham'].config(command=on_them_kham)
    app_ev['btn_xoa_kham'].config(command=on_xoa_kham)
    app_ev['ent_ma_bn'].bind("<Return>", lambda e: _load_exam_history())


# ═══════════════════════════════════════════════════════
# MEDICATION PAGE
# ═══════════════════════════════════════════════════════

def _load_med_history():
    """Tải lịch sử thuốc cho mã BN đã nhập."""
    ma_bn = app_mv['ent_ma_bn'].get().strip().upper()
    if not ma_bn:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập Mã BN!")
        return

    df_patients, _ = patient_model.lay_danh_sach()
    bn_row = df_patients[df_patients['ma_bn'] == ma_bn]
    if bn_row.empty:
        messagebox.showwarning("Cảnh báo", f"Không tìm thấy bệnh nhân {ma_bn}!")
        app_mv['lbl_patient_name'].config(text="")
        return

    app_mv['lbl_patient_name'].config(text=f"👤 {bn_row.iloc[0]['ho_ten']}")

    df_med, ok = med_model.lay_lich_su_thuoc(ma_bn)
    if ok:
        medication_view.hien_thi_lich_su_thuoc(app_mv, df_med)


def on_them_thuoc():
    """Thêm thuốc mới."""
    ma_bn = app_mv['ent_ma_bn'].get().strip().upper()
    if not ma_bn:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập Mã BN trước!")
        return

    data = medication_view.hien_thi_form_thuoc(app_root)
    if data:
        ok, msg = med_model.them_thuoc(ma_bn, data)
        if ok:
            messagebox.showinfo("Thành công", msg)
            _load_med_history()
        else:
            messagebox.showerror("Lỗi", msg)


def on_xoa_thuoc():
    """Xóa thuốc đã chọn."""
    tree = app_mv['tree']
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn thuốc cần xóa!")
        return

    med_id = tree.item(selected[0], 'values')[0]
    if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa thuốc này?"):
        ok, msg = med_model.xoa_thuoc(med_id)
        if ok:
            _load_med_history()
        else:
            messagebox.showerror("Lỗi", msg)


def _bind_med_events():
    """Gán sự kiện cho medication view."""
    app_mv['btn_load'].config(command=_load_med_history)
    app_mv['btn_them_thuoc'].config(command=on_them_thuoc)
    app_mv['btn_xoa_thuoc'].config(command=on_xoa_thuoc)
    app_mv['ent_ma_bn'].bind("<Return>", lambda e: _load_med_history())


# ═══════════════════════════════════════════════════════
# STATS PAGE
# ═══════════════════════════════════════════════════════

def _refresh_stats():
    """Làm mới biểu đồ thống kê."""
    df, ok = patient_model.lay_danh_sach()
    if ok:
        stats_view.ve_bieu_do(app_sv, df)


def _bind_stats_events():
    """Gán sự kiện cho stats view."""
    app_sv['btn_refresh'].config(command=_refresh_stats)


# ═══════════════════════════════════════════════════════
# ABOUT & MAIN
# ═══════════════════════════════════════════════════════

def on_about():
    """Hiển thị thông tin giới thiệu."""
    about_text = (
        "🏥 PHẦN MỀM: QUẢN LÝ HỒ SƠ BỆNH NHÂN\n"
        "────────────────────────────────────\n"
        "🔹 Phiên bản: 1.0.0\n"
        "🔹 Kiến trúc: MVC (Model-View-Controller)\n"
        "🔹 Công nghệ: Python, Tkinter, SQLite, Pandas\n"
        "🔹 Ngày phát hành: 13/05/2026\n"
        "────────────────────────────────────\n"
        "Phần mềm hỗ trợ quản lý hồ sơ bệnh nhân,\n"
        "lịch sử khám bệnh, thuốc và thống kê y tế."
    )
    messagebox.showinfo("Giới thiệu", about_text)


def chay_ung_dung():
    """Khởi chạy ứng dụng GUI."""
    global app_root, app_ui
    logger.info("Khởi động ứng dụng Quản lý Bệnh nhân (GUI)")

    app_root = tk.Tk()
    app_ui = main_window.tao_cua_so_chinh(app_root)

    # Bind navigation
    app_ui['nav_buttons']['benh_nhan'].config(command=lambda: _show_page("benh_nhan"))
    app_ui['nav_buttons']['lich_su_kham'].config(command=lambda: _show_page("lich_su_kham"))
    app_ui['nav_buttons']['thuoc'].config(command=lambda: _show_page("thuoc"))
    app_ui['nav_buttons']['thong_ke'].config(command=lambda: _show_page("thong_ke"))
    app_ui['btn_about'].config(command=on_about)

    # Show default page
    _show_page("benh_nhan")

    app_root.mainloop()
    logger.info("Thoát ứng dụng (GUI)")
