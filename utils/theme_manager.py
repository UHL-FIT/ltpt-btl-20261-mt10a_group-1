"""
THEME MANAGER – utils/theme_manager.py
Quản lý 4 chế độ giao diện: sáng, tối, theo hệ thống, theo thời gian.

Kiến trúc:
  ThemeManager chỉ biết về ttk.Style và danh sách callback.
  Nó KHÔNG biết về View – giao tiếp qua callback pattern.
  View đăng ký hàm apply_theme(colors) của mình để được thông báo.
"""
import platform
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from typing import Callable

# ─── Bảng màu ───────────────────────────────────────────────────────────────
THEMES: dict[str, dict] = {
    'light': {
        'bg':               '#f0f0f0',
        'fg':               '#1a1a1a',
        'entry_bg':         '#ffffff',
        'entry_fg':         '#1a1a1a',
        'button_bg':        '#e1e1e1',
        'button_fg':        '#1a1a1a',
        'button_active_bg': '#cce4f7',
        'select_bg':        '#0078d4',
        'select_fg':        '#ffffff',
        'tree_bg':          '#ffffff',
        'tree_fg':          '#1a1a1a',
        'tree_heading_bg':  '#e8e8e8',
        'text_bg':          '#ffffff',
        'text_fg':          '#1a1a1a',
        'insert_color':     '#1a1a1a',
        'border':           '#ababab',
        'trough':           '#dcdcdc',
        'tab_bg':           '#e5e5e5',
        'tab_selected_bg':  '#f0f0f0',
        'chart_bg':         '#f9f9f9',
        'chart_fg':         '#1a1a1a',
        'chart_grid':       '#dddddd',
    },
    'dark': {
        'bg':               '#2b2b2b',
        'fg':               '#d4d4d4',
        'entry_bg':         '#3c3f41',
        'entry_fg':         '#d4d4d4',
        'button_bg':        '#4c5052',
        'button_fg':        '#d4d4d4',
        'button_active_bg': '#2d6a9f',
        'select_bg':        '#2374b5',
        'select_fg':        '#ffffff',
        'tree_bg':          '#313335',
        'tree_fg':          '#d4d4d4',
        'tree_heading_bg':  '#3c3f41',
        'text_bg':          '#3c3f41',
        'text_fg':          '#d4d4d4',
        'insert_color':     '#d4d4d4',
        'border':           '#555555',
        'trough':           '#1e1e1e',
        'tab_bg':           '#3c3f41',
        'tab_selected_bg':  '#2b2b2b',
        'chart_bg':         '#313335',
        'chart_fg':         '#d4d4d4',
        'chart_grid':       '#444444',
    },
}

# Nhãn hiển thị trong menu
MODE_LABELS: dict[str, str] = {
    'light':  '☀️  Sáng',
    'dark':   '🌙  Tối',
    'system': '💻  Theo hệ thống',
    'time':   '🕐  Theo thời gian  (6h–18h: Sáng)',
}

# Giờ chuyển chế độ theo thời gian
_TIME_DAY_START   = 6   # 06:00 → bật chế độ sáng
_TIME_NIGHT_START = 18  # 18:00 → bật chế độ tối

# Khoảng thời gian polling khi ở chế độ system / time (ms)
_POLL_INTERVAL_MS = 30_000


class ThemeManager:
    """
    Quản lý chủ đề giao diện toàn ứng dụng.

    Luồng hoạt động
    ──────────────
    1. main.py tạo ThemeManager(root, style)
    2. Mỗi View đăng ký callback:  tm.register_callback(view.apply_theme)
    3. Khi người dùng chọn menu:   tm.set_mode('dark')
       → ThemeManager gọi _apply() để cập nhật ttk.Style
       → Thông báo tất cả callback → mỗi View tự cập nhật widget tk thuần

    Tại sao cần callback?
    ─────────────────────
    ttk.Style chỉ cập nhật các widget ttk.*. Các widget tk thuần (tk.Text,
    tk.Canvas, tk.Toplevel …) phải được cấu hình trực tiếp. Callback đảm
    bảo View luôn nhận được bảng màu mới nhất.
    """

    def __init__(self, root: tk.Tk, style: ttk.Style):
        self.root   = root
        self.style  = style
        self._mode   = 'light'   # chế độ logic: light | dark | system | time
        self._active = 'light'   # theme thực tế đang áp: light | dark
        self._callbacks: list[Callable] = []
        self._poll_job: str | None = None

    # ── Đăng ký callback ────────────────────────────────────────────────────
    def register_callback(self, cb: Callable):
        """
        Đăng ký hàm cb(colors: dict) để được gọi khi theme thay đổi.
        Thường là view.apply_theme.
        """
        self._callbacks.append(cb)

    # ── Public API ──────────────────────────────────────────────────────────
    def set_mode(self, mode: str):
        """
        Đặt chế độ: 'light' | 'dark' | 'system' | 'time'
        Tự động bật/tắt polling khi cần.
        """
        if mode not in MODE_LABELS:
            raise ValueError(f"Chế độ không hợp lệ: {mode!r}. Chọn: {list(MODE_LABELS)}")
        self._mode = mode
        self._refresh(force=True)
        if mode in ('system', 'time'):
            self._start_polling()
        else:
            self._stop_polling()

    @property
    def mode(self) -> str:
        """Chế độ đang được chọn (có thể khác theme đang hiển thị)."""
        return self._mode

    @property
    def active_theme(self) -> str:
        """Theme đang thực sự áp dụng: 'light' hoặc 'dark'."""
        return self._active

    @property
    def colors(self) -> dict:
        """Bảng màu đang áp dụng."""
        return THEMES[self._active]

    # ── Phát hiện theme hệ thống ─────────────────────────────────────────────
    @staticmethod
    def detect_system_theme() -> str:
        """Đọc cài đặt dark mode từ OS. Trả về 'light' hoặc 'dark'."""
        system = platform.system()
        try:
            if system == 'Darwin':                          # macOS
                result = subprocess.run(
                    ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                    capture_output=True, text=True, timeout=1
                )
                return 'dark' if 'Dark' in result.stdout else 'light'

            elif system == 'Windows':                       # Windows 10/11
                import winreg  # type: ignore
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
                )
                val, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                return 'light' if val == 1 else 'dark'

            elif system == 'Linux':                         # GNOME / KDE
                result = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                    capture_output=True, text=True, timeout=1
                )
                return 'dark' if 'dark' in result.stdout.lower() else 'light'

        except Exception:
            pass
        return 'light'   # fallback an toàn

    @staticmethod
    def get_time_theme() -> str:
        """6:00 – 17:59 → sáng; còn lại → tối."""
        hour = datetime.now().hour
        return 'light' if _TIME_DAY_START <= hour < _TIME_NIGHT_START else 'dark'

    # ── Nội bộ ──────────────────────────────────────────────────────────────
    def _resolve(self) -> str:
        """Chuyển _mode → theme thực tế ('light' hoặc 'dark')."""
        if self._mode == 'system':
            return self.detect_system_theme()
        if self._mode == 'time':
            return self.get_time_theme()
        return self._mode   # 'light' hoặc 'dark' trực tiếp

    def _refresh(self, force: bool = False):
        """Cập nhật nếu theme thực tế thay đổi (hoặc force=True)."""
        resolved = self._resolve()
        if resolved != self._active or force:
            self._active = resolved
            self._apply(THEMES[resolved])

    def _apply(self, c: dict):
        """
        Áp dụng bảng màu vào ttk.Style và thông báo cho các callback.
        Cần gọi style.theme_use('clam') trước để đảm bảo style hỗ trợ
        việc override màu sắc.
        """
        s = self.style
        s.theme_use('clam')

        # Mặc định toàn cục (tất cả ttk widget kế thừa)
        s.configure('.',
                    background=c['bg'],
                    foreground=c['fg'],
                    fieldbackground=c['entry_bg'],
                    bordercolor=c['border'],
                    troughcolor=c['trough'],
                    selectbackground=c['select_bg'],
                    selectforeground=c['select_fg'],
                    insertcolor=c['insert_color'])

        # Frame và Label
        for widget_class in ('TFrame', 'TLabel'):
            s.configure(widget_class, background=c['bg'], foreground=c['fg'])

        s.configure('TLabelframe',
                    background=c['bg'], foreground=c['fg'], bordercolor=c['border'])
        s.configure('TLabelframe.Label',
                    background=c['bg'], foreground=c['fg'])

        # Entry
        s.configure('TEntry',
                    fieldbackground=c['entry_bg'],
                    foreground=c['entry_fg'],
                    insertcolor=c['insert_color'],
                    bordercolor=c['border'],
                    selectbackground=c['select_bg'],
                    selectforeground=c['select_fg'])

        # Combobox
        s.configure('TCombobox',
                    fieldbackground=c['entry_bg'],
                    foreground=c['entry_fg'],
                    background=c['button_bg'],
                    arrowcolor=c['fg'],
                    selectbackground=c['select_bg'],
                    selectforeground=c['select_fg'])
        s.map('TCombobox',
              fieldbackground=[('readonly', c['entry_bg']), ('disabled', c['bg'])],
              foreground=[('readonly', c['entry_fg'])])

        # Button
        s.configure('TButton',
                    background=c['button_bg'],
                    foreground=c['button_fg'],
                    bordercolor=c['border'],
                    focuscolor=c['select_bg'])
        s.map('TButton',
              background=[('active', c['button_active_bg']), ('pressed', c['select_bg'])],
              foreground=[('active', c['button_fg']),        ('pressed', c['select_fg'])])

        # Notebook (tab bar)
        s.configure('TNotebook',
                    background=c['bg'],
                    bordercolor=c['border'],
                    tabmargins=[2, 5, 2, 0])
        s.configure('TNotebook.Tab',
                    background=c['tab_bg'],
                    foreground=c['fg'],
                    padding=[14, 5],
                    bordercolor=c['border'])
        s.map('TNotebook.Tab',
              background=[('selected', c['tab_selected_bg']),
                          ('active',   c['button_active_bg'])],
              foreground=[('selected', c['fg'])])

        # Treeview
        s.configure('Treeview',
                    background=c['tree_bg'],
                    foreground=c['tree_fg'],
                    fieldbackground=c['tree_bg'],
                    rowheight=26,
                    bordercolor=c['border'])
        s.configure('Treeview.Heading',
                    background=c['tree_heading_bg'],
                    foreground=c['fg'],
                    bordercolor=c['border'],
                    relief='flat')
        s.map('Treeview',
              background=[('selected', c['select_bg'])],
              foreground=[('selected', c['select_fg'])])

        # Scrollbar
        s.configure('TScrollbar',
                    background=c['button_bg'],
                    troughcolor=c['trough'],
                    bordercolor=c['border'],
                    arrowcolor=c['fg'])
        s.map('TScrollbar',
              background=[('active', c['button_active_bg'])])

        # Root window background (tk thuần)
        self.root.configure(bg=c['bg'])

        # Thông báo tất cả View để cập nhật widget tk thuần
        for cb in self._callbacks:
            try:
                cb(c)
            except Exception as exc:
                print(f"[ThemeManager] callback error: {exc}")

    # ── Polling (system / time mode) ─────────────────────────────────────────
    def _start_polling(self):
        self._stop_polling()
        self._poll()

    def _stop_polling(self):
        if self._poll_job:
            self.root.after_cancel(self._poll_job)
            self._poll_job = None

    def _poll(self):
        """Kiểm tra mỗi 30 giây xem theme có cần thay đổi không."""
        self._refresh()
        self._poll_job = self.root.after(_POLL_INTERVAL_MS, self._poll)