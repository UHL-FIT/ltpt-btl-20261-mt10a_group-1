"""
VIEW: Tab Thống Kê & Báo Cáo
Nhận dict dữ liệu từ Controller → vẽ biểu đồ và cập nhật nhãn.
Không tự truy vấn database.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Tahoma', 'DejaVu Sans']


class StatsView(ttk.Frame):
    """
    Frame chứa toàn bộ Tab 2.
    Expose ra bên ngoài:
      - on_refresh: callback khi nhấn "Làm mới"
      - update(stats_dict): Controller gọi để đẩy dữ liệu mới vào
      - on_export_png: callback khi nhấn xuất PNG
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.on_refresh    = None
        self.on_export_png = None
        self._current_fig  = None
        self._current_canvas = None
        self._build()

    # ------------------------------------------------------------------
    # Xây dựng giao diện
    # ------------------------------------------------------------------
    def _build(self):
        # Cột trái: chữ số
        text_frame = ttk.LabelFrame(self, text="Báo Cáo Số Liệu", padding=20)
        text_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(text_frame, text="TỔNG QUAN PHÒNG KHÁM", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0, 20))

        self.lbl_total   = ttk.Label(text_frame, text="Tổng số hồ sơ: 0",        font=("Arial", 11))
        self.lbl_today   = ttk.Label(text_frame, text="Bệnh nhân hôm nay: 0",    font=("Arial", 11, "bold"), foreground="blue")
        self.lbl_diseases = ttk.Label(text_frame, text="",                        font=("Arial", 11), justify=tk.LEFT)

        self.lbl_total.pack(anchor=tk.W, pady=5)
        self.lbl_today.pack(anchor=tk.W, pady=5)

        ttk.Label(text_frame, text="-" * 30).pack(anchor=tk.W, pady=10)
        ttk.Label(text_frame, text="Top Bệnh Lý Phổ Biến:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.lbl_diseases.pack(anchor=tk.W, pady=5)

        ttk.Button(text_frame, text="Làm mới dữ liệu",      command=lambda: self.on_refresh and self.on_refresh()).pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        ttk.Button(text_frame, text="Xuất biểu đồ PNG",  command=self._fire_export_png).pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 5))

        # Cột phải: biểu đồ
        self.chart_frame = ttk.LabelFrame(self, text="Biểu Đồ Trực Quan", padding=10)
        self.chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ------------------------------------------------------------------
    # API cho Controller gọi
    # ------------------------------------------------------------------
    def update(self, stats: dict):
        """
        Controller gọi hàm này sau khi lấy dữ liệu từ Model.
        stats = {"total", "today", "gender_data", "disease_data"}
        """
        self.lbl_total.config(text=f"Tổng số hồ sơ: {stats['total']}")
        self.lbl_today.config(text=f"Bệnh nhân hôm nay: {stats['today']}")

        disease_text = ""
        for i, (disease, count) in enumerate(stats["disease_data"], 1):
            disease_text += f"{i}. {disease} ({count} ca)\n"
        self.lbl_diseases.config(text=disease_text or "Chưa có dữ liệu.")

        self._draw_charts(stats["gender_data"], stats["disease_data"])

    def _draw_charts(self, gender_data: list, disease_data: list):
        # Hủy canvas cũ để tránh rò rỉ bộ nhớ
        if self._current_canvas:
            self._current_canvas.get_tk_widget().destroy()
            plt.close(self._current_fig)

        self._current_fig = plt.Figure(figsize=(8, 4), dpi=100)

        # Biểu đồ tròn – Giới tính
        ax1 = self._current_fig.add_subplot(121)
        if gender_data:
            labels = [str(r[0]) for r in gender_data if r[0]]
            sizes  = [r[1]      for r in gender_data if r[0]]
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                    colors=['#66b3ff', '#ff9999', '#99ff99'])
            ax1.set_title("Tỉ Lệ Giới Tính")
        else:
            ax1.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center')

        # Biểu đồ ngang – Top bệnh
        ax2 = self._current_fig.add_subplot(122)
        if disease_data:
            d_labels = [str(r[0])[:15] + ('...' if len(str(r[0])) > 15 else '') for r in disease_data]
            d_sizes  = [r[1] for r in disease_data]
            d_labels.reverse(); d_sizes.reverse()

            bars = ax2.barh(d_labels, d_sizes, color='#ffcc99')
            ax2.set_title("Top 5 Bệnh Chính")
            ax2.set_xlabel("Số ca")
            for bar in bars:
                ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                         f'{int(bar.get_width())}', va='center')
        else:
            ax2.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center')

        self._current_fig.tight_layout()

        self._current_canvas = FigureCanvasTkAgg(self._current_fig, master=self.chart_frame)
        self._current_canvas.draw()
        self._current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Callback
    # ------------------------------------------------------------------
    def _fire_export_png(self):
        if not self._current_fig:
            messagebox.showwarning("Lỗi", "Biểu đồ chưa được vẽ!")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            title="Lưu biểu đồ thống kê"
        )
        if file_path:
            try:
                self._current_fig.savefig(file_path, bbox_inches='tight')
                messagebox.showinfo("Thành công", f"Đã xuất biểu đồ:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

        if self.on_export_png:
            self.on_export_png(self._current_fig)
