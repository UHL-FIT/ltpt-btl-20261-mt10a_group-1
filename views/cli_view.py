"""
views/cli_view.py
=================
Module hiển thị giao diện CLI trên Terminal cho Quản lý Bệnh nhân.
"""


def hien_menu_chinh():
    """
    Hiển thị menu chính CLI và nhận lựa chọn.

    Returns:
        str: Lựa chọn của người dùng.
    """
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║     🏥 QUẢN LÝ HỒ SƠ BỆNH NHÂN (CLI)     ║")
    print("╠══════════════════════════════════════════════╣")
    print("║  1. Xem danh sách bệnh nhân                ║")
    print("║  2. Thêm bệnh nhân                         ║")
    print("║  3. Sửa thông tin bệnh nhân                ║")
    print("║  4. Xóa bệnh nhân                          ║")
    print("║  5. Tìm kiếm bệnh nhân                     ║")
    print("║  6. Xem thống kê                            ║")
    print("║  0. Thoát                                   ║")
    print("╚══════════════════════════════════════════════╝")
    return input("  Chọn chức năng: ").strip()


def hien_bang_benh_nhan(df):
    """
    Hiển thị danh sách bệnh nhân dạng bảng trên Terminal.

    Args:
        df (pandas.DataFrame): Dữ liệu bệnh nhân.
    """
    if df.empty:
        print("\n  (Chưa có bệnh nhân nào)")
        return

    print("\n  DANH SÁCH BỆNH NHÂN")
    header = f"  {'MaBN':<10} {'Họ tên':<22} {'Tuổi':>4} {'GT':<5} {'SĐT':<12} {'Ngày TN':<12} {'Bệnh chính':<18} {'BMI':>5}"
    print(header)
    print("  " + "─" * len(header.strip()))

    for _, row in df.iterrows():
        ma = str(row.get('ma_bn', ''))[:9]
        ten = str(row.get('ho_ten', ''))[:21]
        tuoi = int(row.get('tuoi', 0))
        gt = str(row.get('gioi_tinh', ''))[:4]
        sdt = str(row.get('sdt', ''))[:11]
        ngay = str(row.get('ngay_tiep_nhan', ''))[:11]
        benh = str(row.get('benh_chinh', ''))[:17]
        bmi = float(row.get('bmi', 0))

        bmi_str = f"{bmi:.1f}" if bmi > 0 else "  —"
        print(f"  {ma:<10} {ten:<22} {tuoi:>4} {gt:<5} {sdt:<12} {ngay:<12} {benh:<18} {bmi_str:>5}")

    print(f"\n  Tổng: {len(df)} bệnh nhân")


def hien_thong_ke(stats):
    """
    Hiển thị thống kê tổng quan.

    Args:
        stats (dict): Dữ liệu thống kê.
    """
    if not stats or stats.get("tong_bn", 0) == 0:
        print("\n  (Chưa có dữ liệu thống kê)")
        return

    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║          📊 THỐNG KÊ BỆNH NHÂN              ║")
    print("  ╠══════════════════════════════════════════════╣")
    si_so = f"{stats['tong_bn']} (Nam: {stats.get('nam', 0)}, Nữ: {stats.get('nu', 0)})"
    print(f"  ║  Tổng BN        : {si_so:<25} ║")
    print(f"  ║  Tuổi TB        : {stats.get('tuoi_tb', 0):<25.1f} ║")
    print(f"  ║  BMI TB         : {stats.get('bmi_tb', 0):<25.1f} ║")
    benh = str(stats.get('benh_pho_bien', 'N/A'))[:25]
    print(f"  ║  Bệnh phổ biến  : {benh:<25} ║")
    print("  ╚══════════════════════════════════════════════╝")


def nhap_thong_tin_benh_nhan():
    """
    Nhập thông tin bệnh nhân từ Terminal.

    Returns:
        dict/None: Thông tin bệnh nhân hoặc None nếu thiếu.
    """
    print("\n  ── Nhập thông tin bệnh nhân ──")
    ho_ten = input("  Họ tên (*)    : ").strip()
    tuoi_str = input("  Tuổi (*)      : ").strip()
    gioi_tinh = input("  Giới tính     : ").strip() or "Nam"
    sdt = input("  SĐT           : ").strip()
    ngay_tn = input("  Ngày tiếp nhận: ").strip()
    benh_chinh = input("  Bệnh chính (*): ").strip()
    benh_phu = input("  Bệnh phụ      : ").strip()

    if not ho_ten or not tuoi_str or not benh_chinh:
        thong_bao("❌ Họ tên, Tuổi và Bệnh chính không được để trống!")
        return None

    try:
        tuoi = int(tuoi_str)
    except ValueError:
        thong_bao("❌ Tuổi phải là số nguyên!")
        return None

    return {
        "ho_ten": ho_ten, "tuoi": tuoi, "gioi_tinh": gioi_tinh,
        "sdt": sdt, "ngay_tiep_nhan": ngay_tn,
        "benh_chinh": benh_chinh, "benh_phu": benh_phu
    }


def nhap_ma_bn():
    """Nhập mã bệnh nhân."""
    return input("\n  Nhập Mã BN (VD: BN-00001): ").strip().upper()


def thong_bao(msg):
    """Hiển thị thông báo."""
    print(f"\n  {msg}")


def xac_nhan(msg):
    """Hỏi xác nhận yes/no."""
    return input(f"\n  {msg} (y/n): ").strip().lower() in ("y", "yes")
