"""Markup tối giản cho nội dung: chỉ hỗ trợ inline code bằng dấu backtick."""

from __future__ import annotations

import re

from markupsafe import Markup, escape

_INLINE_CODE = re.compile(r"`([^`]+)`")


def inline_code(text: str) -> Markup:
    """Escape trước rồi mới chuyển `x` thành <code>x</code>.

    Thứ tự này quan trọng: nội dung do người dùng cung cấp không thể chèn HTML,
    còn dấu backtick không bị escape nên mẫu vẫn khớp sau bước escape.
    """
    return Markup(_INLINE_CODE.sub(r"<code>\1</code>", str(escape(text))))
