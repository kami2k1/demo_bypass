# Chạy và kiểm thử

## Chạy

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

flask --app wsgi run --debug        # http://127.0.0.1:5000, có auto reload
python wsgi.py                      # cách khác, tương đương
```

Không cần database, biến môi trường hay bước build frontend. `SECRET_KEY` có giá trị mặc
định cho môi trường phát triển; ở production hãy đặt biến môi trường thật.

## Kiểm thử

```bash
pytest                              # toàn bộ, dưới 1 giây
pytest tests/test_content.py        # chỉ kiểm tra tính toàn vẹn nội dung
pytest -k "search"                  # theo tên
pytest -v                           # xem tên từng test
```

`pyproject.toml` bật `filterwarnings = ["error"]`: một `DeprecationWarning` từ Flask hay
thư viện chuẩn sẽ làm test đỏ. Điều này có chủ đích — cảnh báo hôm nay là lỗi của phiên
bản sau.

## Lint và định dạng

```bash
make lint      # ruff check + ruff format --check
make format    # ruff format, ghi thay đổi
make check     # lint + test + kiểm tra nội dung nạp được
```

Cấu hình nằm trong `pyproject.toml`. `E501` (dòng quá dài) được tắt: `ruff format` đã lo
độ dài dòng của code, còn các chuỗi văn xuôi trong module nội dung không nên bị cắt máy
móc giữa câu.

## Năm tệp test và vai trò

| Tệp | Kiểm tra điều gì |
| --- | --- |
| `test_content.py` | Bất biến của dữ liệu: slug, đánh số, đủ thành phần, thẻ hợp lệ, demo trỏ đúng |
| `test_routes.py` | Mọi URL trả về 200; slug sai trả về 404; sitemap.xml là XML hợp lệ |
| `test_pages.py` | HTML thực sự chứa nội dung: tiêu đề, section, code, callout, mục lục |
| `test_search.py` | Xếp hạng, đoạn trích, truy vấn rỗng, và escape đầu vào |
| `test_markup.py` | Filter inline code: chuyển backtick nhưng vẫn escape HTML |

Điểm đáng chú ý ở `test_routes.py`: nó lặp qua **toàn bộ** bài học, chương, thẻ và demo lấy
từ registry, chứ không dùng danh sách URL viết tay. Thêm một bài mới là tự động có thêm
một trường hợp test; không thể thêm nội dung mà quên test nó.

```python
def test_moi_bai_hoc_tra_ve_200(client, curriculum):
    for lesson in curriculum.lessons:
        response = client.get(f"/lessons/{lesson.slug}")
        assert response.status_code == 200, lesson.slug
```

## Kiểm tra giao diện bằng ảnh chụp

Bộ test không kiểm tra hình thức trực quan. Khi sửa CSS hoặc template, hãy chụp ảnh và
xem lại:

```python
# /tmp/shot.py
import threading, time
from playwright.sync_api import sync_playwright
from app import create_app

app = create_app()
threading.Thread(target=lambda: app.run(port=5055, use_reloader=False), daemon=True).start()
time.sleep(2)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    for name, path in [("home", "/"), ("lesson", "/lessons/goroutine-co-ban")]:
        page.goto(f"http://127.0.0.1:5055{path}", wait_until="networkidle")
        page.screenshot(path=f"/tmp/shots/{name}.png")
    browser.close()
```

```bash
mkdir -p /tmp/shots && PYTHONPATH=. python /tmp/shot.py
```

Bốn khung nhìn nên kiểm tra: 1440px (desktop), 1024px (tablet — sidebar chuyển xuống dưới
bài viết), 860px (menu thu thành nút hamburger), 390px (điện thoại).

## Vòng lặp phát triển thường dùng

```bash
pytest -q && flask --app wsgi run --debug
```

Sửa nội dung thì cần khởi động lại tiến trình: `load_curriculum()` được cache bằng
`lru_cache` nên chỉ nạp một lần. Ở chế độ `--debug`, Flask tự khởi động lại khi file `.py`
đổi, nên trong thực tế bạn không phải làm gì thêm.
