# Kiến trúc

## Vấn đề cần giải

Yêu cầu là một site tối thiểu 100 trang. Cách hiển nhiên — tạo 100 file HTML — sai ngay từ
bước thứ hai: mỗi file mang một bản sao của layout, nên sửa thanh điều hướng là sửa một
trăm lần, và chắc chắn có file bị bỏ sót. Thêm nữa, không có gì bảo đảm trang thứ 87 có đủ
tiêu đề, ví dụ và liên kết trước/sau.

Cách làm ở đây đảo ngược bài toán: **nội dung là dữ liệu, trang là hàm của dữ liệu**.

```
Module nội dung  →  Registry (gộp + kiểm tra)  →  Blueprint  →  Template  →  HTML
   ch01..ch12          Curriculum                site/learn      Jinja
```

Kết quả: 110 bài học đi qua **một** route `/lessons/<slug>` và **một** template
`lesson.html`. Sửa layout một lần là 110 trang đổi theo.

## Bốn tầng

### 1. Tầng nội dung — `app/content/`

`models.py` định nghĩa các dataclass bất biến (`frozen=True, slots=True`):

- `CodeSample` — một ví dụ mã, kèm output và lời giải thích tuỳ chọn
- `Section` — một mục văn bản, gồm nhiều đoạn và một callout tuỳ chọn
- `Lesson` — một bài học: metadata + sections + samples + takeaways + exercises
- `Chapter` — một nhóm bài học
- `Demo` — một demo HTML/CSS, trỏ tới template partial của nó

Điểm quan trọng: **các bất biến được kiểm tra trong `__post_init__`**. Một bài học không
có ví dụ mã, hay một section không có đoạn văn nào, sẽ làm việc nạp thất bại ngay lúc
import — chứ không âm thầm render ra một trang trống.

```python
def __post_init__(self) -> None:
    if self.level not in LEVELS:
        raise ValueError(f"lesson {self.slug!r} has unknown level {self.level!r}")
    if not self.samples:
        raise ValueError(f"lesson {self.slug!r} has no code samples")
```

`builder.py` cung cấp `lesson()`, `sec()`, `code()`, `chapter()` để module nội dung đọc
như văn bản có cấu trúc thay vì như code khởi tạo dataclass.

`chapters/__init__.py` liệt kê 12 module **tường minh**, không quét thư mục. Thứ tự trong
danh sách đó chính là thứ tự lộ trình, nên nó không được phụ thuộc vào thứ tự đọc
filesystem.

### 2. Registry — `app/content/registry.py`

`load_curriculum()` làm bốn việc, đúng một lần cho cả tiến trình (`lru_cache`):

1. **Đánh số** bài học liên tục 1..N và gắn thông tin chương vào từng bài
2. **Kiểm tra** slug không trùng, đủ số bài tối thiểu, demo trỏ tới bài tồn tại
3. **Lập chỉ mục** theo slug và theo thẻ
4. Trả về một `Curriculum` bất biến với các phương thức truy vấn

```python
MINIMUM_LESSONS = 100

def _validate(chapters, lessons) -> None:
    if len(lessons) < MINIMUM_LESSONS:
        raise ContentError(f"curriculum needs at least {MINIMUM_LESSONS} lessons, found {len(lessons)}")
```

Ràng buộc "ít nhất 100 bài" vì thế không phải một lời hứa trong tài liệu mà là một điều
kiện do mã nguồn thực thi: xoá bớt nội dung xuống dưới 100 bài thì ứng dụng không khởi
động được.

### 3. Tầng route — `app/blueprints/`

Hai blueprint theo mối quan tâm, không theo kiểu dữ liệu:

- `site` — trang chủ, tại sao Go, giới thiệu, tìm kiếm, demo, sitemap (HTML và XML)
- `learn` — lộ trình, chương, bài học, thẻ

Route giữ vai trò mỏng: tra cứu dữ liệu, `abort(404)` nếu không có, đưa vào template. Mọi
logic tính toán nằm ở tầng nội dung hoặc `search.py`.

### 4. Tầng hiển thị — `app/templates/`, `app/static/`

`base.html` giữ layout duy nhất. `partials/macros.html` chứa các macro tái dùng
(`lesson_card`, `code_block`, `tag_list`, `breadcrumb`). Mỗi demo là một partial riêng
trong `templates/demos/`, được `demo_detail.html` include theo tên lấy từ dữ liệu `Demo`.

## Luồng một request

`GET /lessons/goroutine-co-ban`:

1. Flask khớp route `learn.lesson_detail`
2. `load_curriculum()` trả về `Curriculum` từ cache
3. `curriculum.lesson(slug)` tra dict → O(1); không thấy thì 404
4. `curriculum.neighbours(lesson)` cho bài trước/sau bằng chỉ số, không quét tuyến tính
5. `_related()` tính các bài chia sẻ nhiều thẻ nhất
6. `lesson.html` render: sections, callout, code block, takeaways, bài tập, sidebar

Không truy vấn database, không I/O. Nội dung nằm trong bộ nhớ nên thời gian render là vài
mili giây.

## Tìm kiếm

`app/search.py` là một chỉ mục đảo đơn giản, dựng một lần và cache:

- Token hoá bằng regex, bỏ các mảnh chỉ gồm dấu câu
- Trọng số theo trường: tiêu đề 8, thẻ 5, tóm tắt 3, thân bài 1
- Điểm của một tài liệu là tổng trọng số các token trùng với truy vấn
- Đoạn trích lấy quanh vị trí xuất hiện đầu tiên của từ khoá

Với 110 tài liệu, quét toàn bộ mất chưa tới một mili giây, nên không cần Whoosh hay
Elasticsearch. Nếu số bài lên hàng nghìn, chỗ cần thay là **duy nhất** hàm `search()` —
phần còn lại của ứng dụng không biết chỉ mục được hiện thực thế nào.

## Bảo mật nội dung

Jinja bật autoescape mặc định, nên mọi giá trị dữ liệu đều được escape. Điều này quan
trọng vì nội dung chứa rất nhiều mã Go với `<-`, `<`, `&&`.

Filter `inline_code` trong `app/markup.py` cần cẩn thận hơn một chút: nó cho phép tác giả
viết `` `go build` `` trong văn xuôi. Thứ tự hai bước là điểm cốt lõi:

```python
def inline_code(text: str) -> Markup:
    return Markup(_INLINE_CODE.sub(r"<code>\1</code>", str(escape(text))))
```

**Escape trước, thay thế sau.** Nếu làm ngược lại, một đoạn văn chứa
`` `<img onerror=x>` `` sẽ trở thành HTML thật. Test `test_markup.py` khoá hành vi này
lại bằng cả hai chiều: chuỗi trong backtick vẫn bị escape, và HTML ngoài backtick cũng
vậy.

## Các quyết định thiết kế và lý do

| Quyết định | Lý do | Đánh đổi |
| --- | --- | --- |
| Nội dung là dataclass Python, không phải Markdown/CMS | Kiểm tra bất biến lúc import, IDE tự hoàn thành, không thêm phụ thuộc | Tác giả phải viết Python thay vì Markdown |
| Danh sách chương tường minh | Thứ tự lộ trình xác định, không phụ thuộc filesystem | Thêm chương phải sửa hai file |
| `lru_cache` trên `load_curriculum` | Nạp và kiểm tra một lần cho cả tiến trình | Nội dung không hot-reload; phải khởi động lại |
| CSS thuần, không framework | Không bước build, không phụ thuộc JS, tải nhanh | Phải tự viết layout |
| Tìm kiếm tự viết | Không phụ thuộc ngoài, đủ nhanh ở quy mô này | Không có stemming hay fuzzy match |
| Demo là template partial, không phải HTML trong dữ liệu | Không cần `|safe` ở bất kỳ đâu | Thêm demo phải tạo file template |

## Điều gì sẽ vỡ trước khi mở rộng

Nếu số bài học tăng lên hàng nghìn, hai chỗ cần xem lại: trang `/lo-trinh` render toàn bộ
danh sách trong một HTML (hiện ~84 KB), và `search()` quét tuyến tính. Cả hai đều là thay
đổi cục bộ — cấu trúc dữ liệu và route không cần đổi.
