"""
VIEW: Tab Thống Kê & Báo Cáo
Nhận dict dữ liệu từ Controller → vẽ biểu đồ và cập nhật nhãn.
Không tự truy vấn database.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Tahoma', 'DejaVu Sans']

# Bảng màu biểu đồ mặc định (sẽ bị ghi đè bởi apply_theme)
_DEFAULT_COLORS = {
    'chart_bg':   '#f9f9f9',
    'chart_fg':   '#1a1a1a',
    'chart_grid': '#dddddd',
    'bg':         '#f0f0f0',
    'tree_bg':    '#ffffff',
    'border':     '#cccccc',
    'select_bg':  '#0078d4',
}
 
_PIE_COLORS  = ['#66b3ff', '#ff9999', '#99ff99', '#ffcc99', '#c2c2f0']
_BAR_COLOR_LIGHT = '#ffaa55'
_BAR_COLOR_DARK  = '#4a9eca'
_COLOR_MALE_L     = '#4a90d9'   # Nam  – sáng
_COLOR_FEMALE_L   = '#e87070'   # Nữ   – sáng
_COLOR_OTHER_L    = '#82c882'   # Khác – sáng
_COLOR_MALE_D     = '#6ab0f5'
_COLOR_FEMALE_D   = '#f59595'
_COLOR_OTHER_D    = '#a0d8a0'

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
        self._colors         = dict(_DEFAULT_COLORS)   # bản sao để an toàn
        self._last_stats     = None                     # cache để redraw khi đổi theme
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

        self.lbl_total   = ttk.Label(text_frame, text="Tổng số hồ sơ: 0", font=("Arial", 11))
        self.lbl_today   = ttk.Label(text_frame, text="Bệnh nhân hôm nay: 0", font=("Arial", 11, "bold"), foreground="#0078d4")
        self.lbl_diseases = ttk.Label(text_frame, text="", font=("Arial", 11), justify=tk.LEFT)

        self.lbl_total.pack(anchor=tk.W, pady=5)
        self.lbl_today.pack(anchor=tk.W, pady=5)

        ttk.Label(text_frame, text="-" * 30).pack(anchor=tk.W, pady=10)
        ttk.Label(text_frame, text="Top Bệnh Lý Phổ Biến:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.lbl_diseases.pack(anchor=tk.W, pady=5)

        # ── Bảng BMI ──────────────────────────────────────────────────────
        ttk.Label(text_frame, text="-" * 30).pack(anchor=tk.W, pady=(10, 5))
        ttk.Label(text_frame, text="Thống Kê BMI:", font=("Arial", 11, "bold")).pack(anchor=tk.W)

        bmi_tree_frame = ttk.Frame(text_frame)
        bmi_tree_frame.pack(anchor=tk.W, fill=tk.X, pady=(5, 0))

        bmi_cols = ("category", "count", "range")
        self.bmi_tree = ttk.Treeview(bmi_tree_frame, columns=bmi_cols,
                                     show="headings", height=4)
        self.bmi_tree.heading("category", text="Phân loại")
        self.bmi_tree.heading("count",    text="Số BN")
        self.bmi_tree.heading("range",    text="Chỉ số BMI")
        self.bmi_tree.column("category", width=100, anchor=tk.W)
        self.bmi_tree.column("count",    width=60,  anchor=tk.CENTER)
        self.bmi_tree.column("range",    width=110, anchor=tk.CENTER)
        self.bmi_tree.pack(side=tk.LEFT, fill=tk.X)

        # Tag màu cho từng hàng BMI
        self.bmi_tree.tag_configure("underweight", foreground="#3498db")
        self.bmi_tree.tag_configure("normal",      foreground="#27ae60")
        self.bmi_tree.tag_configure("overweight",  foreground="#e67e22")
        self.bmi_tree.tag_configure("obese",       foreground="#c0392b",
                                    font=("TkDefaultFont", 10, "bold"))

        self.lbl_bmi_note = ttk.Label(text_frame, text="",
                                      font=("Arial", 9, "italic"),
                                      foreground="gray")
        self.lbl_bmi_note.pack(anchor=tk.W, pady=(3, 0))

        ttk.Button(text_frame, text="Làm mới dữ liệu",
                   command=lambda: self.on_refresh and self.on_refresh()).pack(
            side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        ttk.Button(text_frame, text="Xuất biểu đồ PNG",
                   command=self._fire_export_png).pack(
            side=tk.BOTTOM, fill=tk.X, pady=(20, 5))

         # ── Cột phải: canvas cuộn ───────────────────────────────────────
        chart_outer = ttk.LabelFrame(self, text="Biểu Đồ Trực Quan", padding=5)
        chart_outer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollable canvas container
        self._scroll_canvas = tk.Canvas(chart_outer, highlightthickness=0)
        self._vscroll = ttk.Scrollbar(chart_outer, orient=tk.VERTICAL,
                                      command=self._scroll_canvas.yview)
        self._scroll_canvas.configure(yscrollcommand=self._vscroll.set)

        self._vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chart_frame = ttk.Frame(self._scroll_canvas)
        self._scroll_window = self._scroll_canvas.create_window(
            (0, 0), window=self.chart_frame, anchor="nw")

        self.chart_frame.bind("<Configure>", self._on_chart_frame_configure)
        self._scroll_canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse wheel scroll
        self._scroll_canvas.bind("<Enter>",  self._bind_mousewheel)
        self._scroll_canvas.bind("<Leave>",  self._unbind_mousewheel)

    def _on_chart_frame_configure(self, event):
        self._scroll_canvas.configure(
            scrollregion=self._scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self._scroll_canvas.itemconfig(self._scroll_window, width=event.width)

    def _bind_mousewheel(self, event):
        self._scroll_canvas.bind_all("<MouseWheel>",   self._on_mousewheel)
        self._scroll_canvas.bind_all("<Button-4>",     self._on_mousewheel)
        self._scroll_canvas.bind_all("<Button-5>",     self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self._scroll_canvas.unbind_all("<MouseWheel>")
        self._scroll_canvas.unbind_all("<Button-4>")
        self._scroll_canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:
            self._scroll_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._scroll_canvas.yview_scroll(1, "units")
        else:
            self._scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    # ------------------------------------------------------------------
    # API cho Controller gọi
    # ------------------------------------------------------------------
    def update(self, stats: dict):
        """
        Controller gọi hàm này sau khi lấy dữ liệu từ Model.
        stats = {"total", "today", "gender_data", "disease_data",
                 "bmi_list", "bmi_categories"}
        """
        self._last_stats = stats

        self.lbl_total.config(text=f"Tổng số hồ sơ: {stats['total']}")
        self.lbl_today.config(text=f"Bệnh nhân hôm nay: {stats['today']}")

        # Label top 10 bệnh (kèm Nam/Nữ)
        dgd = stats.get("disease_gender_data") or []
        if not dgd:
            # fallback sang disease_data cũ nếu model chưa cập nhật
            disease_text = ""
            for i, (disease, count) in enumerate(stats.get("disease_data", []), 1):
                disease_text += f"{i}. {disease} ({count} ca)\n"
            self.lbl_diseases.config(text=disease_text or "Chưa có dữ liệu.")
        else:
            lines = []
            for i, (disease, total, nam, nu, khac) in enumerate(dgd, 1):
                detail = f"Nam:{nam} / Nữ:{nu}"
                if khac:
                    detail += f" / Khác:{khac}"
                lines.append(f"{i}. {disease[:20]} ({total} ca)\n   {detail}")
            self.lbl_diseases.config(text="\n".join(lines) or "Chưa có dữ liệu.")

        self._update_bmi_table(stats.get("bmi_categories", {}),
                               stats.get("bmi_list", []))
        self._draw_charts(stats)

    def _update_bmi_table(self, categories: dict, bmi_list: list):
        for row in self.bmi_tree.get_children():
            self.bmi_tree.delete(row)

        rows = [
            ("Thiếu cân",   categories.get("Thiếu cân",   0), "< 18.5",   "underweight"),
            ("Bình thường", categories.get("Bình thường", 0), "18.5–24.9","normal"),
            ("Thừa cân",    categories.get("Thừa cân",    0), "25–29.9",  "overweight"),
            ("Béo phì",     categories.get("Béo phì",     0), "≥ 30",     "obese"),
        ]
        for cat, cnt, rng, tag in rows:
            self.bmi_tree.insert("", tk.END, values=(cat, cnt, rng), tags=(tag,))

        total_bmi = len(bmi_list)
        obese = categories.get("Béo phì", 0)
        if total_bmi > 0:
            pct = round(obese / total_bmi * 100, 1)
            self.lbl_bmi_note.config(
                text=f"Tỉ lệ béo phì: {pct}%  ({total_bmi} BN có dữ liệu)")
        else:
            self.lbl_bmi_note.config(text="Chưa có dữ liệu chiều cao/cân nặng.")

    def _draw_charts(self, stats: dict):
        # Hủy canvas cũ
        if self._current_canvas:
            self._current_canvas.get_tk_widget().destroy()
            plt.close(self._current_fig)
            self._current_canvas = None

        c   = self._colors
        cfg = c.get('chart_fg', '#1a1a1a')
        cbg = c.get('chart_bg', '#f9f9f9')
        tbg = c.get('tree_bg', '#ffffff')
        brd = c.get('border', '#cccccc')
        grd = c.get('chart_grid', '#dddddd')
        is_dark  = c.get('bg', '#f0f0f0')[1:3] < '88'
        bar_mono = _BAR_COLOR_DARK if is_dark else _BAR_COLOR_LIGHT
        c_male   = _COLOR_MALE_D   if is_dark else _COLOR_MALE_L
        c_female = _COLOR_FEMALE_D if is_dark else _COLOR_FEMALE_L
        c_other  = _COLOR_OTHER_D  if is_dark else _COLOR_OTHER_L

        # Layout: 2 hàng × 2 cột
        fig = plt.Figure(figsize=(13, 10), dpi=100, facecolor=cbg)
        self._current_fig = fig

        gs = fig.add_gridspec(2, 2, hspace=0.45, wspace=0.35,
                              left=0.08, right=0.97, top=0.94, bottom=0.07)

        ax_month_pt  = fig.add_subplot(gs[0, 0], facecolor=tbg)   # BN theo tháng
        ax_month_fu  = fig.add_subplot(gs[0, 1], facecolor=tbg)   # Tái khám theo tháng
        ax_disease   = fig.add_subplot(gs[1, 0], facecolor=tbg)   # Top 10 bệnh Nam/Nữ
        ax_bmi       = fig.add_subplot(gs[1, 1], facecolor=tbg)   # BMI

        # ── Hàng 1 trái: Số bệnh nhân nhận theo tháng ───────────────────
        monthly_pt = stats.get("monthly_patients", [])
        self._draw_monthly_bar(ax_month_pt, monthly_pt,
                               "Số Bệnh Nhân Nhận Theo Tháng",
                               bar_mono, cfg, brd, grd)

        # ── Hàng 1 phải: Số lịch tái khám theo tháng ────────────────────
        monthly_fu = stats.get("monthly_followups", [])
        self._draw_monthly_bar(ax_month_fu, monthly_fu,
                               "Số Lịch Tái Khám Theo Tháng",
                               '#7ec8a0' if not is_dark else '#50a878',
                               cfg, brd, grd)

        # ── Hàng 2 trái: Top 10 bệnh chính – stacked bar Nam/Nữ ─────────
        dgd = stats.get("disease_gender_data") or []
        self._draw_disease_gender(ax_disease, dgd, cfg, brd, c_male, c_female, c_other)

        # ── Hàng 2 phải: Phân loại BMI ───────────────────────────────────
        bmi_cats   = stats.get("bmi_categories", {})
        bmi_vals   = [bmi_cats.get(k, 0) for k in
                      ["Thiếu cân", "Bình thường", "Thừa cân", "Béo phì"]]
        bmi_labels = ["Thiếu cân", "Bình thường", "Thừa cân", "Béo phì"]
        bmi_colors = ["#3498db", "#27ae60", "#e67e22", "#c0392b"]
        if sum(bmi_vals) > 0:
            wedges, texts, autotexts = ax_bmi.pie(
                bmi_vals, labels=bmi_labels, autopct='%1.1f%%',
                startangle=90, colors=bmi_colors)
            for t in texts + autotexts:
                t.set_color(cfg)
                t.set_fontsize(8)
        else:
            ax_bmi.text(0.5, 0.5, "Chưa có dữ liệu\nchiều cao/cân nặng",
                        ha='center', va='center', color=cfg, fontsize=9)
        ax_bmi.set_title("Phân Loại BMI", color=cfg, fontsize=10, fontweight='bold')

        self._current_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self._current_canvas.draw()
        self._current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ── Helpers vẽ ──────────────────────────────────────────────────────
    def _draw_monthly_bar(self, ax, data: list, title: str,
                          color: str, cfg: str, brd: str, grd: str):
        ax.set_title(title, color=cfg, fontsize=9, fontweight='bold')
        if not data:
            ax.text(0.5, 0.5, "Chưa có dữ liệu", ha='center', va='center',
                    color=cfg, fontsize=9)
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_color(brd)
            return

        months = [r[0] for r in data]
        counts = [r[1] for r in data]

        # Rút gọn nhãn: chỉ giữ MM/YY
        short_labels = []
        for m in months:
            if not m or not isinstance(m, str):
                short_labels.append("K.Xác Định")
                continue
            parts = m.split('-')
            short_labels.append(f"{parts[1]}/{parts[0][2:]}") if len(parts) == 2 else short_labels.append(m)

        x = range(len(months))
        bars = ax.bar(x, counts, color=color, edgecolor=brd, width=0.6)
        ax.set_xticks(list(x))
        ax.set_xticklabels(short_labels, rotation=45, ha='right',
                           fontsize=7, color=cfg)
        ax.tick_params(axis='y', colors=cfg, labelsize=7)
        ax.set_ylabel("Số ca", color=cfg, fontsize=8)
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.grid(axis='y', color=grd, linestyle='--', linewidth=0.5, alpha=0.7)
        ax.set_axisbelow(True)

        for sp in ('top', 'right'):
            ax.spines[sp].set_visible(False)
        for sp in ('bottom', 'left'):
            ax.spines[sp].set_color(brd)

        # Nhãn số trên mỗi cột
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.05,
                        str(int(h)), ha='center', va='bottom',
                        fontsize=6.5, color=cfg)

    def _draw_disease_gender(self, ax, dgd: list,
                             cfg: str, brd: str,
                             c_male: str, c_female: str, c_other: str):
        ax.set_title("Top 10 Bệnh Chính (Nam / Nữ)",
                     color=cfg, fontsize=9, fontweight='bold')
        if not dgd:
            ax.text(0.5, 0.5, "Chưa có dữ liệu", ha='center', va='center',
                    color=cfg, fontsize=9)
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_color(brd)
            return

        # Đảo ngược để bệnh nhiều nhất ở trên
        dgd_rev = list(reversed(dgd))
        labels  = [d[0][:18] + ('…' if len(d[0]) > 18 else '') for d in dgd_rev]
        nam_vals  = [d[2] for d in dgd_rev]
        nu_vals   = [d[3] for d in dgd_rev]
        khac_vals = [d[4] for d in dgd_rev]

        y = range(len(labels))

        b_nam  = ax.barh(list(y), nam_vals,  color=c_male,   edgecolor=brd, label="Nam",  height=0.6)
        b_nu   = ax.barh(list(y), nu_vals,   color=c_female, edgecolor=brd, label="Nữ",
                         left=nam_vals, height=0.6)

        # Khác chỉ vẽ nếu có
        left_other = [n + f for n, f in zip(nam_vals, nu_vals)]
        if any(k > 0 for k in khac_vals):
            ax.barh(list(y), khac_vals, color=c_other, edgecolor=brd, label="Khác",
                    left=left_other, height=0.6)

        ax.set_yticks(list(y))
        ax.set_yticklabels(labels, fontsize=7.5, color=cfg)
        ax.tick_params(axis='x', colors=cfg, labelsize=7)
        ax.set_xlabel("Số ca", color=cfg, fontsize=8)
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

        for sp in ('top', 'right'):
            ax.spines[sp].set_visible(False)
        for sp in ('bottom', 'left'):
            ax.spines[sp].set_color(brd)

        ax.legend(fontsize=7, loc='lower right',
                  labelcolor=cfg,
                  facecolor=ax.get_facecolor(),
                  edgecolor=brd)

        # Nhãn tổng cuối mỗi bar
        for i, d in enumerate(dgd_rev):
            total = d[1]
            ax.text(total + 0.05, i, str(total),
                    va='center', ha='left', fontsize=6.5, color=cfg)

    # ── Theme support ────────────────────────────────────────────────────────
    def apply_theme(self, colors: dict):
        self._colors = colors
        highlight = '#5ab4ff' if colors.get('bg', '#f') < '#888' else '#0078d4'
        self.lbl_today.config(foreground=highlight)
 
        # Cập nhật nền canvas cuộn
        self._scroll_canvas.configure(bg=colors.get('bg', '#f0f0f0'))

        if self._last_stats is not None:
            self._draw_charts(self._last_stats)
 

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
