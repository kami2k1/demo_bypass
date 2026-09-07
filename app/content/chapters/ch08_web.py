"""Chương 8 — Web với net/http."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="web",
    title="Web với net/http",
    summary=(
        "Thư viện chuẩn đủ để chạy production: routing, middleware, template, "
        "client có timeout, graceful shutdown và các mặc định an toàn."
    ),
    lessons=[
        lesson(
            slug="net-http-server-dau-tien",
            title="Server đầu tiên với net/http",
            summary="Một goroutine cho mỗi kết nối, và vì goroutine rẻ nên mô hình đơn giản này chịu tải rất tốt.",
            level="beginner",
            tags=["web", "net-http"],
            sections=[
                sec(
                    "Mô hình xử lý",
                    "`http.Server` chấp nhận kết nối trong một vòng lặp và khởi chạy một "
                    "goroutine cho mỗi kết nối. Không có event loop, không có callback: "
                    "handler của bạn viết theo lối tuần tự, dễ đọc, trong khi hàng nghìn "
                    "kết nối vẫn được xử lý song song.",
                    "Đây là chỗ mô hình goroutine trả cổ tức lớn nhất: code đồng bộ nhưng "
                    "khả năng đồng thời của hệ thống bất đồng bộ.",
                ),
                sec(
                    "Handler là một interface",
                    "`http.Handler` chỉ có `ServeHTTP(ResponseWriter, *Request)`. "
                    "`http.HandlerFunc` là adapter biến một hàm thành Handler. Toàn bộ hệ "
                    "sinh thái middleware của Go dựa trên hai kiểu này.",
                    "Đừng dùng `http.ListenAndServe` với DefaultServeMux ở production: hãy "
                    "tạo `http.Server` tường minh để đặt được timeout — mặc định của nó là "
                    "không giới hạn.",
                    note="Server không timeout là lỗ hổng cạn tài nguyên: một client chậm có thể giữ kết nối vô hạn.",
                ),
            ],
            samples=[
                code(
                    "Server có timeout tường minh",
                    """
func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		fmt.Fprintln(w, "ok")
	})

	srv := &http.Server{
		Addr:              ":8080",
		Handler:           mux,
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       15 * time.Second,
		WriteTimeout:      15 * time.Second,
		IdleTimeout:       60 * time.Second,
	}
	log.Fatal(srv.ListenAndServe())
}
""",
                ),
            ],
            takeaways=[
                "Một goroutine cho mỗi kết nối: code đồng bộ, hệ thống đồng thời.",
                "Handler là interface một phương thức, nền tảng của middleware.",
                "Luôn tạo http.Server tường minh để đặt timeout.",
            ],
            exercises=[
                "Khởi chạy server rồi dùng `ab` hoặc `hey` bắn 1000 request đồng thời và quan sát."
            ],
        ),
        lesson(
            slug="routing-servemux",
            title="Routing với ServeMux (Go 1.22+)",
            summary="ServeMux nay hỗ trợ method và tham số đường dẫn — đủ cho phần lớn API mà không cần router ngoài.",
            level="beginner",
            tags=["web", "net-http"],
            sections=[
                sec(
                    "Mẫu đường dẫn mới",
                    "Từ Go 1.22, pattern có thể chứa method và wildcard: "
                    '`"GET /users/{id}"`. Lấy giá trị bằng `r.PathValue("id")`. Wildcard '
                    "cuối dạng `{path...}` khớp phần còn lại của đường dẫn.",
                    "Quy tắc ưu tiên: pattern cụ thể hơn thắng, không phụ thuộc thứ tự đăng "
                    "ký. Hai pattern xung đột mà không ai cụ thể hơn sẽ gây panic lúc đăng "
                    "ký — lỗi được phát hiện ngay khi khởi động.",
                ),
                sec(
                    "Còn cần router ngoài không?",
                    "Với API REST thông thường thì không. Router ngoài (chi, gin, echo) vẫn "
                    "hữu ích khi bạn cần nhóm route với middleware theo nhóm, ràng buộc regex "
                    "cho tham số, hoặc hệ sinh thái middleware sẵn có.",
                    "Chiến lược thực dụng: bắt đầu bằng ServeMux; chỉ thêm phụ thuộc khi bạn "
                    "gặp một nhu cầu cụ thể mà nó không đáp ứng.",
                    note='Đăng ký `"/"` khớp mọi đường dẫn chưa có route khác, nên đó chính là nơi đặt handler 404 của bạn.',
                ),
            ],
            samples=[
                code(
                    "Method và tham số đường dẫn",
                    """
mux := http.NewServeMux()

mux.HandleFunc("GET /users/{id}", func(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	fmt.Fprintf(w, "user %s", id)
})

mux.HandleFunc("POST /users", createUser)
mux.HandleFunc("GET /files/{path...}", serveFile)
mux.HandleFunc("/", notFound) // bắt mọi đường dẫn còn lại
""",
                ),
                code(
                    "Nhóm route bằng prefix",
                    """
api := http.NewServeMux()
api.HandleFunc("GET /users/{id}", getUser)

root := http.NewServeMux()
root.Handle("/api/v1/", http.StripPrefix("/api/v1", api))
""",
                    explanation="StripPrefix cho phép mount một mux con, cách gom nhóm route mà không cần thư viện.",
                ),
            ],
            takeaways=[
                "Pattern hỗ trợ method và `{param}`, đọc bằng `r.PathValue`.",
                "Pattern cụ thể hơn thắng, không phụ thuộc thứ tự đăng ký.",
                "StripPrefix + mux con để nhóm route.",
            ],
            exercises=["Viết CRUD bốn route cho `/notes` chỉ dùng ServeMux và test bằng httptest."],
        ),
        lesson(
            slug="handler-va-middleware",
            title="Middleware: hàm bọc handler",
            summary="Middleware trong Go chỉ là hàm nhận Handler và trả Handler — không có magic, không có framework.",
            level="intermediate",
            tags=["web", "kien-truc"],
            sections=[
                sec(
                    "Chữ ký chuẩn",
                    "`func(next http.Handler) http.Handler`. Vì đây là quy ước cộng đồng, "
                    "middleware từ các thư viện khác nhau ghép được với nhau và với code của "
                    "bạn mà không cần adapter.",
                    "Thứ tự bọc quyết định thứ tự chạy: middleware ngoài cùng nhận request "
                    "trước và ghi response sau. Recover nên ở ngoài cùng, còn logging thường "
                    "ngay sau nó để đo được cả thời gian của các tầng trong.",
                ),
                sec(
                    "Bắt status code",
                    "`ResponseWriter` không cho đọc lại status đã ghi. Muốn log status, hãy "
                    "bọc nó bằng một struct ghi nhận lại WriteHeader. Lưu ý nếu handler gọi "
                    "Write mà chưa gọi WriteHeader thì status là 200.",
                    "Nếu wrapper của bạn cần hỗ trợ streaming hay hijack, hãy hiện thực thêm "
                    "`http.Flusher`, hoặc dùng `http.NewResponseController` từ Go 1.20 để "
                    "truy cập các khả năng đó một cách an toàn.",
                ),
            ],
            samples=[
                code(
                    "Middleware ghi log có status",
                    """
type statusRecorder struct {
	http.ResponseWriter
	status int
}

func (r *statusRecorder) WriteHeader(code int) {
	r.status = code
	r.ResponseWriter.WriteHeader(code)
}

func Logging(log *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			rec := &statusRecorder{ResponseWriter: w, status: http.StatusOK}
			next.ServeHTTP(rec, r)
			log.Info("request",
				"method", r.Method,
				"path", r.URL.Path,
				"status", rec.status,
				"duration_ms", time.Since(start).Milliseconds())
		})
	}
}
""",
                ),
                code(
                    "Ghép chuỗi middleware",
                    """
func chain(h http.Handler, mws ...func(http.Handler) http.Handler) http.Handler {
	for i := len(mws) - 1; i >= 0; i-- {
		h = mws[i](h)
	}
	return h
}

handler := chain(mux, Recover(log), Logging(log), RequestID())
""",
                    explanation="Bọc từ phải sang trái để thứ tự tham số trùng với thứ tự chạy.",
                ),
            ],
            takeaways=[
                "Middleware = `func(http.Handler) http.Handler`, quy ước toàn hệ sinh thái.",
                "Thứ tự bọc quyết định thứ tự chạy; Recover ở ngoài cùng.",
                "Bọc ResponseWriter để ghi nhận status cho log.",
            ],
            exercises=["Viết middleware giới hạn tần suất theo IP dùng map + mutex."],
        ),
        lesson(
            slug="html-template",
            title="html/template và chống XSS",
            summary="Template của Go tự escape theo ngữ cảnh — HTML, JS, URL đều được xử lý đúng cách.",
            level="intermediate",
            tags=["web", "bao-mat", "template"],
            sections=[
                sec(
                    "Escape theo ngữ cảnh",
                    "`html/template` phân tích cấu trúc HTML và escape khác nhau tuỳ nơi giá "
                    "trị được chèn: trong thân HTML, trong thuộc tính, trong JavaScript, "
                    "trong URL. Đó là lý do bạn phải dùng html/template chứ không phải "
                    "text/template cho web.",
                    "Muốn chèn HTML thô, phải bọc trong `template.HTML` — một hành động tường "
                    "minh, dễ soát trong code review. Đừng bao giờ bọc dữ liệu do người dùng "
                    "nhập.",
                ),
                sec(
                    "Tổ chức template",
                    "`template.Must(template.ParseFS(...))` phân tích một lần lúc khởi động; "
                    "lỗi cú pháp lộ ra ngay chứ không đợi request đầu tiên. Dùng "
                    "`{{define}}`/`{{template}}` để có layout chung và block nội dung.",
                    "Truyền vào template một struct dữ liệu tường minh, không phải map chung "
                    "chung — compiler không kiểm tra template, nên struct rõ ràng giúp bạn "
                    "biết trang cần gì.",
                    note="Template được thực thi lúc chạy nên lỗi tên trường chỉ hiện khi render; hãy có test render mọi trang.",
                ),
            ],
            samples=[
                code(
                    "Layout và escape tự động",
                    """
//go:embed templates/*.html
var tmplFS embed.FS

var templates = template.Must(template.ParseFS(tmplFS, "templates/*.html"))

type pageData struct {
	Title string
	Query string // dữ liệu người dùng nhập
}

func search(w http.ResponseWriter, r *http.Request) {
	data := pageData{Title: "Tìm kiếm", Query: r.URL.Query().Get("q")}
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	if err := templates.ExecuteTemplate(w, "search.html", data); err != nil {
		http.Error(w, "lỗi render", http.StatusInternalServerError)
	}
}
""",
                ),
                code(
                    "Đầu vào tấn công được xử lý",
                    """
<!-- template -->
<p>Bạn tìm: {{ .Query }}</p>

<!-- với q=<script>alert(1)</script> kết quả render là: -->
<p>Bạn tìm: &lt;script&gt;alert(1)&lt;/script&gt;</p>
""",
                    language="html",
                    explanation="Không cần làm gì thêm: escape là mặc định, không phải tuỳ chọn.",
                ),
            ],
            takeaways=[
                "html/template escape theo ngữ cảnh chèn giá trị.",
                "Parse template lúc khởi động bằng template.Must.",
                "Chỉ dùng template.HTML cho nội dung bạn tự sinh, không cho input người dùng.",
            ],
            exercises=[
                "Render một trang với input `<img onerror=alert(1)>` và kiểm tra HTML đầu ra."
            ],
        ),
        lesson(
            slug="phuc-vu-file-tinh",
            title="Phục vụ file tĩnh",
            summary="FileServer, cache header và những cạm bẫy về đường dẫn.",
            level="beginner",
            tags=["web", "net-http"],
            sections=[
                sec(
                    "FileServer và StripPrefix",
                    '`http.FileServer(http.Dir("static"))` phục vụ một thư mục. Vì '
                    "FileServer nhận đường dẫn nguyên vẹn từ URL, bạn cần "
                    '`http.StripPrefix("/static/", ...)` để nó không tìm file '
                    "`static/static/app.css`.",
                    "Từ Go 1.22, `http.FileServerFS` nhận `fs.FS`, dùng trực tiếp với "
                    "`embed.FS`. Nó cũng tự xử lý Range request và ETag dựa trên thời gian "
                    "sửa file.",
                ),
                sec(
                    "Cache và bảo mật",
                    "Đặt `Cache-Control: public, max-age=31536000, immutable` cho tài nguyên "
                    "có hash trong tên file, và `no-cache` cho HTML. Không có hash thì đừng "
                    "cache lâu, vì bạn sẽ không có cách nào buộc client tải bản mới.",
                    "FileServer đã chặn `..` để không thoát khỏi thư mục gốc. Nhưng nếu bạn "
                    "tự nối đường dẫn từ tham số URL, hãy dùng `filepath.Clean` và kiểm tra "
                    "tiền tố — đây là lớp lỗi path traversal kinh điển.",
                    note="Đừng phục vụ cả thư mục dự án. Chỉ mở đúng thư mục static, và đừng để file .env hay backup nằm trong đó.",
                ),
            ],
            samples=[
                code(
                    "Static với cache header",
                    """
//go:embed static
var staticFS embed.FS

func staticHandler() http.Handler {
	sub, _ := fs.Sub(staticFS, "static")
	fileServer := http.FileServerFS(sub)

	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if strings.HasSuffix(r.URL.Path, ".css") || strings.HasSuffix(r.URL.Path, ".js") {
			w.Header().Set("Cache-Control", "public, max-age=86400")
		}
		fileServer.ServeHTTP(w, r)
	})
}

mux.Handle("/static/", http.StripPrefix("/static/", staticHandler()))
""",
                ),
            ],
            takeaways=[
                "Cần StripPrefix khi mount FileServer dưới một prefix.",
                "FileServerFS dùng trực tiếp với embed.FS.",
                "Cache dài chỉ an toàn khi tên file có hash phiên bản.",
            ],
            exercises=["Thêm hash nội dung vào tên file CSS và bật cache một năm."],
        ),
        lesson(
            slug="json-api-va-validate",
            title="Xây JSON API và kiểm tra dữ liệu vào",
            summary="Decode có giới hạn, validate tường minh, và trả lỗi theo một hình dạng thống nhất.",
            level="intermediate",
            tags=["web", "api", "bao-mat"],
            sections=[
                sec(
                    "Nhận dữ liệu an toàn",
                    "Ba việc bắt buộc ở mọi endpoint nhận JSON: giới hạn kích thước body "
                    "(`http.MaxBytesReader`), từ chối trường lạ (`DisallowUnknownFields`), và "
                    "kiểm tra Content-Type. Thiếu bất kỳ điều nào cũng mở ra một lớp sự cố.",
                    "Tách kiểu request (DTO) khỏi kiểu miền nghiệp vụ. Nếu dùng chung, một "
                    "trường nội bộ như `IsAdmin` có thể bị client gán qua JSON — lỗ hổng "
                    "mass assignment.",
                ),
                sec(
                    "Hình dạng lỗi thống nhất",
                    "Định nghĩa một struct lỗi duy nhất cho API và một hàm helper để ghi nó. "
                    "Client chỉ cần viết một bộ xử lý lỗi, và bạn không bị rò rỉ thông điệp "
                    "nội bộ ra ngoài.",
                    "Validate nên trả về danh sách lỗi theo trường thay vì dừng ở lỗi đầu "
                    "tiên: người dùng sửa được một lượt thay vì thử lại năm lần.",
                ),
            ],
            samples=[
                code(
                    "Handler đầy đủ với validate",
                    """
type createNoteRequest struct {
	Title string `json:"title"`
	Body  string `json:"body"`
}

func (r createNoteRequest) validate() map[string]string {
	problems := map[string]string{}
	if strings.TrimSpace(r.Title) == "" {
		problems["title"] = "không được để trống"
	}
	if len(r.Body) > 10_000 {
		problems["body"] = "tối đa 10000 ký tự"
	}
	return problems
}

func createNote(w http.ResponseWriter, r *http.Request) {
	if r.Header.Get("Content-Type") != "application/json" {
		writeError(w, http.StatusUnsupportedMediaType, "cần application/json", nil)
		return
	}

	var in createNoteRequest
	dec := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20))
	dec.DisallowUnknownFields()
	if err := dec.Decode(&in); err != nil {
		writeError(w, http.StatusBadRequest, "JSON không hợp lệ", nil)
		return
	}
	if problems := in.validate(); len(problems) > 0 {
		writeError(w, http.StatusUnprocessableEntity, "dữ liệu không hợp lệ", problems)
		return
	}
	// ... lưu và trả 201
}
""",
                ),
                code(
                    "Helper lỗi dùng chung",
                    """
type apiError struct {
	Message  string            `json:"message"`
	Problems map[string]string `json:"problems,omitempty"`
}

func writeError(w http.ResponseWriter, status int, msg string, problems map[string]string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(apiError{Message: msg, Problems: problems})
}
""",
                ),
            ],
            takeaways=[
                "Luôn giới hạn body, chặn trường lạ, kiểm tra Content-Type.",
                "Tách DTO khỏi kiểu miền để tránh mass assignment.",
                "Một hình dạng lỗi duy nhất cho toàn bộ API.",
            ],
            exercises=["Viết test bảng cho `validate` với 5 trường hợp đầu vào khác nhau."],
        ),
        lesson(
            slug="cookie-va-session",
            title="Cookie, session và CSRF",
            summary="Cờ cookie đúng, session lưu ở đâu, và vì sao CSRF token vẫn cần thiết.",
            level="advanced",
            tags=["web", "bao-mat"],
            sections=[
                sec(
                    "Cờ cookie bắt buộc",
                    "`HttpOnly` chặn JavaScript đọc cookie, `Secure` buộc chỉ gửi qua HTTPS, "
                    "`SameSite=Lax` (hoặc Strict) chặn phần lớn CSRF, `Path` và `MaxAge` giới "
                    "hạn phạm vi và tuổi. Thiếu HttpOnly là biến mọi lỗ XSS thành chiếm "
                    "phiên đăng nhập.",
                    "Session id phải sinh từ `crypto/rand`, không phải `math/rand`. Đủ dài "
                    "(32 byte) để không thể đoán.",
                ),
                sec(
                    "Lưu session ở đâu",
                    "Server-side (Redis, DB) cho phép thu hồi phiên ngay lập tức nhưng cần "
                    "thêm hạ tầng. Cookie có chữ ký hoặc mã hoá thì không cần lưu trữ, nhưng "
                    "không thu hồi được trước khi hết hạn — hãy giữ thời hạn ngắn và có "
                    "refresh token.",
                    "Xoay session id ngay sau khi đăng nhập thành công để chặn session "
                    "fixation. Với thao tác đổi dữ liệu, thêm CSRF token dạng "
                    "double-submit hoặc synchroniser token.",
                    note="SameSite=Lax không bảo vệ request GET gây thay đổi trạng thái. Đó là một lý do nữa để GET luôn chỉ đọc.",
                ),
            ],
            samples=[
                code(
                    "Đặt cookie session an toàn",
                    """
func newSessionID() (string, error) {
	b := make([]byte, 32)
	if _, err := rand.Read(b); err != nil { // crypto/rand
		return "", err
	}
	return base64.RawURLEncoding.EncodeToString(b), nil
}

func setSession(w http.ResponseWriter, id string) {
	http.SetCookie(w, &http.Cookie{
		Name:     "sid",
		Value:    id,
		Path:     "/",
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteLaxMode,
		MaxAge:   int((24 * time.Hour).Seconds()),
	})
}
""",
                ),
            ],
            takeaways=[
                "HttpOnly + Secure + SameSite là mức tối thiểu cho cookie phiên.",
                "Session id sinh từ crypto/rand, dài ít nhất 32 byte.",
                "Xoay session id sau khi đăng nhập; thêm CSRF token cho thao tác ghi.",
            ],
            exercises=[
                "Thêm CSRF token dạng double-submit vào một form POST và test cả hai nhánh."
            ],
        ),
        lesson(
            slug="http-client-va-timeout",
            title="HTTP client: timeout và tái sử dụng kết nối",
            summary="`http.DefaultClient` không có timeout — đó là mặc định bạn phải sửa ngay.",
            level="intermediate",
            tags=["web", "net-http", "van-hanh"],
            sections=[
                sec(
                    "Client dùng chung, không tạo mỗi lần",
                    "Tạo một `*http.Client` ở cấp package hoặc tiêm vào struct. Client giữ "
                    "connection pool; tạo client mới cho mỗi request sẽ mở lại TCP và TLS "
                    "handshake mỗi lần, đắt hơn nhiều lần.",
                    "Đặt `Timeout` trên client cho toàn bộ chu trình, và cấu hình Transport "
                    "cho các mốc chi tiết: dial, TLS handshake, response header. Kết hợp với "
                    "context cho từng request.",
                ),
                sec(
                    "Đọc và đóng body",
                    "Luôn `defer resp.Body.Close()`, kể cả khi không cần dữ liệu — nếu không, "
                    "kết nối không được trả về pool và bạn sẽ cạn file descriptor. Nếu bỏ qua "
                    "nội dung, hãy `io.Copy(io.Discard, resp.Body)` trước khi đóng để kết nối "
                    "được tái sử dụng.",
                    "Kiểm tra `resp.StatusCode`: một lỗi 500 từ server **không** làm "
                    "`client.Do` trả về error. Đây là chỗ rất nhiều bug lọt qua.",
                    note="MaxIdleConnsPerHost mặc định là 2. Với service gọi dày đặc một backend, hãy tăng nó lên rõ ràng.",
                ),
            ],
            samples=[
                code(
                    "Client cấu hình đúng",
                    """
var httpClient = &http.Client{
	Timeout: 10 * time.Second,
	Transport: &http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 20,
		IdleConnTimeout:     90 * time.Second,
		DialContext: (&net.Dialer{
			Timeout: 3 * time.Second,
		}).DialContext,
		TLSHandshakeTimeout:   3 * time.Second,
		ResponseHeaderTimeout: 5 * time.Second,
	},
}

func fetchUser(ctx context.Context, id string) (User, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, "https://api.example.com/users/"+id, nil)
	if err != nil {
		return User{}, err
	}
	resp, err := httpClient.Do(req)
	if err != nil {
		return User{}, fmt.Errorf("gọi API: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		io.Copy(io.Discard, resp.Body)
		return User{}, fmt.Errorf("API trả về %d", resp.StatusCode)
	}
	var u User
	return u, json.NewDecoder(resp.Body).Decode(&u)
}
""",
                ),
            ],
            takeaways=[
                "Dùng một client chung để tái sử dụng connection pool.",
                "Luôn đóng body; đọc cạn nếu muốn kết nối được tái dùng.",
                "Status 5xx không phải error — phải tự kiểm tra StatusCode.",
            ],
            exercises=["Viết wrapper `getJSON[T any]` dùng generics và test bằng httptest.Server."],
        ),
        lesson(
            slug="graceful-shutdown",
            title="Graceful shutdown",
            summary="Nhận SIGTERM, ngừng nhận request mới, chờ request đang chạy, rồi đóng tài nguyên.",
            level="intermediate",
            tags=["web", "van-hanh"],
            sections=[
                sec(
                    "Vì sao quan trọng",
                    "Khi Kubernetes rolling update, pod nhận SIGTERM. Nếu process thoát ngay, "
                    "các request đang xử lý bị ngắt giữa đường: client thấy lỗi 502, "
                    "transaction có thể dở dang. Graceful shutdown biến việc triển khai thành "
                    "vô hình với người dùng.",
                    "`srv.Shutdown(ctx)` đóng listener, không nhận kết nối mới, và chờ các "
                    "handler đang chạy kết thúc tới khi ctx hết hạn.",
                ),
                sec(
                    "Thứ tự dọn dẹp",
                    "Đúng thứ tự: (1) dừng nhận request mới, (2) chờ request đang chạy xong, "
                    "(3) đóng worker và consumer, (4) đóng kết nối DB và cache. Đảo thứ tự — "
                    "ví dụ đóng DB trước — sẽ làm các request cuối cùng thất bại.",
                    "Thời gian chờ nên nhỏ hơn `terminationGracePeriodSeconds` của "
                    "orchestrator, nếu không process vẫn bị SIGKILL giữa lúc dọn dẹp.",
                    note="Nếu có health check, hãy cho nó trả về không-ready ngay khi bắt đầu shutdown để load balancer rút pod khỏi vòng xoay.",
                ),
            ],
            samples=[
                code(
                    "Shutdown đầy đủ",
                    """
func run(ctx context.Context, srv *http.Server, db *sql.DB, log *slog.Logger) error {
	ctx, stop := signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)
	defer stop()

	errc := make(chan error, 1)
	go func() {
		log.Info("server đang lắng nghe", "addr", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errc <- err
		}
	}()

	select {
	case err := <-errc:
		return err
	case <-ctx.Done():
		log.Info("nhận tín hiệu dừng, bắt đầu shutdown")
	}

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()

	if err := srv.Shutdown(shutdownCtx); err != nil {
		return fmt.Errorf("shutdown http: %w", err)
	}
	return db.Close()
}
""",
                ),
            ],
            takeaways=[
                "`signal.NotifyContext` biến tín hiệu hệ điều hành thành huỷ context.",
                "Shutdown ngừng nhận kết nối mới rồi chờ handler đang chạy.",
                "Đóng tài nguyên sau HTTP server, không trước.",
            ],
            exercises=["Thêm graceful shutdown cho worker pool đọc từ queue, dùng cùng context."],
        ),
        lesson(
            slug="bao-mat-web-co-ban",
            title="Mặc định an toàn cho web service",
            summary="Header bảo mật, giới hạn tần suất, bí mật ngoài code — danh sách kiểm tra tối thiểu.",
            level="advanced",
            tags=["web", "bao-mat", "van-hanh"],
            sections=[
                sec(
                    "Header và cấu hình",
                    "Đặt `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, "
                    "`Referrer-Policy`, `Strict-Transport-Security` khi chạy HTTPS. Một "
                    "middleware duy nhất đặt tất cả, để không endpoint nào bị bỏ sót.",
                    "Không bao giờ đặt bí mật trong code hay repo. Đọc từ biến môi trường "
                    "hoặc secret manager; log ra thì phải che. Với dữ liệu người dùng, kiểm "
                    "tra ở biên và dùng truy vấn tham số hoá để chặn SQL injection.",
                ),
                sec(
                    "Giới hạn tài nguyên",
                    "Mỗi biên nhận dữ liệu cần một giới hạn: kích thước body, số request mỗi "
                    "giây theo IP hoặc theo API key, timeout cho mọi thao tác I/O, số kết nối "
                    "DB. Không có giới hạn nghĩa là một client là đủ để làm sập service.",
                    "Đưa các giới hạn này vào cấu hình để điều chỉnh được mà không phải build "
                    "lại — nhưng luôn có giá trị mặc định an toàn.",
                    note="Danh sách kiểm tra tối thiểu: timeout, giới hạn body, rate limit, header bảo mật, bí mật ngoài code, truy vấn tham số hoá.",
                ),
            ],
            samples=[
                code(
                    "Middleware header bảo mật",
                    """
func SecurityHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		h := w.Header()
		h.Set("X-Content-Type-Options", "nosniff")
		h.Set("Referrer-Policy", "strict-origin-when-cross-origin")
		h.Set("Content-Security-Policy", "default-src 'self'")
		if r.TLS != nil {
			h.Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
		}
		next.ServeHTTP(w, r)
	})
}
""",
                ),
                code(
                    "Truy vấn tham số hoá",
                    """
// ĐÚNG: driver tự escape
row := db.QueryRowContext(ctx, "SELECT id, email FROM users WHERE email = $1", email)

// SAI: nối chuỗi mở đường cho SQL injection
// query := "SELECT id FROM users WHERE email = '" + email + "'"
""",
                ),
            ],
            takeaways=[
                "Một middleware đặt toàn bộ header bảo mật.",
                "Mọi biên nhận dữ liệu phải có giới hạn tài nguyên.",
                "Truy vấn tham số hoá và bí mật nằm ngoài repo là điều không thương lượng.",
            ],
            exercises=[
                "Rà một service của bạn theo danh sách kiểm tra trên và ghi lại điểm còn thiếu."
            ],
        ),
    ],
)
