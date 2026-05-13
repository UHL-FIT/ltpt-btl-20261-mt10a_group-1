"""
controllers/cli_controller.py
=============================
Controller điều phối luồng xử lý cho giao diện CLI.
"""

import sys
from views import cli_view
from models import patient as patient_model
from utils.logger import setup_logger

logger = setup_logger()


def _xem_danh_sach():
    """Lấy danh sách từ models và gửi sang views để in."""
    logger.info("CLI: Xem danh sách bệnh nhân.")
    df, ok = patient_model.lay_danh_sach()
    if ok:
        cli_view.hien_bang_benh_nhan(df)
    else:
        cli_view.thong_bao("❌ Lỗi khi đọc dữ liệu.")


def _them_benh_nhan():
    """Nhập liệu và thêm bệnh nhân mới."""
    logger.info("CLI: Thêm bệnh nhân.")
    data = cli_view.nhap_thong_tin_benh_nhan()
    if data:
        ok, msg, ma_bn = patient_model.them_benh_nhan(data)
        cli_view.thong_bao(f"✅ {msg}" if ok else f"❌ {msg}")


def _sua_benh_nhan():
    """Tìm và sửa thông tin bệnh nhân."""
    logger.info("CLI: Sửa bệnh nhân.")
    ma_bn = cli_view.nhap_ma_bn()
    if not ma_bn:
        return
    data = cli_view.nhap_thong_tin_benh_nhan()
    if data:
        ok, msg = patient_model.sua_benh_nhan(ma_bn, data)
        cli_view.thong_bao(f"✅ {msg}" if ok else f"❌ {msg}")


def _xoa_benh_nhan():
    """Xóa bệnh nhân sau khi xác nhận."""
    logger.info("CLI: Xóa bệnh nhân.")
    ma_bn = cli_view.nhap_ma_bn()
    if not ma_bn:
        return
    if cli_view.xac_nhan(f"Bạn có chắc muốn xóa {ma_bn}?"):
        ok, msg = patient_model.xoa_benh_nhan(ma_bn)
        cli_view.thong_bao(f"✅ {msg}" if ok else f"❌ {msg}")


def _tim_kiem():
    """Tìm kiếm bệnh nhân theo từ khóa."""
    logger.info("CLI: Tìm kiếm bệnh nhân.")
    keyword = input("\n  Nhập từ khóa tìm kiếm: ").strip()
    if keyword:
        df, ok = patient_model.tim_kiem(keyword)
        if ok:
            cli_view.hien_bang_benh_nhan(df)
    else:
        cli_view.thong_bao("❌ Từ khóa không được để trống!")


def _thong_ke():
    """Hiển thị thống kê."""
    logger.info("CLI: Xem thống kê.")
    df, ok = patient_model.lay_danh_sach()
    if ok:
        stats = patient_model.thong_ke(df)
        cli_view.hien_thong_ke(stats)
    else:
        cli_view.thong_bao("❌ Lỗi khi đọc dữ liệu.")


def chay_ung_dung():
    """Khởi chạy ứng dụng CLI."""
    logger.info("Khởi động ứng dụng (CLI)")
    try:
        while True:
            lua_chon = cli_view.hien_menu_chinh()

            if lua_chon == "1":
                _xem_danh_sach()
            elif lua_chon == "2":
                _them_benh_nhan()
            elif lua_chon == "3":
                _sua_benh_nhan()
            elif lua_chon == "4":
                _xoa_benh_nhan()
            elif lua_chon == "5":
                _tim_kiem()
            elif lua_chon == "6":
                _thong_ke()
            elif lua_chon == "0":
                print("\n  Cảm ơn bạn đã sử dụng chương trình!")
                logger.info("Thoát chương trình.")
                break
            else:
                cli_view.thong_bao("❌ Lựa chọn không hợp lệ!")
    except KeyboardInterrupt:
        print("\n\n  Thoát chương trình (Ctrl+C).")
        logger.warning("Thoát đột ngột do KeyboardInterrupt.")
        sys.exit(0)
    except Exception as e:
        cli_view.thong_bao(f"❌ Lỗi: {e}")
        logger.error(f"Ngoại lệ: {e}", exc_info=True)
