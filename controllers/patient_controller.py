"""
CONTROLLER - Cầu nối Model ↔ View
Chứa toàn bộ logic nghiệp vụ:
  - Nhận sự kiện từ View
  - Gọi Model để lấy/lưu dữ liệu
  - Trả kết quả về View
Controller không biết SQL, không biết tkinter widget cụ thể.
"""
import csv
import shutil
import os
from datetime import datetime
from tkinter import messagebox, filedialog

from models.patient_model import PatientModel
from views.manage_view    import ManageView
from views.stats_view     import StatsView
from views.follow_up_view    import FollowUpView


class PatientController:
    """
    Nhận cả 3 View vào constructor để có thể điều phối giữa chúng.
    Ví dụ: khi lưu bệnh nhân → cập nhật cả tab thống kê nếu đang mở.
    """

    def __init__(self, model: PatientModel, manage_view: ManageView,
                 stats_view: StatsView, follow_up_view: FollowUpView, root):
        self.model        = model
        self.manage_view  = manage_view
        self.stats_view   = stats_view
        self.follow_up_view  = follow_up_view        
        self.root         = root

        self._bind_events()
        self.load_patients()  # Tải dữ liệu ban đầu khi khởi động

    # ------------------------------------------------------------------
    # Kết nối callback: View gọi phương thức nào của Controller?
    # ------------------------------------------------------------------
    def _bind_events(self):
        mv = self.manage_view
        mv.on_save         = self.save_patient
        mv.on_delete       = self.delete_patient
        mv.on_edit         = self.prepare_edit_patient # cho nút Sửa
        mv.on_search       = self.load_patients
        mv.on_clear_search = self.load_patients       # gọi không tham số → load tất cả
        mv.on_export_csv   = self.export_csv
        mv.on_double_click = self.show_detail

        sv = self.stats_view
        sv.on_refresh = self.load_statistics

        fv = self.follow_up_view
        fv.on_save         = self.save_follow_up
        fv.on_delete       = self.delete_follow_up
        fv.on_search       = self.load_follow_ups
        fv.on_clear_search = self.load_follow_ups
        fv.on_lookup_id    = self.lookup_patient_name

    # Gioi thieu 
    def show_about(self):
        about_text = (
            "Hệ Thống Quản Lý Hồ Sơ Bệnh Nhân\n"
            "Phiên bản: alpha 0.2\n"
            "Kiến trúc: MVC (Model-View-Controller)\n\n"
            "Phần mềm hỗ trợ bác sĩ lưu trữ, tìm kiếm và thống kê bệnh án nhanh chóng."
        )
        messagebox.showinfo("Giới thiệu phần mềm", about_text)

    # ------------------------------------------------------------------
    # Xử lý nghiệp vụ – Quản lý bệnh nhân
    # ------------------------------------------------------------------
    
    def export_database(self):
        """Sao lưu file .db ra một nơi khác an toàn"""
        dest_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db")],
            title="Lưu bản sao lưu Database",
            initialfile=f"backup_patients_{datetime.now().strftime('%Y%m%d')}.db"
        )
        if dest_path:
            try:
                # Copy file từ model.db_name sang đường dẫn mới
                shutil.copy2(self.model.db_name, dest_path)
                messagebox.showinfo("Thành công", f"Đã sao lưu Database ra:\n{dest_path}")
            except Exception as e:
                messagebox.showerror("Lỗi sao lưu", f"Không thể xuất DB: {e}")

    def import_database(self):
        """Phục hồi dữ liệu từ file .db khác"""
        src_path = filedialog.askopenfilename(
            filetypes=[("SQLite Database", "*.db")],
            title="Chọn file Database để phục hồi"
        )
        if src_path:
            confirm = messagebox.askyesno(
                "Cảnh báo nguy hiểm", 
                "Việc nhập Database sẽ GHI ĐÈ và XÓA TOÀN BỘ dữ liệu hiện tại.\nBạn có chắc chắn muốn tiếp tục?"
            )
            if confirm:
                try:
                    # Ghi đè file DB cũ bằng file mới
                    shutil.copy2(src_path, self.model.db_name)
                    self.load_patients() # Tải lại danh sách
                    self.load_follow_ups()
                    if self.stats_view.winfo_ismapped():
                        self.load_statistics() # Tải lại thống kê nếu đang mở
                    messagebox.showinfo("Thành công", "Đã phục hồi Database thành công!")
                except Exception as e:
                    messagebox.showerror("Lỗi phục hồi", f"Không thể nhập DB: {e}")            
    
    def load_patients(self, query: str = ""):
        rows = self.model.search_patients(query)
        self.manage_view.refresh_list(rows)

    def prepare_edit_patient(self):
        """Lấy dữ liệu người đang chọn và đẩy lên Form để bác sĩ sửa"""
        patient_id = self.manage_view.get_selected_patient_id() # Gói gọn việc lấy ID bên View
        if not patient_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một hồ sơ để sửa!")
            return
            
        patient_data = self.model.get_patient_by_id(patient_id)
        if patient_data:
            # Ra lệnh cho View đẩy data lên Form
            self.manage_view.fill_form_for_edit(patient_id, patient_data)
        

    def save_patient(self, data: dict):
        # Validate bắt buộc
        if not data["name"] or not data["age"] or not data["primary_disease"]:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập ít nhất Họ tên, Tuổi và Bệnh chính!")
            return

        # Validate chiều cao / cân nặng (tuỳ chọn, nhưng nếu nhập phải là số)
        height = None
        weight = None
        try:
            if data["height"]:
                height = float(data["height"])
                if height <= 0 or height > 300:
                    raise ValueError
        except ValueError:
            messagebox.showwarning("Chiều cao không hợp lệ", "Chiều cao phải là số dương (cm), ví dụ: 170")
            return
        try:
            if data["weight"]:
                weight = float(data["weight"])
                if weight <= 0 or weight > 500:
                    raise ValueError
        except ValueError:
            messagebox.showwarning("Cân nặng không hợp lệ", "Cân nặng phải là số dương (kg), ví dụ: 65")
            return

        try:
            editing_id = self.manage_view.current_editing_id

            if editing_id:
                update_tuple = (
                    data["name"], data["age"], data["gender"], data["phone"],
                    data["receive_time"], data["primary_disease"],
                    data["history"], height, weight, editing_id
                )
                self.model.update_patient(editing_id, update_tuple)
                messagebox.showinfo("Thành công", f"Đã cập nhật hồ sơ: {data['name']}")
            else:
                insert_tuple = (
                    data["name"], data["age"], data["gender"], data["phone"],
                    data["receive_time"], data["primary_disease"],
                    data["history"], height, weight
                )
                self.model.add_patient(insert_tuple)
                messagebox.showinfo("Thành công", f"Đã thêm hồ sơ mới: {data['name']}")

            self.load_patients()
            self.manage_view.clear_form()

        except Exception as e:
            messagebox.showerror("Lỗi CSDL", str(e))


    def delete_patient(self, patient_id: int):
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            "Bạn có chắc chắn muốn xóa hồ sơ này?\nHành động này không thể hoàn tác."
        )
        if confirm:
            try:
                self.model.delete_patient(patient_id)
                self.load_patients()
                messagebox.showinfo("Thành công", "Đã xóa hồ sơ bệnh nhân.")
            except Exception as e:
                messagebox.showerror("Lỗi CSDL", str(e))

    def show_detail(self, patient_id: int):
        patient = self.model.get_patient_by_id(patient_id)
        if patient:
            self.manage_view.show_detail_popup(patient, self.root)

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Chọn vị trí lưu danh sách bệnh nhân"
        )
        if not file_path:
            return
        try:
            rows = self.model.export_all()
            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["Họ tên", "Tuổi", "Giới tính", "Số điện thoại",
                                  "Thời gian nhận", "Bệnh chính", "Lịch sử khám",
                                  "Chiều cao (cm)", "Cân nặng (kg)"])
                writer.writerows(rows)
            messagebox.showinfo("Thành công", f"Đã xuất file:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi Xuất File", str(e))

    # ------------------------------------------------------------------
    # Xử lý nghiệp vụ – Thống kê
    # ------------------------------------------------------------------
    def load_statistics(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        try:
            stats = self.model.get_statistics(today_str)
            self.stats_view.update(stats)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải thống kê: {e}")


    # ------------------------------------------------------------------
    # Lịch Tái Khám
    # ------------------------------------------------------------------
    def load_follow_ups(self, search: str = ""):
        """Tải danh sách lịch tái khám và cập nhật tóm tắt."""
        try:
            rows = self.model.get_follow_ups(search)
            self.follow_up_view.refresh_list(rows)
 
            stats = self.model.get_follow_up_stats()
            self.follow_up_view.update_summary(stats)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải lịch tái khám: {e}")
 
    def save_follow_up(self, data: dict):
        """Validate và lưu lịch tái khám mới."""
        if not data["patient_id"]:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập ID Bệnh nhân!")
            return
        if not data["appointment_date"]:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Ngày tái khám!")
            return
 
        # Validate patient_id là số nguyên
        try:
            patient_id = int(data["patient_id"])
        except ValueError:
            messagebox.showwarning("ID không hợp lệ", "ID Bệnh nhân phải là số nguyên!")
            return
 
        # Kiểm tra bệnh nhân tồn tại
        patient = self.model.get_patient_by_id(patient_id)
        if not patient:
            messagebox.showwarning("Không tìm thấy",
                                   f"Không có bệnh nhân với ID = {patient_id}!")
            return
 
        # Validate định dạng ngày
        try:
            datetime.strptime(data["appointment_date"], "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Ngày không hợp lệ",
                                   "Định dạng ngày phải là YYYY-MM-DD\n"
                                   "Ví dụ: 2025-12-31")
            return
 
        try:
            self.model.add_follow_up(
                patient_id=patient_id,
                appointment_date=data["appointment_date"],
                reason=data["reason"],
                frequency=data["frequency"],
            )
            messagebox.showinfo("Thành công",
                                f"Đã thêm lịch tái khám cho: {patient[1]}")
            self.follow_up_view.clear_form()
            self.load_follow_ups()
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", str(e))
 
    def delete_follow_up(self, follow_up_id: int):
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            "Bạn có chắc chắn muốn xóa lịch tái khám này?\n"
            "Hành động này không thể hoàn tác."
        )
        if confirm:
            try:
                self.model.delete_follow_up(follow_up_id)
                self.load_follow_ups()
                messagebox.showinfo("Thành công", "Đã xóa lịch tái khám.")
            except Exception as e:
                messagebox.showerror("Lỗi CSDL", str(e))
 
    def lookup_patient_name(self, id_str: str):
        """Tra cứu tên bệnh nhân theo ID để hiển thị gợi ý trong form."""
        if not id_str:
            self.follow_up_view.set_patient_name_label(None)
            return
        try:
            patient_id = int(id_str)
            name = self.model.get_patient_name_by_id(patient_id)
            self.follow_up_view.set_patient_name_label(name)
        except ValueError:
            self.follow_up_view.set_patient_name_label(None)
 