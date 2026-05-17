import unicodedata

def remove_accents(text: str) -> str:
    """Xóa dấu tiếng Việt để hỗ trợ tìm kiếm không dấu."""
    if not text:
        return ""
    text = unicodedata.normalize('NFD', str(text))
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.replace('đ', 'd').replace('Đ', 'D').lower()
