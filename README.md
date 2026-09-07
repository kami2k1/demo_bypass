# Go Nhanh — site giới thiệu ngôn ngữ Go

Ứng dụng **Python Flask** giới thiệu ngôn ngữ **Go (Golang)**: 110 bài học, mỗi bài có ví
dụ mã chạy được, cùng 8 demo tương tác dựng bằng HTML/CSS thuần.

| Chỉ số | Giá trị |
| --- | --- |
| Bài học | 110 |
| Chương | 12 |
| Ví dụ mã | 165 (~2200 dòng) |
| Demo tương tác | 8 |
| URL công khai | > 170 |
| Test | 73, chạy dưới 1 giây |

## Chạy tại máy

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

flask --app wsgi run --debug     # http://127.0.0.1:5000
pytest                            # 73 test
```

Không cần database, không cần bước build frontend, không cần biến môi trường nào.

## Bản đồ mã nguồn

```
app/
├── __init__.py           # application factory
├── config.py             # cấu hình theo môi trường
├── markup.py             # filter inline code cho nội dung
├── search.py             # chỉ mục tìm kiếm trong bộ nhớ
├── blueprints/
│   ├── site.py           # trang chủ, tìm kiếm, demo, sitemap
│   └── learn.py          # lộ trình, chương, bài học, thẻ
├── content/
│   ├── models.py         # Lesson, Chapter, Section, CodeSample, Demo
│   ├── builder.py        # constructor gọn cho tác giả nội dung
│   ├── registry.py       # gộp + kiểm tra + lập chỉ mục
│   ├── demos.py          # danh sách demo
│   └── chapters/         # 12 module nội dung
├── templates/            # Jinja: layout, trang, macro, demo
└── static/               # CSS thuần + một file JS
docs/                     # tài liệu (bắt đầu từ docs/README.md)
tests/                    # 73 test
```

## Tài liệu

| Tài liệu | Nội dung |
| --- | --- |
| [docs/kien-truc.md](docs/kien-truc.md) | Kiến trúc, luồng một request, các quyết định thiết kế |
| [docs/them-noi-dung.md](docs/them-noi-dung.md) | Cách thêm bài học, chương và demo mới |
| [docs/chay-va-kiem-thu.md](docs/chay-va-kiem-thu.md) | Chạy, kiểm thử, chụp ảnh giao diện |
| [docs/frontend.md](docs/frontend.md) | Quy ước CSS/JS, design token, khả năng truy cập |
| [docs/trien-khai.md](docs/trien-khai.md) | Triển khai với gunicorn, Docker, checklist production |

## Một lưu ý về nội dung

Trang [Tại sao Go](app/templates/why_go.html) nói thẳng: Go **không** phải ngôn ngữ nhanh
nhất trên mọi benchmark. C, C++ và Rust vẫn dẫn trước ở tính toán thuần. Go dẫn đầu khi
tính cả ba chiều — thời gian biên dịch, thời gian chạy và thời gian bảo trì — và site này
trình bày đúng như vậy thay vì đưa ra một khẩu hiệu không kiểm chứng được.
