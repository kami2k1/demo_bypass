"""Chương 12 — Đưa Go lên production."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="van-hanh",
    title="Vận hành production",
    summary=(
        "Build, đóng gói, cấu hình, quan sát, kiểm tra sức khoẻ, CI/CD và bảo mật "
        "chuỗi cung ứng — phần việc biến code thành một service đáng tin."
    ),
    lessons=[
        lesson(
            slug="build-flag-va-ldflags",
            title="Cờ build và nhúng thông tin phiên bản",
            summary="ldflags cho phép ghi commit hash và thời điểm build vào binary mà không sửa code.",
            level="intermediate",
            tags=["van-hanh", "cong-cu"],
            sections=[
                sec(
                    "Nhúng biến lúc build",
                    '`-ldflags "-X main.version=$(git rev-parse --short HEAD)"` gán giá trị '
                    "cho biến string cấp package lúc liên kết. Nhờ đó binary tự biết nó được "
                    "build từ commit nào — thông tin vô giá khi điều tra sự cố.",
                    "`-s -w` loại bỏ symbol table và debug info, giảm kích thước binary "
                    "khoảng 25%. Đổi lại stack trace mất một phần thông tin, nên hãy cân nhắc "
                    "nếu bạn dựa vào panic trace ở production.",
                ),
                sec(
                    "Build tag",
                    "`//go:build` cho phép biên dịch có điều kiện theo hệ điều hành, kiến "
                    "trúc hoặc tag tự định nghĩa. Dùng để tách code chỉ chạy trên Linux, hoặc "
                    "để có một hiện thực khác cho môi trường test.",
                    "Đừng lạm dụng build tag cho logic nghiệp vụ: code không được biên dịch "
                    "cũng không được test, và sẽ hỏng âm thầm.",
                    note="`runtime/debug.ReadBuildInfo()` cho biết module và phiên bản phụ thuộc đã build vào binary — không cần ldflags.",
                ),
            ],
            samples=[
                code(
                    "Build có thông tin phiên bản",
                    """
VERSION=$(git rev-parse --short HEAD)
BUILT=$(date -u +%Y-%m-%dT%H:%M:%SZ)

go build -trimpath \\
  -ldflags "-s -w -X main.version=$VERSION -X main.buildTime=$BUILT" \\
  -o bin/api ./cmd/api
""",
                    language="bash",
                ),
                code(
                    "Đọc trong chương trình",
                    """
var (
	version   = "dev"
	buildTime = "unknown"
)

func main() {
	slog.Info("khởi động", "version", version, "built", buildTime)

	if info, ok := debug.ReadBuildInfo(); ok {
		slog.Info("build", "go", info.GoVersion, "module", info.Main.Path)
	}
}
""",
                ),
            ],
            takeaways=[
                "`-X` nhúng phiên bản vào binary mà không sửa code.",
                "`-trimpath` bỏ đường dẫn tuyệt đối, cho build tái lập được.",
                "ReadBuildInfo cho thông tin module sẵn có, không cần cấu hình.",
            ],
            exercises=["Thêm endpoint `/version` trả về commit hash đã nhúng."],
        ),
        lesson(
            slug="cross-compile",
            title="Biên dịch chéo trong một lệnh",
            summary="GOOS và GOARCH là toàn bộ những gì cần để build cho hệ điều hành khác.",
            level="beginner",
            tags=["van-hanh", "cong-cu"],
            sections=[
                sec(
                    "Không cần toolchain riêng",
                    "`GOOS=linux GOARCH=arm64 go build` trên máy macOS tạo ra binary cho "
                    "Linux ARM. Không cần cross-compiler, không cần container. Đây là một "
                    "trong những tiện lợi khiến Go phổ biến cho CLI và công cụ hạ tầng.",
                    "`go tool dist list` liệt kê mọi cặp GOOS/GOARCH được hỗ trợ — hàng chục "
                    "tổ hợp, gồm cả wasm.",
                ),
                sec(
                    "cgo là ngoại lệ",
                    "Nếu code dùng cgo (một số driver SQLite, thư viện hình ảnh), biên dịch "
                    "chéo cần cross-compiler C và mọi thứ trở nên phức tạp. `CGO_ENABLED=0` "
                    "cho binary liên kết tĩnh hoàn toàn, chạy được trên image scratch.",
                    "Với net package, CGO_ENABLED=0 chuyển sang bộ giải DNS thuần Go. Điều này "
                    "hầu như luôn ổn, nhưng khác biệt nhỏ về cách đọc /etc/nsswitch.conf đáng "
                    "để biết khi gỡ lỗi DNS trong container.",
                    note="Ưu tiên chọn thư viện thuần Go khi có thể; nó giữ cho việc build và triển khai đơn giản.",
                ),
            ],
            samples=[
                code(
                    "Build cho nhiều nền tảng",
                    """
for target in linux/amd64 linux/arm64 darwin/arm64 windows/amd64; do
  GOOS=${target%/*} GOARCH=${target#*/} CGO_ENABLED=0 \\
    go build -o "dist/api-${target%/*}-${target#*/}" ./cmd/api
done
ls dist/
""",
                    language="bash",
                    output="api-darwin-arm64  api-linux-amd64  api-linux-arm64  api-windows-amd64",
                ),
            ],
            takeaways=[
                "GOOS/GOARCH là đủ để biên dịch chéo, không cần toolchain thêm.",
                "CGO_ENABLED=0 cho binary tĩnh chạy trên scratch.",
                "cgo làm mất hầu hết sự đơn giản này — hãy tránh khi có thể.",
            ],
            exercises=["Build binary cho ba nền tảng và kiểm tra kích thước từng file."],
        ),
        lesson(
            slug="docker-multi-stage",
            title="Docker image tối giản",
            summary="Multi-stage build cho image vài chục MB, không compiler, không shell.",
            level="intermediate",
            tags=["van-hanh", "bao-mat"],
            sections=[
                sec(
                    "Hai stage",
                    "Stage đầu dùng image golang có toolchain để build; stage sau chỉ copy "
                    "binary vào một base tối giản. Kết quả là image không chứa mã nguồn, "
                    "compiler hay công cụ — bề mặt tấn công nhỏ hơn hẳn.",
                    "Copy `go.mod`/`go.sum` và chạy `go mod download` trước khi copy toàn bộ "
                    "source. Layer phụ thuộc được cache và chỉ build lại khi go.mod đổi.",
                ),
                sec(
                    "Chọn base image",
                    "`scratch` nhỏ nhất nhưng không có CA certificate hay tzdata — phải copy "
                    "vào hoặc nhúng bằng embed. `gcr.io/distroless/static` có sẵn CA và user "
                    "không phải root, thường là lựa chọn cân bằng tốt nhất. Alpine tiện vì có "
                    "shell để debug, nhưng dùng musl libc nên cần chú ý khi có cgo.",
                    "Luôn chạy bằng user không phải root và đặt `--read-only` filesystem nếu "
                    "service không cần ghi.",
                    note="Không có shell nghĩa là không `docker exec` để debug. Hãy đầu tư vào log và metrics thay vì vào shell trong image.",
                ),
            ],
            samples=[
                code(
                    "Dockerfile hai stage",
                    """
FROM golang:1.23-alpine AS build
WORKDIR /src

# Layer phụ thuộc được cache riêng
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o /out/api ./cmd/api

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/api /api
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/api"]
""",
                    language="dockerfile",
                    output="REPOSITORY  TAG     SIZE\napi         latest  14.2MB",
                ),
            ],
            takeaways=[
                "Multi-stage giữ compiler và source ngoài image cuối.",
                "Cache layer `go mod download` riêng để build nhanh.",
                "distroless + nonroot là mặc định an toàn và thực dụng.",
            ],
            exercises=[
                "Đóng gói một service Go và so sánh kích thước image alpine với distroless."
            ],
        ),
        lesson(
            slug="cau-hinh-12-factor",
            title="Cấu hình theo 12-factor",
            summary="Cấu hình đến từ môi trường, được validate lúc khởi động, và không bao giờ chứa bí mật trong repo.",
            level="intermediate",
            tags=["van-hanh", "kien-truc"],
            sections=[
                sec(
                    "Đọc và kiểm tra một lần",
                    "Đọc toàn bộ cấu hình vào một struct ngay khi khởi động, validate và "
                    "thoát ngay nếu thiếu giá trị bắt buộc. Fail fast tốt hơn nhiều so với "
                    "phát hiện thiếu biến môi trường lúc 3 giờ sáng ở request thứ một nghìn.",
                    "Truyền struct cấu hình vào các thành phần qua tham số, đừng đọc "
                    "`os.Getenv` rải rác trong code — điều đó khiến việc test và tra soát "
                    "trở nên khổ sở.",
                ),
                sec(
                    "Bí mật và môi trường",
                    "Bí mật đến từ secret manager hoặc biến môi trường được inject, không từ "
                    "file trong repo. In cấu hình lúc khởi động là ý tưởng tốt — nhưng phải có "
                    "hàm che các trường bí mật.",
                    "Một binary duy nhất cho mọi môi trường, chỉ khác nhau ở cấu hình. Nếu "
                    'code của bạn có `if env == "production"` thì đó là dấu hiệu sắp có sự '
                    "cố “chỉ xảy ra ở production”.",
                    note="Hàm cấu hình nên nhận `func(string) (string, bool)` thay vì gọi os.LookupEnv trực tiếp — như vậy test không cần đặt biến môi trường thật.",
                ),
            ],
            samples=[
                code(
                    "Cấu hình có validate",
                    """
type Config struct {
	Addr        string
	DatabaseURL string
	LogLevel    slog.Level
	Timeout     time.Duration
}

func Load(getenv func(string) (string, bool)) (Config, error) {
	c := Config{
		Addr:     envOr(getenv, "ADDR", ":8080"),
		LogLevel: slog.LevelInfo,
		Timeout:  15 * time.Second,
	}

	var missing []string
	url, ok := getenv("DATABASE_URL")
	if !ok || url == "" {
		missing = append(missing, "DATABASE_URL")
	}
	c.DatabaseURL = url

	if len(missing) > 0 {
		return Config{}, fmt.Errorf("thiếu biến môi trường: %s", strings.Join(missing, ", "))
	}
	return c, nil
}

// Che bí mật khi log
func (c Config) LogValue() slog.Value {
	return slog.GroupValue(
		slog.String("addr", c.Addr),
		slog.String("database_url", "***"),
		slog.Duration("timeout", c.Timeout),
	)
}
""",
                ),
            ],
            takeaways=[
                "Đọc và validate cấu hình một lần lúc khởi động, fail fast.",
                "Tiêm hàm getenv để test không phụ thuộc môi trường thật.",
                "Hiện thực LogValue để che bí mật khi log cấu hình.",
            ],
            exercises=["Viết test cho Load với ba bộ biến môi trường: đủ, thiếu và sai định dạng."],
        ),
        lesson(
            slug="slog-va-observability",
            title="Log có cấu trúc với slog",
            summary="Log là giao diện gỡ lỗi chính của bạn ở production — hãy thiết kế nó tử tế.",
            level="intermediate",
            tags=["van-hanh", "quan-sat"],
            sections=[
                sec(
                    "Handler và attribute",
                    "`slog.New(slog.NewJSONHandler(...))` cho log JSON, dễ truy vấn ở "
                    "Elasticsearch hay Loki. `logger.With(...)` tạo logger con mang sẵn ngữ "
                    "cảnh — dùng để đính request id vào mọi dòng log của một request.",
                    "Đặt logger vào context ở middleware, rồi lấy ra ở các tầng dưới. Nhờ vậy "
                    "mọi dòng log của một request đều truy vết được về nhau.",
                ),
                sec(
                    "Ba trụ cột quan sát",
                    "Log cho sự kiện rời rạc kèm ngữ cảnh; metrics cho số liệu tổng hợp theo "
                    "thời gian; trace cho đường đi của một request qua nhiều service. Ba thứ "
                    "trả lời ba câu hỏi khác nhau và không thay thế nhau.",
                    "Nối chúng lại bằng một id chung: trace id xuất hiện trong log và trong "
                    "trace. Khi có sự cố, bạn đi từ metrics (biết cái gì bất thường) sang "
                    "trace (biết ở đâu) rồi tới log (biết vì sao).",
                    note="Nguyên tắc log: mỗi dòng phải giúp trả lời một câu hỏi mà người trực sự cố sẽ đặt ra.",
                ),
            ],
            samples=[
                code(
                    "Logger theo request qua context",
                    """
type loggerKey struct{}

func WithLogger(ctx context.Context, l *slog.Logger) context.Context {
	return context.WithValue(ctx, loggerKey{}, l)
}

func FromContext(ctx context.Context) *slog.Logger {
	if l, ok := ctx.Value(loggerKey{}).(*slog.Logger); ok {
		return l
	}
	return slog.Default()
}

func RequestLogger(base *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			id := r.Header.Get("X-Request-Id")
			if id == "" {
				id = newID()
			}
			l := base.With("request_id", id, "path", r.URL.Path)
			next.ServeHTTP(w, r.WithContext(WithLogger(r.Context(), l)))
		})
	}
}
""",
                ),
                code(
                    "Dùng ở tầng dưới",
                    """
func (s Service) Charge(ctx context.Context, id string, cents int64) error {
	log := FromContext(ctx)
	log.Debug("bắt đầu charge", "wallet_id", id, "cents", cents)
	// ... mọi dòng log đều tự có request_id
	return nil
}
""",
                ),
            ],
            takeaways=[
                "slog JSON handler cho log truy vấn được.",
                "Đưa logger vào context để mọi tầng có cùng ngữ cảnh.",
                "Log, metrics, trace trả lời ba câu hỏi khác nhau — cần cả ba.",
            ],
            exercises=[
                "Thêm request id vào log của một service và tra một request xuyên các dòng log."
            ],
        ),
        lesson(
            slug="metrics-va-canh-bao",
            title="Metrics và cảnh báo có ích",
            summary="Bốn chỉ số vàng, histogram cho độ trễ, và cảnh báo dựa trên triệu chứng thay vì nguyên nhân.",
            level="advanced",
            tags=["van-hanh", "quan-sat"],
            sections=[
                sec(
                    "Đo gì",
                    "Bốn chỉ số vàng: độ trễ, lưu lượng, tỉ lệ lỗi, mức sử dụng tài nguyên. "
                    "Với độ trễ, dùng histogram để tính được p50/p95/p99 — giá trị trung bình "
                    "che mất chính những request tệ nhất mà người dùng cảm nhận.",
                    "Cẩn thận với cardinality: đừng đặt user id hay URL đầy đủ làm label. Hãy "
                    "dùng mẫu route (`/users/{id}`) thay vì đường dẫn cụ thể, nếu không hệ "
                    "thống metrics sẽ nổ.",
                ),
                sec(
                    "Cảnh báo theo triệu chứng",
                    "Cảnh báo nên xuất phát từ điều người dùng cảm nhận: “tỉ lệ lỗi 5xx vượt "
                    "1% trong 5 phút”, “p99 vượt 1 giây”. Cảnh báo theo nguyên nhân (“CPU "
                    "80%”) thường gây báo động giả vì CPU cao có thể hoàn toàn bình thường.",
                    "Mỗi cảnh báo phải có runbook: nó nghĩa là gì, cần kiểm tra gì, làm gì để "
                    "giảm thiểu. Cảnh báo không ai biết xử lý thế nào sẽ bị bỏ qua, và rồi "
                    "cảnh báo thật cũng bị bỏ qua.",
                    note="Số cảnh báo phải đủ ít để mỗi lần nổ đều được xem. Cảnh báo bị làm ngơ tệ hơn không có cảnh báo.",
                ),
            ],
            samples=[
                code(
                    "Middleware đo metrics",
                    """
var (
	reqDuration = prometheus.NewHistogramVec(prometheus.HistogramOpts{
		Name:    "http_request_duration_seconds",
		Buckets: []float64{.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5},
	}, []string{"method", "route", "status"})
)

func Metrics(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		rec := &statusRecorder{ResponseWriter: w, status: 200}
		next.ServeHTTP(rec, r)

		reqDuration.WithLabelValues(
			r.Method,
			r.Pattern, // mẫu route, không phải URL cụ thể
			strconv.Itoa(rec.status),
		).Observe(time.Since(start).Seconds())
	})
}
""",
                ),
                code(
                    "Cảnh báo theo triệu chứng",
                    """
- alert: HighErrorRate
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[5m]))
      / sum(rate(http_requests_total[5m])) > 0.01
  for: 5m
  annotations:
    summary: "Tỉ lệ lỗi 5xx vượt 1%"
    runbook: "https://wiki/runbooks/high-error-rate"
""",
                    language="yaml",
                ),
            ],
            takeaways=[
                "Bốn chỉ số vàng và histogram cho độ trễ theo phân vị.",
                "Giữ cardinality thấp: dùng mẫu route, không dùng id.",
                "Cảnh báo theo triệu chứng và luôn kèm runbook.",
            ],
            exercises=["Thêm histogram độ trễ vào một service và vẽ p50/p99 trên dashboard."],
        ),
        lesson(
            slug="health-check-va-readiness",
            title="Health check: liveness và readiness",
            summary="Hai endpoint khác nhau cho hai câu hỏi khác nhau — trộn lẫn chúng gây sự cố lan rộng.",
            level="intermediate",
            tags=["van-hanh", "web"],
            sections=[
                sec(
                    "Liveness khác readiness",
                    "Liveness trả lời “process còn sống không” — nếu fail, orchestrator khởi "
                    "động lại pod. Nó phải cực kỳ đơn giản: trả về 200, không kiểm tra phụ "
                    "thuộc nào. Readiness trả lời “có nên gửi traffic tới không” — nó kiểm tra "
                    "DB, cache, và trả về không-ready khi đang shutdown.",
                    "Đặt kiểm tra DB vào liveness là lỗi kinh điển: DB chậm một chút và "
                    "Kubernetes khởi động lại toàn bộ pod, làm sự cố nặng thêm nhiều lần.",
                ),
                sec(
                    "Thiết kế readiness",
                    "Kiểm tra phụ thuộc với timeout ngắn (1–2 giây) và cache kết quả vài giây "
                    "để không tạo tải khi được gọi mỗi giây. Phân biệt phụ thuộc bắt buộc (DB) "
                    "với phụ thuộc tuỳ chọn (cache) — mất cache thì chậm hơn nhưng vẫn phục vụ "
                    "được.",
                    "Khi nhận SIGTERM, cho readiness trả về 503 ngay lập tức rồi mới bắt đầu "
                    "shutdown. Load balancer cần vài giây để rút pod khỏi vòng xoay.",
                    note="Thứ tự đúng khi shutdown: readiness → 503, chờ ~5 giây cho LB cập nhật, rồi Shutdown server.",
                ),
            ],
            samples=[
                code(
                    "Hai endpoint riêng biệt",
                    """
type Health struct {
	db        *sql.DB
	shuttingDown atomic.Bool
}

// Liveness: không kiểm tra phụ thuộc
func (h *Health) Live(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
}

// Readiness: kiểm tra phụ thuộc bắt buộc
func (h *Health) Ready(w http.ResponseWriter, r *http.Request) {
	if h.shuttingDown.Load() {
		http.Error(w, "đang shutdown", http.StatusServiceUnavailable)
		return
	}
	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()

	if err := h.db.PingContext(ctx); err != nil {
		http.Error(w, "database không sẵn sàng", http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)
}
""",
                ),
            ],
            takeaways=[
                "Liveness đơn giản tuyệt đối; readiness kiểm tra phụ thuộc.",
                "Đừng kiểm tra DB trong liveness — sẽ gây restart hàng loạt.",
                "Readiness trả 503 ngay khi bắt đầu shutdown.",
            ],
            exercises=["Thêm cả hai endpoint và cấu hình probe tương ứng trong Kubernetes."],
        ),
        lesson(
            slug="ci-cd-cho-go",
            title="CI/CD cho dự án Go",
            summary="Một pipeline gọn: fmt, vet, test -race, build, govulncheck — chạy trong vài phút.",
            level="intermediate",
            tags=["van-hanh", "chat-luong", "cong-cu"],
            sections=[
                sec(
                    "Các cổng kiểm tra",
                    "Thứ tự hợp lý theo tốc độ: kiểm tra định dạng (giây), `go vet` (giây), "
                    "build (giây tới phút), test có -race (phút), rồi các bước chậm hơn như "
                    "test tích hợp và govulncheck. Cổng nhanh chạy trước để phản hồi sớm.",
                    "Cache thư mục build (`~/.cache/go-build`) và module (`~/go/pkg/mod`) giữa "
                    "các lần chạy. Với dự án Go, điều này thường đưa CI từ vài phút xuống vài "
                    "chục giây.",
                ),
                sec(
                    "Quy tắc vận hành",
                    "Không cho merge khi CI đỏ, và giữ CI đủ nhanh để không ai muốn bỏ qua. "
                    "Test tích hợp cần DB thì dùng service container, không dùng DB dùng chung "
                    "— test phải độc lập và chạy song song được.",
                    "Build artefact một lần rồi dùng cùng artefact đó cho mọi môi trường. "
                    "Build lại cho từng môi trường nghĩa là bạn triển khai thứ chưa được test.",
                    note="Chạy `go mod tidy` trong CI và fail nếu git diff không rỗng — cách chắc chắn để go.mod luôn sạch.",
                ),
            ],
            samples=[
                code(
                    "GitHub Actions cho Go",
                    """
name: ci
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: test }
        options: >-
          --health-cmd pg_isready --health-interval 10s --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.23'
          cache: true

      - name: Kiểm tra định dạng
        run: test -z "$(gofmt -l .)" || { gofmt -l .; exit 1; }

      - name: go.mod phải sạch
        run: go mod tidy && git diff --exit-code go.mod go.sum

      - run: go vet ./...
      - run: go build ./...
      - run: go test -race -coverprofile=cover.out ./...

      - name: Quét lỗ hổng
        run: go run golang.org/x/vuln/cmd/govulncheck@latest ./...
""",
                    language="yaml",
                ),
            ],
            takeaways=[
                "Xếp cổng kiểm tra theo tốc độ, nhanh trước.",
                "Cache build và module để CI về mức vài chục giây.",
                "Build một artefact dùng cho mọi môi trường.",
            ],
            exercises=["Thêm bước kiểm tra `go mod tidy` sạch vào pipeline hiện có của bạn."],
        ),
        lesson(
            slug="bao-mat-chuoi-cung-ung",
            title="Bảo mật chuỗi cung ứng",
            summary="govulncheck, go.sum, checksum database và kỷ luật với phụ thuộc.",
            level="advanced",
            tags=["bao-mat", "van-hanh", "phu-thuoc"],
            sections=[
                sec(
                    "Ba lớp bảo vệ có sẵn",
                    "go.sum lưu hash của mọi module, nên nội dung bị thay đổi sẽ bị phát hiện. "
                    "Checksum database công khai (sum.golang.org) đảm bảo mọi người thấy cùng "
                    "một nội dung cho một phiên bản. Module proxy lưu bản sao bất biến, nên "
                    "tác giả xoá repo cũng không phá build của bạn.",
                    "`govulncheck` đối chiếu code của bạn với cơ sở dữ liệu lỗ hổng Go và — "
                    "điểm quan trọng — chỉ báo khi bạn **thật sự gọi tới** hàm có lỗ hổng, nên "
                    "ít báo động giả hơn các scanner thông thường.",
                ),
                sec(
                    "Kỷ luật với phụ thuộc",
                    "Mỗi phụ thuộc là một khoản nợ: bạn nhận cả code và cả rủi ro của nó. "
                    "Trước khi thêm, hãy hỏi: thư viện chuẩn làm được không? Nó có bao nhiêu "
                    "phụ thuộc chuyển tiếp? Còn được bảo trì không?",
                    "Cập nhật định kỳ chứ đừng để tích tụ hai năm: nâng cấp một bước nhỏ thì "
                    "dễ, nhảy năm phiên bản lớn thì thành dự án riêng. Ghim phiên bản chính "
                    "xác cho công cụ dùng trong CI để build tái lập được.",
                    note="Go stdlib đủ mạnh khiến số phụ thuộc trung bình của dự án Go thấp hơn nhiều so với các hệ sinh thái khác — hãy giữ lợi thế đó.",
                ),
            ],
            samples=[
                code(
                    "Quét và kiểm tra",
                    """
go run golang.org/x/vuln/cmd/govulncheck@latest ./...
# Vulnerability #1: GO-2024-2687
#   Fixed in: golang.org/x/net@v0.23.0
#   Example call stack: myapp/handler.Serve → net/http2.Server.ServeConn

go mod verify          # nội dung module khớp go.sum
go list -m all         # xem toàn bộ cây phụ thuộc
go mod graph | wc -l   # đo độ phức tạp cây phụ thuộc
""",
                    language="bash",
                ),
                code(
                    "Ghim công cụ theo phiên bản",
                    """
//go:build tools

package tools

import (
	_ "golang.org/x/vuln/cmd/govulncheck"
	_ "honnef.co/go/tools/cmd/staticcheck"
)
""",
                    explanation="File với build tag `tools` giữ công cụ trong go.mod để mọi người và CI dùng cùng một phiên bản.",
                ),
            ],
            takeaways=[
                "go.sum + checksum DB + proxy là ba lớp bảo vệ mặc định.",
                "govulncheck báo theo đường gọi thực tế nên ít báo động giả.",
                "Mỗi phụ thuộc là một khoản nợ — cập nhật đều, thêm có chọn lọc.",
            ],
            exercises=["Chạy govulncheck trên một dự án và xử lý phát hiện đầu tiên."],
        ),
        lesson(
            slug="bo-cuc-du-an-va-tong-ket",
            title="Bố cục dự án và tổng kết lộ trình",
            summary="Một layout dùng được cho hầu hết service, và bản đồ những gì nên học tiếp.",
            level="intermediate",
            tags=["kien-truc", "van-hanh", "tong-quan"],
            sections=[
                sec(
                    "Layout thực dụng",
                    "`cmd/<binary>/main.go` chỉ làm ba việc: đọc cấu hình, khởi tạo phụ thuộc, "
                    "gọi hàm `run(ctx)`. Logic nằm trong `internal/`, chia theo miền nghiệp vụ "
                    "chứ không theo tầng kỹ thuật. Không tạo `pkg/` trừ khi bạn thật sự xuất "
                    "bản thư viện.",
                    "Đặt `main` mỏng và một hàm `run(ctx context.Context) error` giúp bạn test "
                    "được toàn bộ quá trình khởi động — điều gần như không thể khi mọi thứ nằm "
                    "trong main.",
                ),
                sec(
                    "Học tiếp theo hướng nào",
                    "Nếu bạn làm hạ tầng: đọc mã nguồn `net/http` và `runtime`, học "
                    "eBPF/observability. Nếu làm sản phẩm: đi sâu vào thiết kế API, "
                    "database và mô hình miền. Nếu làm dữ liệu: streaming, Kafka, và các "
                    "mẫu xử lý theo lô.",
                    "Cách học Go hiệu quả nhất vẫn là đọc thư viện chuẩn. Nó là kho ví dụ về "
                    "cách viết Go tốt: interface nhỏ, zero value có nghĩa, tài liệu rõ ràng, "
                    "và test kỹ lưỡng.",
                    note="Toàn bộ bài học của site này là một lộ trình có thứ tự; nhưng bạn cũng có thể dùng nó như sách tra cứu theo thẻ và ô tìm kiếm.",
                ),
            ],
            samples=[
                code(
                    "Layout tham chiếu",
                    """
myservice/
├── cmd/
│   └── api/main.go            # mỏng: cấu hình + wiring + run()
├── internal/
│   ├── billing/               # miền nghiệp vụ
│   │   ├── service.go
│   │   └── service_test.go
│   ├── store/                 # truy cập dữ liệu
│   │   ├── postgres.go
│   │   └── migrations/
│   ├── httpapi/               # handler, middleware, router
│   └── config/
├── docs/
├── Dockerfile
├── Makefile
├── go.mod
└── go.sum
""",
                    language="text",
                ),
                code(
                    "main mỏng, run testable",
                    """
func main() {
	if err := run(context.Background(), os.Args[1:], os.LookupEnv); err != nil {
		slog.Error("thoát vì lỗi", "err", err)
		os.Exit(1)
	}
}

func run(ctx context.Context, args []string, getenv func(string) (string, bool)) error {
	cfg, err := config.Load(getenv)
	if err != nil {
		return err
	}
	db, err := store.Open(ctx, cfg.DatabaseURL)
	if err != nil {
		return err
	}
	defer db.Close()

	srv := httpapi.NewServer(cfg, db)
	return srv.ListenAndServeWithShutdown(ctx)
}
""",
                    explanation="Vì `run` nhận args và getenv, test có thể chạy toàn bộ khởi động mà không chạm vào môi trường thật.",
                ),
            ],
            takeaways=[
                "`main` mỏng, logic trong `internal/` chia theo miền nghiệp vụ.",
                "Hàm `run(ctx, args, getenv) error` làm quá trình khởi động test được.",
                "Đọc thư viện chuẩn là cách học Go tốt nhất.",
            ],
            exercises=[
                "Tái cấu trúc một main.go dài thành main mỏng + hàm run.",
                "Chọn ba bài trong site này bạn thấy khó nhất và viết lại ví dụ theo cách của mình.",
            ],
        ),
    ],
)
