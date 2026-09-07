"""Chương 5 — Lỗi, panic và độ bền."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="loi-va-do-ben",
    title="Lỗi, panic và độ bền",
    summary=(
        "Go coi lỗi là giá trị bình thường. Chương này đi từ `errors.New` tới "
        "chiến lược bọc lỗi, retry và ranh giới giữa error và panic."
    ),
    lessons=[
        lesson(
            slug="error-la-gia-tri",
            title="Error là một giá trị",
            summary="Không có exception: lỗi được trả về, kiểm tra và truyền đi như mọi dữ liệu khác.",
            level="beginner",
            tags=["loi", "co-ban"],
            sections=[
                sec(
                    "Interface một phương thức",
                    "`type error interface { Error() string }`. Chỉ có thế. Mọi thứ khác "
                    "trong cách Go xử lý lỗi đều xây trên định nghĩa tối giản này.",
                    "Vì lỗi là giá trị, bạn có thể lưu vào struct, đưa vào channel, so "
                    "sánh, bọc lại và truyền qua tầng — những việc rất khó làm với exception.",
                ),
                sec(
                    "Vì sao không dùng exception",
                    "Exception tạo ra luồng điều khiển ẩn: đọc một hàm bạn không biết nó "
                    "có thể nhảy ra ở dòng nào. Với Go, mọi điểm có thể thất bại đều nhìn "
                    "thấy được trong code, và đó là lý do đọc code Go lạ khá dễ.",
                    "Cái giá là sự lặp lại của khối `if err != nil`. Đổi lại bạn có tính "
                    "tường minh; và trong thực tế, phần lớn khối đó nên làm gì đó hữu ích "
                    "như thêm ngữ cảnh, chứ không chỉ trả về nguyên trạng.",
                    note="Đừng bao giờ bỏ qua lỗi bằng `_`. Nếu thật sự có lý do, hãy viết comment giải thích tại sao.",
                ),
            ],
            samples=[
                code(
                    "Kiểm tra lỗi ngay tại chỗ",
                    """
data, err := os.ReadFile("config.yaml")
if err != nil {
	return fmt.Errorf("đọc cấu hình: %w", err)
}

var cfg Config
if err := yaml.Unmarshal(data, &cfg); err != nil {
	return fmt.Errorf("phân tích cấu hình: %w", err)
}
""",
                    explanation="Mỗi tầng thêm một mẩu ngữ cảnh, tạo thành câu chuyện đọc được khi lỗi lên tới log.",
                ),
            ],
            takeaways=[
                "`error` chỉ là interface với một phương thức Error().",
                "Lỗi là giá trị nên lưu trữ, truyền, so sánh được.",
                "Tính tường minh đổi lấy một chút lặp lại — hãy thêm ngữ cảnh cho nó có ích.",
            ],
            exercises=["Tìm trong code của bạn một chỗ bỏ qua lỗi bằng `_` và xử lý nó cho tử tế."],
        ),
        lesson(
            slug="tao-loi-va-sentinel",
            title="Tạo lỗi và lỗi sentinel",
            summary="errors.New cho lỗi tĩnh, fmt.Errorf cho lỗi có ngữ cảnh, và biến sentinel để người gọi so sánh.",
            level="beginner",
            tags=["loi", "kien-truc"],
            sections=[
                sec(
                    "Ba cách tạo lỗi",
                    '`errors.New("thông điệp")` cho lỗi cố định. `fmt.Errorf("...: %w", '
                    "err)` để bọc lỗi gốc kèm ngữ cảnh. Kiểu lỗi riêng khi người gọi cần "
                    "dữ liệu kèm theo, ví dụ tên trường không hợp lệ.",
                    "Sentinel là biến lỗi cấp package: `var ErrNotFound = errors.New(...)`. "
                    "Người gọi kiểm tra bằng `errors.Is(err, ErrNotFound)` để phân biệt "
                    "“không tìm thấy” với lỗi hạ tầng.",
                ),
                sec(
                    "Thông điệp lỗi viết thế nào",
                    "Quy ước: chữ thường, không dấu chấm cuối, không viết “failed to” vì "
                    "khi bọc nhiều tầng sẽ thành chuỗi lặp. Hãy viết như một mệnh đề mô tả "
                    'hành động: `"tạo hoá đơn: kết nối db: timeout"`.',
                    "Đừng đưa dữ liệu người dùng nhạy cảm vào thông điệp lỗi, vì nó sẽ "
                    "chảy vào log và có thể lên cả API response.",
                ),
            ],
            samples=[
                code(
                    "Sentinel và kiểm tra",
                    """
package store

var (
	ErrNotFound  = errors.New("không tìm thấy bản ghi")
	ErrDuplicate = errors.New("bản ghi đã tồn tại")
)

func (s *Postgres) User(ctx context.Context, id string) (User, error) {
	// ...
	if errors.Is(err, sql.ErrNoRows) {
		return User{}, fmt.Errorf("user %s: %w", id, ErrNotFound)
	}
	return u, nil
}
""",
                ),
                code(
                    "Phía người gọi",
                    """
u, err := store.User(ctx, id)
switch {
case errors.Is(err, store.ErrNotFound):
	http.Error(w, "không tồn tại", http.StatusNotFound)
case err != nil:
	http.Error(w, "lỗi hệ thống", http.StatusInternalServerError)
default:
	writeJSON(w, u)
}
""",
                ),
            ],
            takeaways=[
                "Sentinel cho phép phân loại lỗi mà không lộ chi tiết triển khai.",
                "Thông điệp lỗi: chữ thường, không dấu chấm, mô tả hành động.",
                "Không đưa dữ liệu nhạy cảm vào thông điệp lỗi.",
            ],
            exercises=["Định nghĩa `ErrQuotaExceeded` và xử lý nó thành HTTP 429 ở tầng handler."],
        ),
        lesson(
            slug="wrapping-va-errors-is-as",
            title="Bọc lỗi với %w, errors.Is và errors.As",
            summary="Chuỗi lỗi giữ nguyên nguyên nhân gốc trong khi mỗi tầng thêm ngữ cảnh của mình.",
            level="intermediate",
            tags=["loi", "kien-truc"],
            sections=[
                sec(
                    "%w tạo chuỗi",
                    '`fmt.Errorf("ngữ cảnh: %w", err)` tạo một lỗi mới có phương thức '
                    "`Unwrap()` trả về lỗi gốc. `errors.Is` đi dọc chuỗi để so sánh với "
                    "một sentinel; `errors.As` đi dọc chuỗi để tìm lỗi có kiểu cụ thể và "
                    "gán vào biến đích.",
                    "Dùng `%v` thay vì `%w` sẽ biến lỗi gốc thành chuỗi text và cắt đứt "
                    "chuỗi — người gọi không còn kiểm tra được nguyên nhân. Đó là quyết "
                    "định thiết kế: dùng `%v` khi bạn **muốn** che chi tiết nội bộ.",
                ),
                sec(
                    "Bọc ở đâu, bao nhiêu lần",
                    "Bọc khi vượt qua một ranh giới có ý nghĩa: từ tầng lưu trữ lên tầng "
                    "nghiệp vụ, từ nghiệp vụ lên handler. Không cần bọc ở mọi hàm; chuỗi "
                    "lỗi dài mười tầng lặp lại cùng thông tin thì vô dụng.",
                    "Từ Go 1.20, `errors.Join` gộp nhiều lỗi độc lập thành một, tiện khi "
                    "validate nhiều trường và muốn báo hết một lượt.",
                    note="Nguyên tắc: mỗi lần bọc phải thêm thông tin mà người đọc log chưa có.",
                ),
            ],
            samples=[
                code(
                    "Is, As và Join",
                    """
var target *ValidationError
err := createUser(ctx, input)

switch {
case errors.As(err, &target):
	fmt.Println("trường sai:", target.Field)
case errors.Is(err, store.ErrDuplicate):
	fmt.Println("email đã dùng")
}

// Gộp nhiều lỗi validate
var errs []error
if input.Email == "" {
	errs = append(errs, &ValidationError{Field: "email"})
}
if input.Age < 0 {
	errs = append(errs, &ValidationError{Field: "age"})
}
return errors.Join(errs...) // nil nếu slice rỗng
""",
                ),
            ],
            takeaways=[
                "`%w` giữ chuỗi lỗi; `%v` cắt chuỗi có chủ đích.",
                "`errors.Is` so với sentinel, `errors.As` lấy kiểu lỗi cụ thể.",
                "`errors.Join` báo nhiều lỗi validate một lượt.",
            ],
            exercises=[
                "Viết test dùng errors.As lấy ra danh sách trường sai từ một lỗi đã bọc hai tầng."
            ],
        ),
        lesson(
            slug="kieu-loi-tuy-chinh",
            title="Kiểu lỗi tuỳ chỉnh mang dữ liệu",
            summary="Khi người gọi cần hơn một thông điệp, hãy định nghĩa kiểu lỗi riêng.",
            level="intermediate",
            tags=["loi", "kien-truc"],
            sections=[
                sec(
                    "Thiết kế kiểu lỗi",
                    "Kiểu lỗi là struct thường, hiện thực `Error() string` và nên có "
                    "`Unwrap() error` nếu nó bọc lỗi khác. Đặt receiver con trỏ và trả về "
                    "`&MyError{...}` để so sánh kiểu hoạt động nhất quán.",
                    "Chỉ đưa vào các trường mà người gọi thật sự cần để ra quyết định: mã "
                    "lỗi, tên trường, thời gian nên thử lại. Đừng nhồi cả stack trace vào.",
                ),
                sec(
                    "Ánh xạ sang biên ngoài",
                    "Ở biên HTTP hoặc gRPC, bạn cần một hàm duy nhất biến lỗi nội bộ thành "
                    "mã trạng thái. Đặt hàm đó ở một chỗ, dùng errors.As/Is, và tuyệt đối "
                    "không rải logic ánh xạ khắp handler.",
                    "Lỗi trả cho client nên mô tả vấn đề mà không tiết lộ nội thất hệ "
                    "thống; ghi chi tiết vào log kèm một request id để tra cứu.",
                ),
            ],
            samples=[
                code(
                    "Kiểu lỗi có dữ liệu và Unwrap",
                    """
type QuotaError struct {
	Limit     int
	RetryAfter time.Duration
	cause     error
}

func (e *QuotaError) Error() string {
	return fmt.Sprintf("vượt giới hạn %d, thử lại sau %s", e.Limit, e.RetryAfter)
}

func (e *QuotaError) Unwrap() error { return e.cause }
""",
                ),
                code(
                    "Ánh xạ tập trung sang HTTP",
                    """
func statusFor(err error) int {
	var quota *QuotaError
	switch {
	case err == nil:
		return http.StatusOK
	case errors.As(err, &quota):
		return http.StatusTooManyRequests
	case errors.Is(err, store.ErrNotFound):
		return http.StatusNotFound
	case errors.Is(err, context.DeadlineExceeded):
		return http.StatusGatewayTimeout
	default:
		return http.StatusInternalServerError
	}
}
""",
                ),
            ],
            takeaways=[
                "Kiểu lỗi riêng khi người gọi cần dữ liệu để quyết định.",
                "Thêm `Unwrap()` để giữ chuỗi nguyên nhân.",
                "Ánh xạ lỗi sang mã trạng thái ở một nơi duy nhất.",
            ],
            exercises=["Viết `statusFor` cho ba loại lỗi của bạn và test bảng các trường hợp."],
        ),
        lesson(
            slug="panic-va-recover",
            title="panic, recover và ranh giới sử dụng",
            summary="Panic dành cho lỗi lập trình; recover chỉ dùng ở biên để không sập cả process.",
            level="intermediate",
            tags=["loi", "runtime"],
            sections=[
                sec(
                    "Khi nào panic là đúng",
                    "Panic khi bất biến của chương trình bị vi phạm và tiếp tục chạy sẽ "
                    "gây hại: cấu hình bắt buộc thiếu lúc khởi động, chỉ số vượt biên do "
                    "lỗi logic, trạng thái không thể xảy ra. Với lỗi dự đoán được như file "
                    "không tồn tại hay input sai, hãy trả về error.",
                    "Panic mang theo stack trace và làm sập goroutine hiện tại; nếu không "
                    "ai recover, cả process kết thúc.",
                ),
                sec(
                    "recover ở biên",
                    "Chỉ recover tại các ranh giới: middleware HTTP, worker của queue, "
                    "goroutine dài hạn. Recover xong phải ghi log kèm stack rồi trả lỗi "
                    "500 — đừng lặng lẽ tiếp tục như chưa có gì.",
                    "Điểm cực kỳ quan trọng: panic trong một goroutine **không** được "
                    "recover bởi hàm ở goroutine khác. Mỗi goroutine bạn tự khởi chạy đều "
                    "cần lớp bảo vệ riêng.",
                    note="net/http tự recover panic của handler, nhưng nó chỉ đóng kết nối; hãy tự viết middleware để có log và response tử tế.",
                ),
            ],
            samples=[
                code(
                    "Middleware recover",
                    """
func Recover(log *slog.Logger, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if rec := recover(); rec != nil {
				log.Error("panic",
					"value", rec,
					"path", r.URL.Path,
					"stack", string(debug.Stack()))
				http.Error(w, "lỗi hệ thống", http.StatusInternalServerError)
			}
		}()
		next.ServeHTTP(w, r)
	})
}
""",
                ),
                code(
                    "Goroutine cần bảo vệ riêng",
                    """
func safeGo(log *slog.Logger, fn func()) {
	go func() {
		defer func() {
			if rec := recover(); rec != nil {
				log.Error("panic trong goroutine", "value", rec)
			}
		}()
		fn()
	}()
}
""",
                    explanation="Không có lớp này, một panic trong worker sẽ giết toàn bộ process.",
                ),
            ],
            takeaways=[
                "Panic cho lỗi lập trình, error cho lỗi dự đoán được.",
                "Recover chỉ ở biên, luôn kèm log và stack.",
                "Mỗi goroutine tự khởi chạy cần lớp recover riêng.",
            ],
            exercises=[
                "Thêm middleware recover vào một server nhỏ và kích hoạt panic để kiểm tra log."
            ],
        ),
        lesson(
            slug="loi-tam-thoi-va-retry",
            title="Lỗi tạm thời, retry và backoff",
            summary="Không phải lỗi nào cũng nên thử lại; và thử lại sai cách thì làm sự cố nặng thêm.",
            level="advanced",
            tags=["loi", "van-hanh"],
            sections=[
                sec(
                    "Phân loại trước khi thử lại",
                    "Chỉ retry lỗi tạm thời và thao tác idempotent: timeout mạng, 503, "
                    "deadlock của DB. Không retry lỗi 4xx do input sai hay lỗi xác thực — "
                    "thử lại chỉ tốn tài nguyên.",
                    "Với thao tác không idempotent (tạo đơn hàng), cần idempotency key để "
                    "lần thử thứ hai không tạo bản ghi trùng.",
                ),
                sec(
                    "Backoff và jitter",
                    "Exponential backoff giãn khoảng chờ theo luỹ thừa; jitter thêm nhiễu "
                    "ngẫu nhiên để hàng nghìn client không cùng thử lại một lúc và tạo "
                    "sóng tải đồng bộ. Luôn giới hạn số lần thử và tôn trọng deadline của "
                    "context.",
                    "Ở quy mô lớn, hãy kết hợp circuit breaker: khi tỉ lệ lỗi vượt ngưỡng, "
                    "ngừng gọi hẳn một khoảng để hệ thống dưới có cơ hội hồi phục.",
                    note="Retry không có jitter là nguyên nhân kinh điển của “thundering herd” khi một service vừa hồi phục lại bị đánh sập ngay.",
                ),
            ],
            samples=[
                code(
                    "Retry với backoff, jitter và context",
                    """
func retry(ctx context.Context, attempts int, fn func() error) error {
	var err error
	delay := 100 * time.Millisecond
	for i := range attempts {
		if err = fn(); err == nil {
			return nil
		}
		if !isTransient(err) {
			return err
		}
		jitter := time.Duration(rand.Int64N(int64(delay / 2)))
		select {
		case <-time.After(delay + jitter):
		case <-ctx.Done():
			return errors.Join(err, ctx.Err())
		}
		delay *= 2
		_ = i
	}
	return fmt.Errorf("hết %d lần thử: %w", attempts, err)
}
""",
                ),
            ],
            takeaways=[
                "Chỉ retry lỗi tạm thời và thao tác idempotent.",
                "Backoff phải có jitter và tôn trọng context deadline.",
                "Circuit breaker bảo vệ hệ thống dưới khi lỗi kéo dài.",
            ],
            exercises=["Bổ sung `isTransient` phân loại lỗi mạng, 5xx và context.Canceled."],
        ),
        lesson(
            slug="ghi-log-loi-dung-cach",
            title="Ghi log lỗi đúng một lần",
            summary="Vừa log vừa trả lỗi lên trên là cách nhanh nhất để có log nhiễu gấp năm lần.",
            level="intermediate",
            tags=["loi", "van-hanh"],
            sections=[
                sec(
                    "Log hoặc trả về, đừng cả hai",
                    "Nếu hàm trả lỗi lên trên, người gọi sẽ xử lý và log. Nếu bạn cũng log "
                    "tại chỗ, mỗi lỗi xuất hiện nhiều lần với ngữ cảnh chồng chéo. Quy tắc: "
                    "chỉ log tại nơi cuối cùng xử lý lỗi, thường là handler hoặc main.",
                    "Ở các tầng giữa, hãy bọc lỗi để thêm ngữ cảnh — đó là “log” của tầng "
                    "đó, nhưng gọn và có cấu trúc.",
                ),
                sec(
                    "Log có cấu trúc với slog",
                    "`log/slog` trong thư viện chuẩn cho log dạng key–value, xuất được JSON "
                    "để hệ thống thu thập phân tích. Đính kèm request id, user id, tên "
                    "thao tác; đừng nhồi cả câu văn dài vào một field message.",
                    "Đặt mức log hợp lý: Error cho việc cần người can thiệp, Warn cho bất "
                    "thường tự phục hồi, Info cho mốc nghiệp vụ, Debug cho chi tiết chỉ bật "
                    "khi điều tra.",
                    note="Nếu mọi thứ đều là Error thì không gì là Error. Hãy giữ mức Error cho những gì thật sự cần người trực xem.",
                ),
            ],
            samples=[
                code(
                    "slog với ngữ cảnh",
                    """
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
	Level: slog.LevelInfo,
}))

reqLog := logger.With("request_id", reqID, "user_id", userID)

if err := svc.Charge(ctx, walletID, 1500); err != nil {
	reqLog.Error("charge thất bại", "wallet_id", walletID, "err", err)
	http.Error(w, "không thể thanh toán", statusFor(err))
	return
}
reqLog.Info("charge thành công", "wallet_id", walletID)
""",
                    output='{"time":"...","level":"ERROR","msg":"charge thất bại","request_id":"r-1","err":"..."}',
                ),
            ],
            takeaways=[
                "Chỉ log lỗi ở nơi cuối cùng xử lý nó.",
                "Các tầng giữa bọc lỗi thay vì log.",
                "slog cho log key–value, dễ truy vấn ở hệ thống tập trung.",
            ],
            exercises=["Rà một luồng xử lý và loại bỏ các lời gọi log trùng lặp cho cùng một lỗi."],
        ),
    ],
)
