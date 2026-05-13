import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from PIL import Image
import os
import threading
import sys
import io

# Đảm bảo hiển thị tiếng Việt trên Windows console nếu app in log ra console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

from du_lieu_mau import tai_du_lieu
from phan_tich import (
    tao_dataframe, phan_tich_bmi, phan_tich_huyet_ap_theo_nhom_tuoi,
    thong_ke_tan_suat_kham, thong_ke_dung_thuoc, thong_ke_tong_quan, tinh_bmi, phan_loai_bmi
)
from bieu_do import ve_tat_ca, CHART_DIR

# Cài đặt giao diện chung
ctk.set_appearance_mode("Dark")  # Dark mode
ctk.set_default_color_theme("blue")  # Màu chủ đạo

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ứng dụng Quản lý Hồ sơ Bệnh nhân")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Cấu hình grid chính
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Dữ liệu
        self.patients = []
        self.df = None
        self.images = {} # Lưu trữ CTkImage để tránh bị garbage collection

        # Tải dữ liệu ban đầu và giao diện tải
        self.loading_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.loading_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.loading_frame.grid_rowconfigure(0, weight=1)
        self.loading_frame.grid_columnconfigure(0, weight=1)
        
        self.loading_label = ctk.CTkLabel(self.loading_frame, text="Đang tải dữ liệu và khởi tạo biểu đồ...", font=ctk.CTkFont(size=20, weight="bold"))
        self.loading_label.grid(row=0, column=0)

        # Sử dụng thread để tránh đứng UI khi tải biểu đồ
        threading.Thread(target=self.init_data_and_charts, daemon=True).start()

    def init_data_and_charts(self):
        try:
            self.patients = tai_du_lieu()
            self.df = tao_dataframe(self.patients)
            
            # Tính các thống kê
            grouped = phan_tich_huyet_ap_theo_nhom_tuoi(self.df)
            visit_df = thong_ke_tan_suat_kham(self.patients)
            med_df = thong_ke_dung_thuoc(self.patients)
            
            # Vẽ tất cả biểu đồ (sẽ lưu file .png vào thư mục CHART_DIR)
            ve_tat_ca(self.df, grouped, visit_df, med_df)
            
            # Cập nhật GUI từ main thread
            self.after(0, self.setup_gui)
        except Exception as e:
            self.after(0, lambda: self.loading_label.configure(text=f"Lỗi khi tải dữ liệu: {str(e)}", text_color="red"))

    def setup_gui(self):
        # Ẩn loading
        self.loading_frame.destroy()

        # ==================== SIDEBAR ====================
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MEDCARE", font=ctk.CTkFont(size=24, weight="bold"), text_color="#3b82f6")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Các nút Sidebar
        self.btn_overview = ctk.CTkButton(self.sidebar_frame, text="Tổng quan", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=self.show_overview)
        self.btn_overview.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_patients = ctk.CTkButton(self.sidebar_frame, text="Danh sách Bệnh nhân", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=self.show_patients)
        self.btn_patients.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_bmi = ctk.CTkButton(self.sidebar_frame, text="Phân tích BMI", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.show_chart("phan_tich_bmi.png", "Phân tích Chỉ số BMI"))
        self.btn_bmi.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_bp = ctk.CTkButton(self.sidebar_frame, text="Huyết áp", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.show_chart("huyet_ap_nhom_tuoi.png", "Huyết áp trung bình theo nhóm tuổi"))
        self.btn_bp.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.btn_visits = ctk.CTkButton(self.sidebar_frame, text="Khám bệnh", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.show_chart("tan_suat_kham.png", "Tần suất Khám bệnh"))
        self.btn_visits.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.btn_meds = ctk.CTkButton(self.sidebar_frame, text="Dùng thuốc", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.show_chart("thong_ke_thuoc.png", "Thống kê Sử dụng Thuốc"))
        self.btn_meds.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        # Nút đổi theme
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Giao diện:", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

        # ==================== MAIN FRAME ====================
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.main_frame, text="Tổng quan", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="w")

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, padx=30, pady=(0, 30), sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Style cho Treeview (Bảng danh sách)
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview", 
                             background="#2b2b2b", 
                             foreground="white", 
                             rowheight=35, 
                             fieldbackground="#2b2b2b",
                             bordercolor="#343638",
                             borderwidth=0,
                             font=('Inter', 11))
        self.style.map('Treeview', background=[('selected', '#3b82f6')])
        self.style.configure("Treeview.Heading", 
                             background="#565b5e", 
                             foreground="white", 
                             relief="flat",
                             font=('Inter', 11, 'bold'))
        self.style.map("Treeview.Heading", background=[('active', '#3484F0')])

        # Hiển thị mặc định
        self.show_overview()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        if new_appearance_mode == "Light":
            self.style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
            self.style.configure("Treeview.Heading", background="#e5e7eb", foreground="black")
            self.style.map('Treeview', background=[('selected', '#3b82f6')])
        else:
            self.style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
            self.style.configure("Treeview.Heading", background="#565b5e", foreground="white")
            self.style.map('Treeview', background=[('selected', '#3b82f6')])

    def set_active_button(self, active_btn):
        # Đặt lại màu tất cả các nút
        buttons = [self.btn_overview, self.btn_patients, self.btn_bmi, self.btn_bp, self.btn_visits, self.btn_meds]
        for btn in buttons:
            btn.configure(fg_color="transparent")
        
        # Đặt màu nút đang active
        active_btn.configure(fg_color=("gray75", "gray25"))

    def show_overview(self):
        self.set_active_button(self.btn_overview)
        self.title_label.configure(text="Thống kê Tổng quan")
        self.clear_content()

        stats = thong_ke_tong_quan(self.df, self.patients)
        
        # Tạo grid lưới hiển thị card thống kê
        cards_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        cards_frame.pack(fill="both", expand=True)
        
        # Cấu hình grid
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
        cards_frame.grid_rowconfigure((0, 1, 2, 3), weight=0, pad=20)

        # Định dạng màu cho các thẻ
        colors = ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#ef4444", "#14b8a6", "#6366f1", "#ec4899", "#84cc16", "#06b6d4"]
        
        row = 0
        col = 0
        for i, (key, value) in enumerate(stats.items()):
            card = ctk.CTkFrame(cards_frame, corner_radius=10, border_width=1, border_color="gray30")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            lbl_key = ctk.CTkLabel(card, text=key.upper(), font=ctk.CTkFont(size=12, weight="bold"), text_color="gray60")
            lbl_key.pack(pady=(15, 5), padx=20, anchor="w")
            
            lbl_val = ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=28, weight="bold"), text_color=colors[i % len(colors)])
            lbl_val.pack(pady=(0, 15), padx=20, anchor="w")
            
            col += 1
            if col > 2:
                col = 0
                row += 1

    def show_patients(self):
        self.set_active_button(self.btn_patients)
        self.title_label.configure(text="Danh sách Bệnh nhân")
        self.clear_content()

        # Frame tìm kiếm
        search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 15))
        
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Tìm kiếm theo tên...", width=300)
        search_entry.pack(side="left", padx=(0, 10))
        
        # Khung chứa bảng
        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True)

        # Thanh cuộn
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side="right", fill="y")

        # Khai báo Treeview
        columns = ("ID", "Họ tên", "Tuổi", "Giới tính", "BMI", "Huyết áp", "Nhịp tim")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=tree_scroll.set, style="Treeview")
        tree_scroll.config(command=self.tree.yview)
        
        # Định nghĩa cột
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=50, anchor="center")
        
        self.tree.heading("Họ tên", text="Họ tên")
        self.tree.column("Họ tên", width=200)
        
        self.tree.heading("Tuổi", text="Tuổi")
        self.tree.column("Tuổi", width=60, anchor="center")
        
        self.tree.heading("Giới tính", text="Giới tính")
        self.tree.column("Giới tính", width=80, anchor="center")
        
        self.tree.heading("BMI", text="BMI")
        self.tree.column("BMI", width=120, anchor="center")
        
        self.tree.heading("Huyết áp", text="Huyết áp")
        self.tree.column("Huyết áp", width=100, anchor="center")
        
        self.tree.heading("Nhịp tim", text="Nhịp tim")
        self.tree.column("Nhịp tim", width=80, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        # Chèn dữ liệu
        self._populate_tree()

        # Cài đặt hàm tìm kiếm
        def search(*args):
            query = search_entry.get().lower()
            self._populate_tree(query)

        search_entry.bind("<KeyRelease>", search)

    def _populate_tree(self, search_query=""):
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        count = 0
        for idx, row in self.df.iterrows():
            if search_query and search_query not in row["ho_ten"].lower():
                continue
                
            bmi = tinh_bmi(row["can_nang"], row["chieu_cao"])
            phan_loai = phan_loai_bmi(bmi)
            ha = f"{row['huyet_ap_tam_thu']}/{row['huyet_ap_tam_truong']}"
            
            # Tô màu cho dòng chẵn lẻ
            tag = 'evenrow' if count % 2 == 0 else 'oddrow'
            
            self.tree.insert("", "end", values=(
                row["id"], row["ho_ten"], row["tuoi"], row["gioi_tinh"], 
                f"{bmi} ({phan_loai})", ha, row["nhip_tim"]
            ), tags=(tag,))
            count += 1
            
        self.tree.tag_configure('evenrow', background="#2b2b2b")
        self.tree.tag_configure('oddrow', background="#333333")

    def show_chart(self, filename, title):
        # Đổi active button
        if filename == "phan_tich_bmi.png":
            self.set_active_button(self.btn_bmi)
        elif filename == "huyet_ap_nhom_tuoi.png":
            self.set_active_button(self.btn_bp)
        elif filename == "tan_suat_kham.png":
            self.set_active_button(self.btn_visits)
        elif filename == "thong_ke_thuoc.png":
            self.set_active_button(self.btn_meds)

        self.title_label.configure(text=title)
        self.clear_content()

        path = os.path.join(CHART_DIR, filename)
        if not os.path.exists(path):
            lbl = ctk.CTkLabel(self.content_frame, text="Không tìm thấy file biểu đồ. Vui lòng thử lại sau.", text_color="red")
            lbl.pack(pady=50)
            return

        # Load hình ảnh và hiển thị
        try:
            pil_image = Image.open(path)
            # Thay đổi kích thước phù hợp với khung
            # Tỉ lệ biểu đồ là 14:5 hoặc 12:6, tuỳ biểu đồ
            w, h = pil_image.size
            ratio = min(800/w, 500/h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            
            ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_w, new_h))
            self.images[filename] = ctk_img # Giữ reference
            
            img_label = ctk.CTkLabel(self.content_frame, image=ctk_img, text="")
            img_label.pack(expand=True, fill="both")
        except Exception as e:
            lbl = ctk.CTkLabel(self.content_frame, text=f"Lỗi khi tải biểu đồ: {str(e)}", text_color="red")
            lbl.pack(pady=50)

if __name__ == "__main__":
    app = App()
    app.mainloop()
