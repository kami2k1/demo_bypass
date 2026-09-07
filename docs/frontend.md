# Frontend

Không có bước build, không có framework, không có phụ thuộc npm. Ba file CSS và một file
JS, tất cả nằm trong `app/static/`.

## Ba file CSS

| File | Trách nhiệm |
| --- | --- |
| `base.css` | Design token, layout, thành phần chung, responsive |
| `code.css` | Code block, khối output, màu token cho highlighter |
| `demos.css` | Style riêng của 8 demo |

Chia như vậy để sửa một demo không có nguy cơ chạm vào layout chung.

## Design token

Toàn bộ màu, bán kính, bóng và font nằm trong `:root` của `base.css`:

```css
:root {
  --go-cyan: #00add8;        /* màu thương hiệu Go */
  --go-cyan-dark: #007d9c;
  --go-navy: #0b1a24;
  --ink: #10212c;            /* văn bản chính */
  --ink-soft: #4a5b67;       /* văn bản phụ */
  --line: #d9e2ea;           /* viền */
  --radius: 10px;
  --shell: 1180px;           /* chiều rộng tối đa của nội dung */
}
```

Đừng viết mã màu trực tiếp trong quy tắc CSS. Nếu cần một màu chưa có, thêm token mới —
như vậy chủ đề vẫn thay đổi được từ một chỗ.

## Bốn breakpoint

| Ngưỡng | Thay đổi |
| --- | --- |
| ≤ 1024px | Hero xếp dọc; sidebar bài học chuyển xuống dưới bài viết |
| ≤ 860px | Menu thu thành nút hamburger; lưới về một cột |
| ≤ 560px | Ô thống kê về hai cột; footer một cột |

Menu di động dùng kỹ thuật checkbox + label, không cần JavaScript, nên nó hoạt động cả
khi JS bị chặn.

## JavaScript

`app/static/js/app.js` là một IIFE, tải với `defer`, làm đúng ba việc:

1. **Tô màu cú pháp** cho các khối `pre.code`
2. **Nút copy** cho từng code block
3. **Đóng menu** di động sau khi chọn một liên kết

Site hoạt động đầy đủ khi tắt JavaScript: mã nguồn vẫn hiển thị (chỉ là một màu), điều
hướng và tìm kiếm vẫn dùng được vì chúng là form và liên kết thật.

### Highlighter và vấn đề an toàn

Highlighter đọc `textContent` rồi dựng lại HTML, nên nó **phải** tự escape:

```javascript
const escapeHtml = (text) =>
  text.replace(/[&<>]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[ch]);

const wrap = (cls, text) => `<span class="${cls}">${escapeHtml(text)}</span>`;
```

Mọi nhánh trong `highlight()` đều đi qua `escapeHtml` hoặc `wrap`, kể cả nhánh mặc định.
Đây là điều kiện bắt buộc, vì đầu vào là mã Go chứa đầy `<-`, `<` và `&&`.

Một regex duy nhất bắt bốn loại token theo thứ tự ưu tiên: comment, chuỗi, số, định danh.
Thứ tự này quan trọng — nếu số được xét trước chuỗi, `"port 8080"` sẽ bị tô sai.

## Khả năng truy cập

Đã có:

- `skip-link` để bỏ qua điều hướng
- `aria-label` cho nav, form tìm kiếm, breadcrumb và nút hamburger
- Vùng focus nhìn thấy được (`outline: 2px solid var(--go-cyan)`)
- HTML có ngữ nghĩa: `header`, `nav`, `main`, `article`, `aside`, `footer`, `figure`
- `@media (prefers-reduced-motion: reduce)` tắt mọi animation của demo

Khi thêm animation cho demo mới, không cần làm gì thêm: quy tắc `prefers-reduced-motion`
áp dụng cho toàn bộ selector `*`.

## Quy ước đặt tên class

Đặt theo khối và phần tử, gạch ngang, không dùng CSS-in-JS hay utility class:

```
.lesson-card        khối
.lesson-card header phần tử con, chọn qua thẻ khi đủ rõ
.badge-level        biến thể
.is-active          trạng thái
```

Tiền tố `is-` chỉ dành cho trạng thái, để dễ tìm khi cần biết class nào do server gán
theo điều kiện.

## Macro Jinja thay cho lặp lại HTML

`templates/partials/macros.html` chứa `lesson_card`, `tag_list`, `code_block`,
`breadcrumb`. Nếu bạn thấy mình copy một đoạn HTML sang template thứ ba, hãy chuyển nó
thành macro — đó là ranh giới hợp lý.
