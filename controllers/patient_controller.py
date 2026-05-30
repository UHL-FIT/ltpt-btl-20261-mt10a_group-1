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
import threading
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
    # Async Threading Helper
    # ------------------------------------------------------------------
    def _run_async(self, task_func, on_success=None, on_error=None):
        """
        Chạy task_func trong thread nền để không đóng băng giao diện.
        - task_func: hàm chạy nền (KHÔNG thao tác widget tkinter)
        - on_success(result): gọi trên main thread khi thành công
        - on_error(exception): gọi trên main thread khi lỗi
        """
        self.root.config(cursor="wait")
        self.root.update_idletasks()

        def _worker():
            try:
                result = task_func()
                self.root.after(0, _on_done, result)
            except Exception as e:
                self.root.after(0, _on_fail, e)

        def _on_done(result):
            self.root.config(cursor="")
            if on_success:
                on_success(result)

        def _on_fail(error):
            self.root.config(cursor="")
            if on_error:
                on_error(error)
            else:
                messagebox.showerror("Lỗi", str(error))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

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
        mv.on_import_csv   = self.import_csv
        mv.on_double_click = self.show_detail

        sv = self.stats_view
        sv.on_refresh = self.load_statistics

        fv = self.follow_up_view
        fv.on_save         = self.save_follow_up
        fv.on_delete       = self.delete_follow_up
        fv.on_search       = self.load_follow_ups
        fv.on_clear_search = self.load_follow_ups
        fv.on_lookup_id    = self.lookup_patient_name
        fv.on_double_click = self.show_follow_up_detail

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
        """Sao lưu file .db ra một nơi khác an toàn (async)."""
        dest_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db")],
            title="Lưu bản sao lưu Database",
            initialfile=f"backup_patients_{datetime.now().strftime('%Y%m%d')}.db"
        )
        if not dest_path:
            return

        def task():
            import sqlite3
            src_conn = sqlite3.connect(self.model.db_name)
            dest_conn = sqlite3.connect(dest_path)
            try:
                src_conn.backup(dest_conn)
            finally:
                dest_conn.close()
                src_conn.close()
            return dest_path

        def on_success(path):
            messagebox.showinfo("Thành công", f"Đã sao lưu Database ra:\n{path}")

        self._run_async(task, on_success,
                        lambda e: messagebox.showerror("Lỗi sao lưu",
                                                       f"Không thể xuất DB: {e}"))

    def import_database(self):
        """Phục hồi dữ liệu từ file .db khác (async)."""
        src_path = filedialog.askopenfilename(
            filetypes=[("SQLite Database", "*.db")],
            title="Chọn file Database để phục hồi"
        )
        if not src_path:
            return
        confirm = messagebox.askyesno(
            "Cảnh báo nguy hiểm",
            "Việc nhập Database sẽ GHI ĐÈ và XÓA TOÀN BỘ dữ liệu hiện tại.\n"
            "Bạn có chắc chắn muốn tiếp tục?"
        )
        if not confirm:
            return

        def task():
            import sqlite3
            src_conn = sqlite3.connect(src_path)
            dest_conn = sqlite3.connect(self.model.db_name)
            try:
                src_conn.backup(dest_conn)
            finally:
                dest_conn.close()
                src_conn.close()

        def on_success(_):
            self.load_patients()
            self.load_follow_ups()
            if self.stats_view.winfo_ismapped():
                self.load_statistics()
            messagebox.showinfo("Thành công", "Đã phục hồi Database thành công!")

        self._run_async(task, on_success,
                        lambda e: messagebox.showerror("Lỗi phục hồi",
                                                       f"Không thể nhập DB: {e}"))
    
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
        """Xuất danh sách bệnh nhân ra CSV (async)."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Chọn vị trí lưu danh sách bệnh nhân"
        )
        if not file_path:
            return

        def task():
            rows = self.model.export_all()
            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["Họ tên", "Tuổi", "Giới tính", "Số điện thoại",
                                  "Thời gian nhận", "Bệnh chính", "Lịch sử khám",
                                  "Chiều cao (cm)", "Cân nặng (kg)"])
                writer.writerows(rows)
            return file_path

        def on_success(path):
            messagebox.showinfo("Thành công", f"Đã xuất file:\n{path}")

        self._run_async(task, on_success,
                        lambda e: messagebox.showerror("Lỗi Xuất File", str(e)))

    def import_csv(self):
        """Nhập danh sách bệnh nhân từ file CSV (async)."""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Chọn file CSV để nhập danh sách bệnh nhân"
        )
        if not file_path:
            return

        def task():
            with open(file_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Bỏ qua dòng tiêu đề
                count = 0
                for row in reader:
                    if len(row) < 6:
                        continue
                    name            = row[0].strip()
                    age             = row[1].strip()
                    gender          = row[2].strip()
                    phone           = row[3].strip() if len(row) > 3 else ""
                    receive_time    = row[4].strip() if len(row) > 4 else ""
                    primary_disease = row[5].strip() if len(row) > 5 else ""
                    history         = row[6].strip() if len(row) > 6 else ""
                    height = None
                    weight = None
                    try:
                        if len(row) > 7 and row[7].strip():
                            height = float(row[7].strip())
                    except ValueError:
                        pass
                    try:
                        if len(row) > 8 and row[8].strip():
                            weight = float(row[8].strip())
                    except ValueError:
                        pass

                    if name and age:
                        data = (name, age, gender, phone, receive_time,
                                primary_disease, history, height, weight)
                        self.model.add_patient(data)
                        count += 1
            return count

        def on_success(count):
            self.load_patients()
            messagebox.showinfo("Thành công",
                                f"Đã nhập {count} hồ sơ bệnh nhân từ CSV.")

        self._run_async(task, on_success,
                        lambda e: messagebox.showerror("Lỗi Nhập File", str(e)))

    # ------------------------------------------------------------------
    # Xử lý nghiệp vụ – Thống kê
    # ------------------------------------------------------------------
    def load_statistics(self):
        """Tải dữ liệu thống kê (async – query nặng + vẽ biểu đồ)."""
        today_str = datetime.now().strftime("%Y-%m-%d")

        def task():
            return self.model.get_statistics(today_str)

        def on_success(stats):
            self.stats_view.update(stats)

        self._run_async(task, on_success,
                        lambda e: messagebox.showerror("Lỗi",
                                                       f"Lỗi tải thống kê: {e}"))


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

    def show_follow_up_detail(self, follow_up_id: int):
        """Hiển thị popup chi tiết lịch tái khám."""
        data = self.model.get_follow_up_by_id(follow_up_id)
        if data:
            self.follow_up_view.show_detail_popup(data, self.root)
 
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
 