"""
VIEW: Tab Lịch Tái Khám
Chỉ biết cách VẼ giao diện. Không chứa logic xử lý.
Mọi hành động người dùng → gọi callback do Controller cung cấp.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date, timedelta


# Nhãn định kì
FREQUENCY_OPTIONS = ["Hàng tuần", "Hàng tháng", "Hàng năm"]

# Màu trạng thái (sẽ được ghi đè theo theme)
_STATUS_COLORS = {
    "overdue":  {"light": "#c0392b", "dark": "#e74c3c"},
    "today":    {"light": "#d35400", "dark": "#e67e22"},
    "upcoming": {"light": "#27ae60", "dark": "#2ecc71"},
}


def _days_label(days: int) -> str:
    if days < 0:
        return f"Quá {-days} ngày"
    if days == 0:
        return "Hôm nay"
    return f"Còn {days} ngày"


def _status_label(days: int) -> str:
    if days < 0:
        return "⚠ Quá hạn"
    if days == 0:
        return "🔔 Hôm nay"
    return "✓ Chờ khám"


def _status_tag(days: int) -> str:
    if days < 0:
        return "overdue"
    if days == 0:
        return "today"
    return "upcoming"


class FollowUpView(ttk.Frame):
    """
    Frame chứa toàn bộ Tab Lịch Tái Khám.
    Expose ra bên ngoài:
      - on_save, on_delete, on_search, on_clear_search  (callback slots)
      - refresh_list(rows)  – Controller gọi để cập nhật danh sách
      - apply_theme(colors) – ThemeManager gọi khi đổi theme
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.on_save         = None
        self.on_delete       = None
        self.on_search       = None
        self.on_clear_search = None
        self.on_lookup_id    = None   # tra cứu tên khi nhập ID

        self._is_dark = False
        self._build()

    # ------------------------------------------------------------------
    # Xây dựng giao diện
    # ------------------------------------------------------------------
    def _build(self):
        # ── Panel trái: Form nhập lịch ──────────────────────────────────
        self._left = ttk.LabelFrame(self, text="Thêm Lịch Tái Khám", padding=(20, 15))
        self._left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # ── Panel phải: Danh sách ────────────────────────────────────────
        right = ttk.LabelFrame(self, text="Danh Sách Lịch Tái Khám", padding=(10, 10))
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_form(self._left)
        self._build_summary(self._left)
        self._build_list(right)

    # ── Form ────────────────────────────────────────────────────────────
    def _build_form(self, parent):
        # ID bệnh nhân + nút tra cứu
        ttk.Label(parent, text="ID Bệnh nhân:").grid(
            row=0, column=0, sticky=tk.W, pady=6)
        id_frame = ttk.Frame(parent)
        id_frame.grid(row=0, column=1, sticky=tk.W, pady=6, padx=(5, 0))

        self.entry_patient_id = ttk.Entry(id_frame, width=10)
        self.entry_patient_id.pack(side=tk.LEFT)
        ttk.Button(id_frame, text="Tra cứu",
                   command=self._fire_lookup_id).pack(side=tk.LEFT, padx=(6, 0))

        # Nhãn tên bệnh nhân (hiển thị sau khi tra cứu)
        self.lbl_patient_name = ttk.Label(parent, text="",
                                          font=("TkDefaultFont", 9, "italic"),
                                          foreground="#0078d4")
        self.lbl_patient_name.grid(row=1, column=0, columnspan=2,
                                   sticky=tk.W, pady=(0, 6), padx=(0, 0))

        # Ngày tái khám
        ttk.Label(parent, text="Ngày tái khám:").grid(
            row=2, column=0, sticky=tk.W, pady=6)
        date_frame = ttk.Frame(parent)
        date_frame.grid(row=2, column=1, sticky=tk.W, pady=6, padx=(5, 0))

        self.entry_date = ttk.Entry(date_frame, width=14)
        self.entry_date.pack(side=tk.LEFT)
        # Gợi ý format
        ttk.Label(date_frame, text="(YYYY-MM-DD)",
                  foreground="gray", font=("TkDefaultFont", 8)).pack(
            side=tk.LEFT, padx=(4, 0))

        # Nút tắt nhanh
        shortcut_frame = ttk.Frame(parent)
        shortcut_frame.grid(row=3, column=0, columnspan=2,
                            sticky=tk.W, pady=(0, 8), padx=(0, 0))
        ttk.Label(shortcut_frame, text="Nhanh:").pack(side=tk.LEFT)
        for label, delta in [("+ 1 tuần", 7), ("+ 1 tháng", 30), ("+ 3 tháng", 90)]:
            ttk.Button(shortcut_frame, text=label,
                       command=lambda d=delta: self._set_date_offset(d)).pack(
                side=tk.LEFT, padx=3)

        # Lí do
        ttk.Label(parent, text="Lí do tái khám:").grid(
            row=4, column=0, sticky=tk.NW, pady=6)
        self.text_reason = tk.Text(parent, width=28, height=5,
                                   font=("TkDefaultFont", 10))
        self.text_reason.grid(row=4, column=1, pady=6, padx=(5, 0))

        # Định kì
        ttk.Label(parent, text="Định kì:").grid(
            row=5, column=0, sticky=tk.W, pady=6)
        self.combo_freq = ttk.Combobox(parent, values=FREQUENCY_OPTIONS,
                                       width=25, state="readonly")
        self.combo_freq.current(1)   # mặc định "Hàng tháng"
        self.combo_freq.grid(row=5, column=1, pady=6, padx=(5, 0))

        # Nút bấm
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(18, 6))
        ttk.Button(btn_frame, text="💾 Lưu Lịch",
                   command=self._fire_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Làm Mới",
                   command=self.clear_form).pack(side=tk.LEFT, padx=5)

    # ── Bảng tóm tắt nhỏ ────────────────────────────────────────────────
    def _build_summary(self, parent):
        sep = ttk.Separator(parent, orient=tk.HORIZONTAL)
        sep.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=(12, 8))

        ttk.Label(parent, text="Tổng quan hôm nay",
                  font=("TkDefaultFont", 10, "bold")).grid(
            row=8, column=0, columnspan=2, sticky=tk.W, pady=(0, 6))

        self.lbl_sum_total   = ttk.Label(parent, text="Tổng lịch: 0")
        self.lbl_sum_today   = ttk.Label(parent, text="Hôm nay: 0",
                                         font=("TkDefaultFont", 10, "bold"),
                                         foreground="#0078d4")
        self.lbl_sum_overdue = ttk.Label(parent, text="Quá hạn: 0",
                                         foreground="#c0392b")
        self.lbl_sum_upcoming = ttk.Label(parent, text="Sắp tới: 0",
                                          foreground="#27ae60")

        for i, lbl in enumerate([self.lbl_sum_total, self.lbl_sum_today,
                                  self.lbl_sum_overdue, self.lbl_sum_upcoming]):
            lbl.grid(row=9 + i, column=0, columnspan=2, sticky=tk.W, pady=2)

    # ── Danh sách ───────────────────────────────────────────────────────
    def _build_list(self, parent):
        # Thanh tìm kiếm
        search_frame = ttk.Frame(parent)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 8))

        ttk.Label(search_frame, text="Tìm kiếm (Tên/SĐT/ID):").pack(
            side=tk.LEFT, padx=(0, 5))
        self.entry_search = ttk.Entry(search_frame, width=28)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        self.entry_search.bind("<Return>", lambda e: self._fire_search())
        ttk.Button(search_frame, text="Tìm",
                   command=self._fire_search).pack(side=tk.LEFT, padx=3)
        ttk.Button(search_frame, text="Xóa bộ lọc",
                   command=self._fire_clear_search).pack(side=tk.LEFT, padx=3)
        ttk.Label(search_frame,
                  text="(Nháy đúp để xóa lịch đã chọn)",
                  foreground="gray").pack(side=tk.RIGHT)

        # Bảng dữ liệu
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        cols = ("fu_id", "patient_id", "name", "phone",
                "appt_date", "reason", "days_left", "frequency", "status")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", selectmode="browse")

        headers = {
            "fu_id":      "#",
            "patient_id": "ID BN",
            "name":       "Họ tên",
            "phone":      "Số điện thoại",
            "appt_date":  "Ngày tái khám",
            "reason":     "Lí do",
            "days_left":  "Còn lại",
            "frequency":  "Định kì",
            "status":     "Trạng thái",
        }
        widths = {
            "fu_id":      40,
            "patient_id": 55,
            "name":       140,
            "phone":      100,
            "appt_date":  105,
            "reason":     160,
            "days_left":  80,
            "frequency":  90,
            "status":     100,
        }
        center_cols = {"fu_id", "patient_id", "appt_date",
                       "days_left", "frequency", "status"}

        for col in cols:
            self.tree.heading(col, text=headers[col])
            anchor = tk.CENTER if col in center_cols else tk.W
            self.tree.column(col, width=widths[col], anchor=anchor,
                             minwidth=30)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL,
                            command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Màu tag mặc định
        self._apply_tree_tags(dark=False)

        # Nút xóa
        action_frame = ttk.Frame(parent)
        action_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))
        ttk.Button(action_frame, text="🗑 Xóa Lịch Đã Chọn",
                   command=self._fire_delete).pack(side=tk.RIGHT, padx=5)

        self.tree.bind("<Double-1>", lambda e: self._fire_delete())

    # ------------------------------------------------------------------
    # Callback fires
    # ------------------------------------------------------------------
    def _fire_save(self):
        if self.on_save:
            self.on_save(self.get_form_data())

    def _fire_delete(self):
        fid = self.get_selected_follow_up_id()
        if fid is not None and self.on_delete:
            self.on_delete(fid)

    def _fire_search(self):
        if self.on_search:
            self.on_search(self.entry_search.get())

    def _fire_clear_search(self):
        self.entry_search.delete(0, tk.END)
        if self.on_clear_search:
            self.on_clear_search()

    def _fire_lookup_id(self):
        if self.on_lookup_id:
            self.on_lookup_id(self.entry_patient_id.get().strip())

    # ------------------------------------------------------------------
    # Tiện ích
    # ------------------------------------------------------------------
    def _set_date_offset(self, days: int):
        """Đặt nhanh ngày tái khám = hôm nay + N ngày."""
        target = date.today() + timedelta(days=days)
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, target.strftime("%Y-%m-%d"))

    def _apply_tree_tags(self, dark: bool):
        mode = "dark" if dark else "light"
        self.tree.tag_configure(
            "overdue",  foreground=_STATUS_COLORS["overdue"][mode])
        self.tree.tag_configure(
            "today",    foreground=_STATUS_COLORS["today"][mode],
            font=("TkDefaultFont", 10, "bold"))
        self.tree.tag_configure(
            "upcoming", foreground=_STATUS_COLORS["upcoming"][mode])

    # ------------------------------------------------------------------
    # API công khai
    # ------------------------------------------------------------------
    def get_form_data(self) -> dict:
        return {
            "patient_id":       self.entry_patient_id.get().strip(),
            "appointment_date": self.entry_date.get().strip(),
            "reason":           self.text_reason.get("1.0", tk.END).strip(),
            "frequency":        self.combo_freq.get(),
        }

    def get_selected_follow_up_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            return None
        return int(selected[0])

    def set_patient_name_label(self, name: str | None):
        """Controller gọi để hiển thị tên sau tra cứu ID."""
        if name:
            self.lbl_patient_name.config(
                text=f"  → {name}", foreground="#0078d4")
        else:
            self.lbl_patient_name.config(
                text="  → Không tìm thấy bệnh nhân", foreground="#c0392b")

    def clear_form(self):
        self.entry_patient_id.delete(0, tk.END)
        self.lbl_patient_name.config(text="")
        self.entry_date.delete(0, tk.END)
        self.text_reason.delete("1.0", tk.END)
        self.combo_freq.current(1)

    def refresh_list(self, rows: list[tuple]):
        """
        rows: mỗi phần tử là tuple
              (fu_id, patient_id, name, phone, appt_date,
               reason, frequency, days_remaining)
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            fu_id, pid, name, phone, appt_date, reason, freq, days = row
            tag = _status_tag(days)
            values = (
                fu_id,
                pid,
                name or "",
                phone or "",
                appt_date or "",
                (reason or "")[:40],
                _days_label(days),
                freq or "",
                _status_label(days),
            )
            self.tree.insert("", tk.END, iid=fu_id, values=values, tags=(tag,))

    def update_summary(self, stats: dict):
        """Controller gọi để cập nhật bảng tóm tắt bên trái."""
        self.lbl_sum_total.config(text=f"Tổng lịch: {stats.get('total', 0)}")
        self.lbl_sum_today.config(text=f"Hôm nay: {stats.get('today', 0)}")
        self.lbl_sum_overdue.config(text=f"Quá hạn: {stats.get('overdue', 0)}")
        self.lbl_sum_upcoming.config(text=f"Sắp tới: {stats.get('upcoming', 0)}")

    def apply_theme(self, colors: dict):
        """ThemeManager gọi khi đổi theme."""
        is_dark = colors.get('bg', '#f0f0f0') < '#888888'
        self._is_dark = is_dark

        self.text_reason.configure(
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            insertbackground=colors['insert_color'],
            selectbackground=colors['select_bg'],
            selectforeground=colors['select_fg'],
        )
        self._apply_tree_tags(dark=is_dark)

        highlight = '#5ab4ff' if is_dark else '#0078d4'
        overdue   = '#e74c3c' if is_dark else '#c0392b'
        upcoming  = '#2ecc71' if is_dark else '#27ae60'

        self.lbl_sum_today.config(foreground=highlight)
        self.lbl_sum_overdue.config(foreground=overdue)
        self.lbl_sum_upcoming.config(foreground=upcoming)
        self.lbl_patient_name.config(foreground=highlight)
