# Thêm nội dung

## Thêm một bài học

Mở module chương tương ứng trong `app/content/chapters/` và thêm một phần tử vào danh sách
`lessons`:

```python
lesson(
    slug="ten-bai-khong-dau",          # a-z, 0-9 và dấu gạch ngang
    title="Tiêu đề bài học",
    summary="Một câu nói rõ bài này giải quyết điều gì.",
    level="beginner",                  # beginner | intermediate | advanced
    tags=["dong-thoi", "runtime"],     # slug ASCII, dùng làm URL
    sections=[
        sec(
            "Tiêu đề mục",
            "Đoạn văn thứ nhất.",
            "Đoạn văn thứ hai.",
            note="Callout tuỳ chọn cho điều dễ vấp.",
        ),
    ],
    samples=[
        code(
            "Nhãn của ví dụ",
            """
package main

func main() {}
""",
            output="kết quả in ra (tuỳ chọn)",
            explanation="một câu giải thích (tuỳ chọn)",
        ),
    ],
    takeaways=["Ý cần nhớ 1", "Ý cần nhớ 2"],
    exercises=["Bài tập tuỳ chọn"],
),
```

Không cần làm gì thêm. Số thứ tự bài, điều hướng trước/sau, trang thẻ, tìm kiếm, sitemap
và các liên kết "cùng chương" đều được suy ra từ dữ liệu.

### Quy tắc bắt buộc

Registry sẽ từ chối nạp nếu vi phạm:

- `slug` khớp `^[a-z0-9]+(-[a-z0-9]+)*$` và không trùng với bài nào khác
- `level` thuộc `{beginner, intermediate, advanced}`
- ít nhất một section, mỗi section có ít nhất một đoạn văn
- ít nhất một code sample, và code không rỗng
- ít nhất hai takeaway
- `language` của sample thuộc danh sách trong `tests/test_content.py`

Chạy `pytest tests/test_content.py` để kiểm tra ngay; thông báo lỗi luôn kèm slug của bài
có vấn đề.

### Viết inline code trong văn xuôi

Dùng dấu backtick: `` "Chạy `go build` để biên dịch" ``. Filter `inline_code` chuyển thành
`<code>` sau khi đã escape HTML. Không viết thẻ HTML trong dữ liệu nội dung — nó sẽ hiện
ra dưới dạng văn bản, và đó là hành vi có chủ đích.

## Thêm một chương

1. Tạo `app/content/chapters/ch13_ten_chuong.py` theo mẫu của các chương có sẵn
2. Thêm import và tên module vào `CHAPTER_MODULES` trong `chapters/__init__.py`

Vị trí trong `CHAPTER_MODULES` quyết định vị trí trong lộ trình và cách đánh số bài.

## Thêm một demo

Demo là template partial, không phải HTML nằm trong dữ liệu — nhờ vậy không chỗ nào trong
ứng dụng cần `|safe`.

1. Tạo `app/templates/demos/ten_demo.html` (chỉ HTML, dùng class CSS)
2. Thêm style vào `app/static/css/demos.css`
3. Thêm một `Demo(...)` vào `DEMOS` trong `app/content/demos.py`, với `related_lesson` là
   slug của một bài đang tồn tại

Registry kiểm tra `related_lesson`: trỏ sai slug thì ứng dụng không khởi động.

## Thêm hoặc đổi thẻ

Thẻ chỉ là chuỗi trong `tags` của bài học. Trang `/tags/<tag>` và trang tổng hợp `/tags`
tự sinh từ dữ liệu. Vì thẻ nằm trong URL, hãy dùng ASCII không dấu và gạch ngang
(`hieu-nang`, không phải `hiệu năng`).

Trước khi tạo thẻ mới, xem `/tags` để tránh tạo thẻ gần trùng nghĩa với thẻ đã có — thẻ
chỉ hữu ích khi nó gom được nhiều bài.

## Danh sách kiểm tra trước khi commit nội dung

```bash
pytest -q                      # 73 test, gồm toàn bộ kiểm tra nội dung
flask --app wsgi run --debug   # xem lại bài mới trên trình duyệt
```

Kiểm tra bằng mắt ba chỗ: callout hiển thị đúng, code block không bị tràn ngang trên màn
hình hẹp, và điều hướng trước/sau trỏ tới bài đúng.
