# Software Requirements Specification (SRS) - Quản Lý Hồ Sơ Bệnh Nhân

## 1. Giới thiệu
### 1.1 Mục đích
Đặc tả yêu cầu chức năng và phi chức năng cho hệ thống **Quản Lý Hồ Sơ Bệnh Nhân** — phần mềm hỗ trợ quản lý thông tin bệnh nhân, lịch sử khám bệnh, thuốc và thống kê y tế.

### 1.2 Phạm vi
Hệ thống cung cấp giao diện trực quan để quản lý toàn bộ hồ sơ bệnh nhân bao gồm thông tin cá nhân, lịch sử khám bệnh, đơn thuốc, và biểu đồ thống kê.

---

## 2. Mô tả Tổng quan
### 2.1 Người dùng
* **Nhân viên Y tế / Bác sĩ**: Người trực tiếp sử dụng phần mềm. Toàn quyền CRUD.

### 2.2 Môi trường
* Windows 10/11 (cung cấp file `.exe`).
* Chạy offline hoàn toàn, dữ liệu lưu SQLite local.

---

## 3. Yêu cầu Chức năng

### FR1: Quản lý Bệnh nhân & GUI
* **FR1.1**: Cửa sổ chính với sidebar navigation (4 trang: Bệnh nhân, Lịch sử khám, Thuốc, Thống kê).
* **FR1.2**: Popup form Thêm/Sửa bệnh nhân với validation đầy đủ.
* **FR1.3**: Xóa một hoặc nhiều bệnh nhân (checkbox).
* **FR1.4**: Tìm kiếm theo: Tất cả, Mã BN, Họ tên, Giới tính, SĐT, Bệnh chính.

### FR2: Thông tin Bệnh nhân
* Họ tên, tuổi, giới tính, SĐT, địa chỉ.
* Chiều cao, cân nặng (auto tính BMI + phân loại WHO).
* Ngày tiếp nhận, bệnh chính, bệnh phụ, ghi chú.

### FR3: Lịch sử Khám bệnh
* Mỗi BN có nhiều lần khám. Mỗi lần ghi: ngày khám, triệu chứng, chẩn đoán, huyết áp, nhiệt độ, bác sĩ.

### FR4: Lịch sử Thuốc
* Mỗi BN có nhiều đơn thuốc. Ghi: tên thuốc, liều lượng, tần suất, ngày bắt đầu/kết thúc.

### FR5: Import / Export
* Import bệnh nhân hàng loạt từ CSV (theo template).
* Export danh sách ra CSV.

### FR6: Thống kê & Biểu đồ
* Phân bố giới tính (Pie chart).
* Phân bố tuổi (Histogram).
* Top 10 bệnh phổ biến (Bar chart).
* Phân loại BMI (Bar chart).

---

## 4. Yêu cầu Phi chức năng

### NFR1: Kiến trúc MVC
* **Model**: SQLite + Pandas/Numpy xử lý tính toán.
* **View**: Tkinter với theme y tế, auto resize.
* **Controller**: Python điều phối View ↔ Model.

### NFR2: UI/UX
* Sidebar navigation modern, color scheme y tế (xanh dương/trắng).
* Auto resize khi thay đổi kích thước cửa sổ.
* Emoji icon trên buttons.

### NFR3: Validation
* Kiểm tra dữ liệu đầu vào với messagebox cảnh báo.
* Tuổi: số nguyên 0-150. SĐT: 10-11 số. Ngày: dd/mm/yyyy.

### NFR4: Developer Experience
* `uv sync` để đồng bộ dependencies.
* Fallback `pip + venv` cho dev không dùng uv.
