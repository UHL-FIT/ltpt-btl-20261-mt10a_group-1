"""
VIEW: Tab Quản Lý Bệnh Nhân
Chỉ biết cách VẼ giao diện. Không chứa logic xử lý.
Mọi hành động người dùng → gọi callback do Controller cung cấp.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class ManageView(ttk.Frame):
    """
    Frame chứa toàn bộ Tab 1.
    Expose ra bên ngoài:
      - Các entry/widget để Controller đọc giá trị
      - Các hàm tiện ích: clear_form(), refresh_list()
      - Các callback slot: on_save, on_delete, on_search, on_double_click
    """

    def __init__(self, parent):
        super().__init__(parent)
        # Callback slots – Controller sẽ gán hàm vào đây
        self.on_save = None
        self.on_delete = None
        self.on_edit = None
        self.on_search = None
        self.on_clear_search = None
        self.on_export_csv  = None
        self.on_double_click = None
        self.on_add_follow_up = None   # ← mới: chuyển sang tab lịch tái khám
        self.current_editing_id: int | None = None
        
        self._build()

    # ------------------------------------------------------------------
    # Xây dựng giao diện
    # ------------------------------------------------------------------
    def _build(self):
        self.left_frame = ttk.LabelFrame(self, text="Nhập Thông Tin", padding=(20, 20))
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        right = ttk.LabelFrame(self, text="Danh Sách Bệnh Nhân", padding=(10, 10))
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_form(self.left_frame)
        self._build_list(right)

    def _build_form(self, parent):
        labels = [
            "Họ và tên:", "Tuổi:", "Giới tính:", "Số điện thoại:",
            "Thời gian nhận:", "Bệnh chính:", "Bệnh phụ:",
        ]
 
        # BUG FIX: đặt tên nhất quán – dùng entry_primary / entry_secondary
        self.entry_name      = ttk.Entry(parent, width=30)
        self.entry_age       = ttk.Entry(parent, width=30)
        self.combo_gender    = ttk.Combobox(parent,
                                            values=["Nam", "Nữ", "Khác"],
                                            width=27, state="readonly")
        self.combo_gender.current(0)
        self.entry_phone     = ttk.Entry(parent, width=30)
        self.entry_time      = ttk.Entry(parent, width=30)
        self.entry_primary   = ttk.Entry(parent, width=30)   # ← tên chính xác
        self.entry_secondary = ttk.Entry(parent, width=30)   # ← tên chính xác
 
        widgets = [
            self.entry_name, self.entry_age, self.combo_gender,
            self.entry_phone, self.entry_time,
            self.entry_primary, self.entry_secondary,
        ]
 
        for i, (lbl, w) in enumerate(zip(labels, widgets)):
            ttk.Label(parent, text=lbl).grid(row=i, column=0, sticky=tk.W, pady=5)
            w.grid(row=i, column=1, pady=5, padx=(5, 0))
 
        # Giá trị mặc định cho thời gian
        self.entry_time.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))

        # Lịch sử khám
        ttk.Label(parent, text="Lịch sử khám:").grid(row=7, column=0, sticky=tk.NW, pady=5)
        self.text_history = tk.Text(parent, width=30, height=8, font=("TkDefaultFont", 10))
        self.text_history.grid(row=7, column=1, pady=5)

        # Nút bấm
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Lưu Hồ Sơ",   command=self._fire_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Làm Mới Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)


    def _build_list(self, parent):
        # Thanh tìm kiếm
        search_frame = ttk.Frame(parent)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Tìm kiếm (Tên/SĐT):").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_search = ttk.Entry(search_frame, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        self.entry_search.bind("<Return>", lambda e: self._fire_search())

        ttk.Button(search_frame, text="Tìm",          command=self._fire_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Xóa bộ lọc",   command=self._fire_clear_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Xuất ra CSV",   command=lambda: self.on_export_csv and self.on_export_csv()).pack(side=tk.LEFT, padx=5)
        ttk.Label(search_frame, text="(Nháy đúp để xem chi tiết)", foreground="gray").pack(side=tk.RIGHT)

        # Nút xóa phía dưới
        action_frame = ttk.Frame(parent)
        action_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        ttk.Button(action_frame, text="Sửa Hồ Sơ Đã Chọn", command=self._on_edit_click).pack(side=tk.RIGHT, padx=5)
        ttk.Button(action_frame, text="Xóa Hồ Sơ Đã Chọn", command=self._fire_delete).pack(side=tk.RIGHT)
        ttk.Button(action_frame, text="📅 Thêm Lịch Tái Khám",
                   command=self._fire_add_follow_up).pack(side=tk.LEFT, padx=5)

        # Bảng dữ liệu
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        cols = ("id", "name", "age", "gender", "time", "primary", "secondary")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

        headers = {"id": "ID", "name": "Họ tên", "age": "Tuổi", "gender": "Giới tính",
                   "time": "Thời gian nhận", "primary": "Bệnh chính", "secondary": "Bệnh phụ"}
        widths  = {"id": 45, "name": 150, "age": 50, "gender": 80, "time": 120, "primary": 150, "secondary": 150}

        for col in cols:
            self.tree.heading(col, text=headers[col])
            anchor = tk.CENTER if col in ("id", "age", "gender", "time") else tk.W
            self.tree.column(col, width=widths[col], anchor=anchor, minwidth=30)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda e: self._fire_double_click())

    # ------------------------------------------------------------------
    # Giao tiếp với Controller (fire callbacks)
    # ------------------------------------------------------------------
    def _fire_save(self):
        if self.on_save:
            self.on_save(self.get_form_data())

    def _fire_delete(self):
        pid = self.get_selected_patient_id()
        if pid is None:
            return
        if self.on_delete:
            self.on_delete(pid)

    def _fire_search(self):
        if self.on_search:
            self.on_search(self.entry_search.get())

    def _fire_clear_search(self):
        self.entry_search.delete(0, tk.END)
        if self.on_clear_search:
            self.on_clear_search()

    def _fire_double_click(self):
        pid = self.get_selected_patient_id()
        if pid is not None and self.on_double_click:
            self.on_double_click(pid)

    def _on_edit_click(self):
        if self.on_edit:
            self.on_edit()

    def _fire_add_follow_up(self):
        pid = self.get_selected_patient_id()
        if pid is None:
            from tkinter import messagebox
            messagebox.showwarning("Chưa chọn bệnh nhân", "Vui lòng chọn một bệnh nhân trước!")
            return
        if self.on_add_follow_up:
            self.on_add_follow_up(pid)

    def refresh_list(self, rows: list[tuple]):
        """Cập nhật danh sách bệnh nhân trên bảng (Treeview)"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            # row: (id, name, age, gender, receive_time, primary_disease, secondary_disease)
            patient_id = row[0]
            display_values = (patient_id,) + row[1:]  # Hiển thị cả ID ở cột đầu

            self.tree.insert("", tk.END, iid=patient_id, values=display_values)

    def fill_form_for_edit(self, patient_id: int, patient_data: tuple):
        """
        BUG FIX #3: dùng đúng tên attribute (entry_primary / entry_secondary).
        patient_data = (id, name, age, gender, phone, receive_time,
                        primary_disease, secondary_disease, history)
        """
        self.clear_form()
        self.current_editing_id = patient_id
        self.left_frame.config(text="✏️ Đang Sửa Hồ Sơ Bệnh Nhân")
 
        self.entry_name.insert(0,      patient_data[1] or "")
        self.entry_age.insert(0,       str(patient_data[2]) if patient_data[2] else "")
        self.combo_gender.set(         patient_data[3] or "Nam")
        self.entry_phone.insert(0,     patient_data[4] or "")
        self.entry_time.delete(0, tk.END)
        self.entry_time.insert(0,      patient_data[5] or "")
        self.entry_primary.insert(0,   patient_data[6] or "")    # ← tên đúng
        self.entry_secondary.insert(0, patient_data[7] or "")    # ← tên đúng
        self.text_history.insert("1.0", patient_data[8] or "")
 

    def clear_form(self):
        """Ghi đè lại clear form cũ: Xóa sạch thì cũng phải reset biến editing_id"""
        """
        BUG FIX #2: gộp hai clear_form() thành một.
        Xóa sạch form và reset trạng thái chỉnh sửa.
        """
        self.current_editing_id = None
        self.left_frame.config(text="Nhập Thông Tin Bệnh Nhân") # Trả lại tiêu đề gốc

        for attr in ("entry_name", "entry_age", "entry_phone",
                     "entry_primary", "entry_secondary"):
            getattr(self, attr).delete(0, tk.END)
        
        self.entry_name.delete(0, tk.END)
        self.entry_age.delete(0, tk.END)
        self.combo_gender.current(0)
        self.entry_phone.delete(0, tk.END)
        self.entry_time.delete(0, tk.END)
        from datetime import datetime
        self.entry_time.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.entry_primary.delete(0, tk.END)
        self.entry_secondary.delete(0, tk.END)
        self.text_history.delete("1.0", tk.END)

    # ------------------------------------------------------------------
    # API cho Controller sử dụng
    # ------------------------------------------------------------------
    def get_form_data(self) -> dict:
        return {
            "name":              self.entry_name.get().strip(),
            "age":               self.entry_age.get().strip(),
            "gender":            self.combo_gender.get(),
            "phone":             self.entry_phone.get().strip(),
            "receive_time":      self.entry_time.get().strip(),
            "primary_disease":   self.entry_primary.get().strip(),
            "secondary_disease": self.entry_secondary.get().strip(),
            "history":           self.text_history.get("1.0", tk.END).strip(),
        }

    def get_selected_patient_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            return None
        # iid được đặt bằng row[0] (patient_id), chuyển về int
        try:
            return int(selected[0])
        except ValueError:
            return None


    def show_detail_popup(self, patient: tuple, root: tk.Tk):
        """Mở cửa sổ chi tiết – View tự vẽ, không cần Controller can thiệp."""
        win = tk.Toplevel(root)
        win.title(f"Chi Tiết Hồ Sơ - {patient[1]}")
        win.geometry("500x520")
        win.wait_visibility()
        win.grab_set()

        frame = ttk.Frame(win, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"Hồ sơ: {patient[1]}", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0, 15))

        info = (
            f"Tuổi: {patient[2]}  |  Giới tính: {patient[3]}\n"
            f"Số điện thoại: {patient[4]}\n"
            f"Thời gian nhận: {patient[5]}\n\n"
            f"Bệnh chính: {patient[6]}\n"
            f"Bệnh phụ:   {patient[7]}"
        )
        ttk.Label(frame, text=info, justify=tk.LEFT).pack(anchor=tk.W)

        ttk.Label(frame, text="Lịch sử khám:", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
        history_box = tk.Text(frame, width=50, height=12, wrap=tk.WORD, font=("TkDefaultFont", 10))
        history_box.insert("1.0", patient[8] or "Không có ghi chú.")
        history_box.config(state=tk.DISABLED)
        history_box.pack(fill=tk.BOTH, expand=True)

        ttk.Button(frame, text="Đóng", command=win.destroy).pack(pady=(15, 0))

    # ── Theme support ────────────────────────────────────────────────────────
    def apply_theme(self, colors: dict):
        """
        ThemeManager gọi hàm này khi theme thay đổi.
        ttk.Style đã xử lý tất cả widget ttk.* tự động;
        ở đây chỉ cần cập nhật tk.Text (widget tk thuần không hỗ trợ ttk.Style).
        """
        self.text_history.configure(
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            insertbackground=colors['insert_color'],
            selectbackground=colors['select_bg'],
            selectforeground=colors['select_fg'],
        )        
