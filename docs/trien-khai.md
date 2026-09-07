# Triển khai

## Chạy với gunicorn

Server phát triển của Flask không dành cho production: nó đơn luồng và không chịu tải.

```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8000 --access-logfile - wsgi:app
```

Chọn số worker theo CPU: khoảng `2 × số lõi + 1`. Vì nội dung nằm trong bộ nhớ và mỗi
worker nạp một bản riêng, hãy tính thêm dung lượng đó — hiện khoảng vài MB mỗi worker.

## Biến môi trường

| Biến | Bắt buộc | Mặc định | Ý nghĩa |
| --- | --- | --- | --- |
| `SECRET_KEY` | Ở production | `dev-only` | Khoá ký session của Flask |

Site không dùng session hay cookie, nhưng đặt `SECRET_KEY` thật vẫn là mặc định an toàn
cho trường hợp về sau có thêm form.

## Docker

```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY app ./app
COPY wsgi.py .

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "wsgi:app"]
```

Copy `requirements.txt` trước phần code để layer cài phụ thuộc được cache lại giữa các
lần build — cùng một lý do như trong bài học về Docker của chính site này.

## Phục vụ file tĩnh

Ở quy mô nhỏ, để Flask phục vụ `app/static/` là đủ; `SEND_FILE_MAX_AGE_DEFAULT` đặt cache
24 giờ. Với lưu lượng lớn, hãy đặt nginx hoặc CDN phía trước:

```nginx
location /static/ {
    alias /app/app/static/;
    expires 7d;
    add_header Cache-Control "public";
}
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

Lưu ý: CSS hiện chưa có hash phiên bản trong tên file, nên đừng đặt cache dài hơn vài
ngày — nếu không, người dùng sẽ giữ bản CSS cũ sau khi bạn deploy.

## Checklist trước khi deploy

```bash
pytest                                  # 73 test phải xanh
python -c "from app import create_app; create_app()"   # kiểm tra nội dung nạp được
```

Bước thứ hai đáng làm riêng: nó phát hiện lỗi dữ liệu nội dung (slug trùng, demo trỏ sai
bài, dưới 100 bài học) trước khi container khởi động và thất bại trong vòng lặp restart.

- [ ] `SECRET_KEY` được đặt từ secret manager, không nằm trong image
- [ ] Chạy sau reverse proxy có TLS
- [ ] Log truy cập của gunicorn được thu về hệ thống tập trung
- [ ] Có health check trỏ tới `/` (site không có endpoint riêng vì không có phụ thuộc ngoài)
- [ ] Cache của file tĩnh không dài hơn nhịp deploy

## Vì sao không có endpoint /health riêng

Site không có database, cache hay dịch vụ ngoài nào. Một readiness check kiểm tra phụ
thuộc sẽ không có gì để kiểm tra, và một liveness check chỉ cần biết tiến trình còn trả
lời hay không — `GET /` làm đúng việc đó. Khi nào site có phụ thuộc ngoài, hãy tách hai
endpoint theo đúng cách được mô tả trong bài *Health check: liveness và readiness*.
