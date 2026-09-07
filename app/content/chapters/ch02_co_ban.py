"""Chương 2 — Cú pháp nền tảng."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="co-ban-ngon-ngu",
    title="Cú pháp nền tảng",
    summary=(
        "Biến, hằng, kiểu số, điều khiển luồng, hàm và defer — bộ cú pháp nhỏ "
        "mà mọi dòng Go về sau đều dựa lên."
    ),
    lessons=[
        lesson(
            slug="bien-va-khai-bao",
            title="Biến và các cách khai báo",
            summary="Ba cách khai báo biến và quy tắc chọn cách nào trong từng ngữ cảnh.",
            level="beginner",
            tags=["co-ban", "cu-phap"],
            sections=[
                sec(
                    "var, := và khối var",
                    "`var x int` khai báo tường minh kèm kiểu và nhận zero value. "
                    "`x := 10` suy diễn kiểu từ giá trị, chỉ dùng được trong hàm. "
                    "Khối `var (...)` gom nhiều khai báo cấp package cho gọn.",
                    "Quy ước thực dụng: dùng `:=` trong thân hàm, dùng `var` khi cần "
                    "nêu rõ kiểu hoặc khi muốn zero value làm điểm bắt đầu.",
                ),
                sec(
                    "Biến không dùng là lỗi",
                    "Compiler từ chối biên dịch nếu một biến cục bộ được khai báo mà "
                    "không đọc tới. Điều này chặn tình trạng code chết tích tụ và giúp "
                    "phát hiện lỗi gõ sai tên biến ngay lập tức.",
                    "Nếu thật sự cần bỏ một giá trị, gán vào `_` — định danh trống.",
                    note="Biến cấp package không dùng thì không bị báo lỗi; chỉ biến cục bộ mới bị.",
                ),
            ],
            samples=[
                code(
                    "Ba cách khai báo",
                    """
package main

import "fmt"

var appName = "golang-tour"

var (
	maxRetry int    = 3
	logLevel string = "info"
)

func main() {
	port := 8080
	var timeout int // zero value: 0
	_, ok := map[string]int{"a": 1}["b"]
	fmt.Println(appName, maxRetry, logLevel, port, timeout, ok)
}
""",
                    output="golang-tour 3 info 8080 0 false",
                ),
            ],
            takeaways=[
                "`:=` cho code trong hàm, `var` khi cần kiểu tường minh.",
                "Biến cục bộ không dùng là lỗi biên dịch.",
                "`_` là nơi để bỏ giá trị không cần.",
            ],
            exercises=["Khai báo một biến cục bộ rồi không dùng, đọc lỗi compiler."],
        ),
        lesson(
            slug="hang-so-va-iota",
            title="Hằng số và iota",
            summary="Hằng số Go được tính lúc biên dịch và có thể không mang kiểu, tạo nên sự linh hoạt bất ngờ.",
            level="beginner",
            tags=["co-ban", "cu-phap"],
            sections=[
                sec(
                    "Hằng không kiểu",
                    "`const Pi = 3.14159` chưa mang kiểu; nó nhận kiểu tại điểm sử dụng. "
                    "Nhờ vậy cùng một hằng có thể gán cho float32 hay float64 mà không "
                    "cần chuyển đổi tường minh.",
                    "Hằng số được tính toán với độ chính xác lớn tại thời điểm biên dịch, "
                    "nên `const big = 1 << 40` hợp lệ ngay cả khi bạn đang ở nền 32-bit, "
                    "miễn là giá trị cuối cùng khớp kiểu đích.",
                ),
                sec(
                    "iota cho enum",
                    "Trong một khối `const`, `iota` đếm từ 0 và tăng theo từng dòng. Đây "
                    "là cách tạo enum tiêu chuẩn của Go. Kết hợp với một kiểu riêng và "
                    "phương thức `String()`, bạn có enum an toàn kiểu và in ra đọc được.",
                    "Mẹo hay dùng: `_ = iota` để bỏ giá trị 0, hoặc `1 << iota` để tạo bitmask.",
                ),
            ],
            samples=[
                code(
                    "Enum với iota và String()",
                    """
type Status int

const (
	StatusPending Status = iota
	StatusActive
	StatusSuspended
)

func (s Status) String() string {
	switch s {
	case StatusPending:
		return "pending"
	case StatusActive:
		return "active"
	case StatusSuspended:
		return "suspended"
	}
	return "unknown"
}
""",
                    output="fmt.Println(StatusActive) // active",
                ),
                code(
                    "Bitmask",
                    """
const (
	CanRead = 1 << iota // 1
	CanWrite            // 2
	CanDelete           // 4
)

perm := CanRead | CanWrite
""",
                ),
            ],
            takeaways=[
                "Hằng không kiểu tự thích ứng theo ngữ cảnh sử dụng.",
                "`iota` là công cụ tạo enum chuẩn của Go.",
                "Thêm `String()` để enum in ra dễ đọc trong log.",
            ],
            exercises=["Tạo enum `Priority` ba mức kèm `String()` và in thử bằng `%v`."],
        ),
        lesson(
            slug="kieu-so-va-chuyen-doi",
            title="Kiểu số và chuyển đổi tường minh",
            summary="Go không tự động ép kiểu số: mọi chuyển đổi phải viết ra, và đó là lý do ít lỗi tràn ngầm.",
            level="beginner",
            tags=["co-ban", "kieu-du-lieu"],
            sections=[
                sec(
                    "Danh mục kiểu",
                    "Số nguyên có dấu: int8, int16, int32, int64 và `int` (kích thước "
                    "theo nền tảng, thường 64 bit). Không dấu: uint8…uint64, uintptr. "
                    "Thực: float32, float64. Phức: complex64, complex128. `byte` là bí "
                    "danh của uint8, `rune` là bí danh của int32.",
                    "Mặc định hãy dùng `int` cho chỉ số và số đếm, `int64` khi cần chắc "
                    "chắn phạm vi (ví dụ số tiền theo cents), `float64` cho số thực.",
                ),
                sec(
                    "Không có ép kiểu ngầm",
                    "`var i int32 = 5; var j int64 = i` là lỗi. Phải viết "
                    "`j := int64(i)`. Ban đầu thấy rườm rà, nhưng điều đó buộc bạn nhìn "
                    "thẳng vào mọi điểm có thể mất dữ liệu do thu hẹp kiểu.",
                    "Chia số nguyên cho số nguyên vẫn là số nguyên: `7/2 == 3`. Muốn kết "
                    "quả thực thì phải chuyển đổi trước.",
                    note="Chuyển từ kiểu rộng sang kiểu hẹp có thể mất dữ liệu âm thầm; hãy kiểm tra biên trước khi ép.",
                ),
            ],
            samples=[
                code(
                    "Chuyển đổi và cạm bẫy chia",
                    """
var count int32 = 7
total := int64(count)

avg := 7 / 2            // 3, phép chia nguyên
avgF := float64(7) / 2  // 3.5

var big int64 = 300
small := int8(big) // 44 — tràn âm thầm, phải tự kiểm tra
""",
                    output="3 3.5 44",
                ),
            ],
            takeaways=[
                "Mọi chuyển đổi số phải tường minh.",
                "`byte` = uint8, `rune` = int32.",
                "Ép sang kiểu hẹp hơn có thể tràn; kiểm tra biên trước.",
            ],
            exercises=["Viết hàm `toInt8(v int64) (int8, error)` báo lỗi khi vượt phạm vi."],
        ),
        lesson(
            slug="zero-value",
            title="Zero value và thiết kế API dùng được ngay",
            summary="Mọi giá trị Go được khởi tạo về zero value, và các API tốt tận dụng điều đó.",
            level="beginner",
            tags=["co-ban", "kien-truc"],
            sections=[
                sec(
                    "Không có biến rác",
                    'Số về 0, bool về false, string về "", con trỏ/slice/map/channel/'
                    "interface/func về nil. Không tồn tại khái niệm biến chưa khởi tạo "
                    "chứa giá trị rác như trong C.",
                    "Hệ quả: struct khai báo bằng `var b bytes.Buffer` dùng được ngay, "
                    "không cần hàm khởi tạo.",
                ),
                sec(
                    "Thiết kế cho zero value có nghĩa",
                    "Thư viện chuẩn theo triết lý “make the zero value useful”: "
                    "`sync.Mutex`, `bytes.Buffer`, `sync.WaitGroup` đều hoạt động khi ở "
                    "trạng thái zero. Khi thiết kế struct của mình, hãy cố gắng để cấu "
                    "hình mặc định là hợp lý.",
                    "Lưu ý ngoại lệ quan trọng: map và channel ở trạng thái nil chỉ đọc "
                    "được (map trả về zero value), ghi vào sẽ panic hoặc chặn mãi. Chúng "
                    "cần `make` trước khi ghi.",
                    note="Đọc từ map nil an toàn và trả zero value; ghi vào map nil thì panic.",
                ),
            ],
            samples=[
                code(
                    "Zero value dùng được ngay",
                    """
var buf bytes.Buffer
buf.WriteString("dùng được ngay\\n") // không cần khởi tạo

var mu sync.Mutex
mu.Lock()
mu.Unlock()

var m map[string]int
fmt.Println(m["thiếu"], len(m)) // 0 0 — đọc an toàn
// m["a"] = 1 --> panic: assignment to entry in nil map
""",
                    output="0 0",
                ),
            ],
            takeaways=[
                "Mọi biến đều được khởi tạo về zero value.",
                "API tốt làm cho zero value có ý nghĩa dùng được.",
                "Map/channel nil phải `make` trước khi ghi.",
            ],
            exercises=[
                "Thiết kế struct `Config` mà zero value tương ứng cấu hình an toàn cho production."
            ],
        ),
        lesson(
            slug="if-va-switch",
            title="if, switch và điều khiển luồng",
            summary="Không ngoặc điều kiện, có khai báo trong if, và switch mạnh hơn hẳn ngôn ngữ C.",
            level="beginner",
            tags=["co-ban", "cu-phap"],
            sections=[
                sec(
                    "if với câu lệnh khởi tạo",
                    "`if err := do(); err != nil { ... }` giới hạn phạm vi của err vào "
                    "đúng khối cần dùng. Đây là mẫu xuất hiện dày đặc trong code Go và "
                    "giúp tránh biến err sống dài không cần thiết.",
                    "Điều kiện không cần ngoặc tròn nhưng bắt buộc có ngoặc nhọn, nên "
                    "không có lớp lỗi “thiếu ngoặc sau if” như trong C.",
                ),
                sec(
                    "switch không cần break",
                    "Mỗi case tự kết thúc, muốn chảy tiếp phải viết `fallthrough`. "
                    "Switch có thể không có biểu thức, trở thành chuỗi if/else if đọc "
                    "gọn hơn; case cũng nhận nhiều giá trị cách nhau bằng dấu phẩy.",
                    "Sau này bạn sẽ gặp `switch v := x.(type)` để phân nhánh theo kiểu "
                    "động của interface — một biến thể riêng của cú pháp này.",
                ),
            ],
            samples=[
                code(
                    "if có khởi tạo, switch không biểu thức",
                    """
if n, err := strconv.Atoi(raw); err == nil && n > 0 {
	fmt.Println("số dương:", n)
}

switch {
case score >= 90:
	grade = "A"
case score >= 80:
	grade = "B"
default:
	grade = "C"
}

switch day {
case "sat", "sun":
	fmt.Println("cuối tuần")
}
""",
                ),
            ],
            takeaways=[
                "Khai báo trong `if` giữ phạm vi biến hẹp nhất có thể.",
                "Case của switch không tự chảy tiếp; cần `fallthrough`.",
                "Switch không biểu thức thay thế chuỗi if/else dài.",
            ],
            exercises=["Viết lại một chuỗi if/else if bằng switch không biểu thức."],
        ),
        lesson(
            slug="vong-lap-for",
            title="Chỉ một vòng lặp: for",
            summary="Go có duy nhất từ khoá for, đảm nhiệm cả while, do-while và foreach.",
            level="beginner",
            tags=["co-ban", "cu-phap"],
            sections=[
                sec(
                    "Bốn dạng của for",
                    "Dạng ba thành phần cổ điển; dạng chỉ có điều kiện (thay cho while); "
                    "dạng không điều kiện (vòng lặp vô hạn); và `for range` để đi qua "
                    "slice, map, string, channel.",
                    "Từ Go 1.22, `for i := range 5` lặp năm lần với i từ 0 đến 4 — không "
                    "cần biến đếm thủ công cho vòng lặp đơn giản.",
                ),
                sec(
                    "Ngữ nghĩa của range",
                    "Với slice, range trả về chỉ số và **bản copy** của phần tử; muốn sửa "
                    "phần tử gốc phải dùng `s[i]`. Với string, range trả về vị trí byte "
                    "và rune đã giải mã UTF-8. Với map, thứ tự lặp được ngẫu nhiên hoá có "
                    "chủ đích để không ai vô tình phụ thuộc vào nó.",
                    "Từ Go 1.22, biến vòng lặp được tạo mới mỗi vòng, nên lỗi “tất cả "
                    "goroutine đều thấy giá trị cuối” đã biến mất.",
                    note="Nếu vẫn phải hỗ trợ Go ≤ 1.21, hãy sao chép biến vòng lặp trước khi truyền vào goroutine hoặc closure.",
                ),
            ],
            samples=[
                code(
                    "Các dạng vòng lặp",
                    """
for i := 0; i < 3; i++ {
}

n := 3
for n > 0 {
	n--
}

for i := range 3 {
	_ = i // Go 1.22+
}

items := []string{"a", "b"}
for i, v := range items {
	items[i] = v + "!" // sửa qua chỉ số, không qua v
}

for pos, r := range "Go♥" {
	fmt.Printf("%d:%c ", pos, r)
}
""",
                    output="0:G 1:o 2:♥",
                    explanation="Rune ♥ chiếm 3 byte nên vị trí byte nhảy từ 2 lên 5 ở vòng kế tiếp.",
                ),
            ],
            takeaways=[
                "Một từ khoá `for` bao trọn mọi kiểu vòng lặp.",
                "`range` trên slice trả về copy phần tử; sửa qua chỉ số.",
                "Thứ tự lặp map là ngẫu nhiên — đừng phụ thuộc vào nó.",
            ],
            exercises=["In các cặp key/value của một map theo thứ tự key đã sắp xếp."],
        ),
        lesson(
            slug="ham-va-gia-tri-tra-ve",
            title="Hàm và nhiều giá trị trả về",
            summary="Trả về nhiều giá trị là nền tảng cho cách Go xử lý lỗi mà không cần exception.",
            level="beginner",
            tags=["co-ban", "ham"],
            sections=[
                sec(
                    "Nhiều giá trị trả về",
                    "Hàm Go trả về bao nhiêu giá trị cũng được. Quy ước gần như tuyệt "
                    "đối: giá trị cuối là `error`. Người gọi kiểm tra lỗi ngay tại chỗ "
                    "thay vì để ngoại lệ bay lên tầng trên.",
                    "Có thể đặt tên cho giá trị trả về để tự tài liệu hoá chữ ký hàm, "
                    "nhưng nên tránh `return` trần vì làm khó đọc luồng dữ liệu.",
                ),
                sec(
                    "Tham số biến thiên và truyền theo giá trị",
                    "`func sum(nums ...int)` nhận số lượng tham số tuỳ ý; bên trong "
                    "`nums` là một slice. Gọi với slice sẵn có bằng cú pháp `sum(s...)`.",
                    "Mọi thứ trong Go truyền theo giá trị. Truyền một struct lớn nghĩa là "
                    "copy nó; truyền con trỏ thì chỉ copy con trỏ. Slice, map, channel "
                    "chứa tham chiếu bên trong nên copy chúng vẫn trỏ về cùng dữ liệu nền.",
                ),
            ],
            samples=[
                code(
                    "Nhiều giá trị trả về và variadic",
                    """
func divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, errors.New("chia cho 0")
	}
	return a / b, nil
}

func sum(nums ...int) int {
	total := 0
	for _, n := range nums {
		total += n
	}
	return total
}

q, err := divide(10, 4)
values := []int{1, 2, 3}
fmt.Println(q, err, sum(values...))
""",
                    output="2.5 <nil> 6",
                ),
            ],
            takeaways=[
                "Nhiều giá trị trả về, error luôn ở cuối.",
                "`...T` cho tham số biến thiên; `s...` để bung slice.",
                "Truyền theo giá trị: struct bị copy, slice/map chia sẻ dữ liệu nền.",
            ],
            exercises=[
                "Viết `minMax(nums ...int) (int, int, error)` báo lỗi khi không có tham số."
            ],
        ),
        lesson(
            slug="closure-va-ham-bac-cao",
            title="Closure và hàm bậc cao",
            summary="Hàm là giá trị hạng nhất; closure bắt biến theo tham chiếu và mở ra nhiều mẫu thiết kế gọn.",
            level="intermediate",
            tags=["ham", "kien-truc"],
            sections=[
                sec(
                    "Hàm là giá trị",
                    "Có thể gán hàm cho biến, truyền làm tham số, trả về từ hàm khác. "
                    "Kiểu của hàm là chữ ký của nó, ví dụ `func(int) (string, error)`.",
                    "Closure là hàm ẩn danh giữ tham chiếu tới biến ở phạm vi bao ngoài. "
                    "Biến đó sống tiếp sau khi hàm bao ngoài trả về, vì escape analysis "
                    "chuyển nó lên heap.",
                ),
                sec(
                    "Mẫu functional option",
                    "Closure là nền tảng của functional option — cách Go xử lý hàm khởi "
                    "tạo có nhiều tham số tuỳ chọn mà vẫn tương thích ngược khi thêm "
                    "tuỳ chọn mới.",
                    "Ứng dụng khác: middleware HTTP, hàm so sánh cho sort, và retry "
                    "wrapper nhận vào một `func() error`.",
                ),
            ],
            samples=[
                code(
                    "Closure đếm và functional option",
                    """
func counter() func() int {
	n := 0
	return func() int {
		n++
		return n
	}
}

type Server struct {
	addr    string
	timeout time.Duration
}

type Option func(*Server)

func WithTimeout(d time.Duration) Option {
	return func(s *Server) { s.timeout = d }
}

func New(addr string, opts ...Option) *Server {
	s := &Server{addr: addr, timeout: 5 * time.Second}
	for _, opt := range opts {
		opt(s)
	}
	return s
}
""",
                    output="next := counter(); next(); next() // 1, 2",
                ),
            ],
            takeaways=[
                "Hàm là giá trị hạng nhất, kiểu của nó chính là chữ ký.",
                "Closure bắt biến theo tham chiếu, biến được đưa lên heap khi cần.",
                "Functional option cho API khởi tạo mở rộng được mà không phá vỡ tương thích.",
            ],
            exercises=["Thêm `WithLogger` vào ví dụ trên mà không sửa chữ ký của `New`."],
        ),
        lesson(
            slug="defer-thuc-thi-hoan-lai",
            title="defer: dọn dẹp không thể quên",
            summary="defer đảm bảo hành động dọn dẹp chạy khi hàm kết thúc, kể cả khi có panic.",
            level="beginner",
            tags=["co-ban", "ham"],
            sections=[
                sec(
                    "Ngữ nghĩa LIFO",
                    "Lệnh `defer` đẩy một lời gọi vào stack của hàm hiện tại; khi hàm trả "
                    "về, các lời gọi này chạy theo thứ tự ngược. Tham số của lời gọi được "
                    "đánh giá **ngay lúc defer**, không phải lúc chạy.",
                    "Đặt defer ngay sau khi giành tài nguyên: mở file thì defer Close, "
                    "khoá mutex thì defer Unlock. Người đọc thấy ngay cặp giành–trả.",
                ),
                sec(
                    "Cạm bẫy thường gặp",
                    "Defer trong vòng lặp không chạy ở cuối mỗi vòng mà tích tụ tới khi "
                    "hàm kết thúc; xử lý nhiều nghìn file trong một hàm sẽ cạn file "
                    "descriptor. Cách chữa: tách thân vòng lặp thành hàm riêng.",
                    "Defer kết hợp giá trị trả về có tên cho phép sửa lỗi trả về, thường "
                    "dùng để bọc lỗi hoặc chuyển panic thành error.",
                    note="Với file chỉ đọc, `defer f.Close()` là đủ; nhưng khi ghi, hãy kiểm tra lỗi của Close vì dữ liệu có thể chưa được flush.",
                ),
            ],
            samples=[
                code(
                    "Thứ tự và thời điểm đánh giá tham số",
                    """
func demo() {
	for i := range 3 {
		defer fmt.Println("defer", i)
	}
	fmt.Println("thân hàm xong")
}
""",
                    output="thân hàm xong\ndefer 2\ndefer 1\ndefer 0",
                ),
                code(
                    "Bọc lỗi qua giá trị trả về có tên",
                    """
func writeReport(path string) (err error) {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer func() {
		if cerr := f.Close(); err == nil {
			err = cerr
		}
	}()
	_, err = f.WriteString("báo cáo\\n")
	return err
}
""",
                    explanation="Lỗi khi Close không bị bỏ qua nhưng cũng không ghi đè lỗi ghi dữ liệu quan trọng hơn.",
                ),
            ],
            takeaways=[
                "Defer chạy theo LIFO khi hàm kết thúc, kể cả lúc panic.",
                "Tham số của lời gọi defer được đánh giá ngay khi gặp lệnh defer.",
                "Đừng defer trong vòng lặp dài — tách thành hàm con.",
            ],
            exercises=["Sửa một vòng lặp mở nhiều file dùng defer sai thành phiên bản tách hàm."],
        ),
    ],
)
