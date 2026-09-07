"""Chương 11 — Hiệu năng và runtime."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="hieu-nang",
    title="Hiệu năng và runtime",
    summary=(
        "Bên trong scheduler, cấp phát bộ nhớ, escape analysis, GC và bộ công cụ "
        "pprof/trace — cách biến phỏng đoán thành số liệu."
    ),
    lessons=[
        lesson(
            slug="runtime-scheduler-sau",
            title="Scheduler G-M-P nhìn từ bên trong",
            summary="Work stealing, preemption và lý do một goroutine chặn syscall không làm đứng cả chương trình.",
            level="advanced",
            tags=["runtime", "dong-thoi", "hieu-nang"],
            sections=[
                sec(
                    "Ba thực thể",
                    "G là goroutine (stack + trạng thái), M là OS thread thực sự chạy mã, P "
                    "là logical processor — số P bằng GOMAXPROCS và là giấy phép để chạy. "
                    "Mỗi P có run queue cục bộ; ngoài ra có một global run queue.",
                    "Khi run queue cục bộ rỗng, P sẽ trộm một nửa công việc từ P khác. Cơ "
                    "chế này giữ mọi lõi có việc mà không cần một điểm đồng bộ trung tâm.",
                ),
                sec(
                    "Syscall và preemption",
                    "Khi một goroutine vào syscall chặn, M của nó bị tách khỏi P; P được gán "
                    "cho M khác để tiếp tục chạy các goroutine còn lại. Vì thế đọc file chậm "
                    "không làm đứng các request khác.",
                    "Từ Go 1.14, preemption là bất đồng bộ dựa trên tín hiệu: một goroutine "
                    "tính toán trong vòng lặp chặt vẫn bị ngắt để nhường chỗ. Trước đó, vòng "
                    "lặp không có lời gọi hàm có thể chiếm P vô hạn.",
                    note="`GODEBUG=schedtrace=1000` in trạng thái scheduler mỗi giây: số P, số M, độ dài run queue — hữu ích khi chẩn đoán độ trễ lạ.",
                ),
            ],
            samples=[
                code(
                    "Quan sát scheduler",
                    """
GODEBUG=schedtrace=1000 ./myapp
# SCHED 1001ms: gomaxprocs=8 idleprocs=6 threads=12 runqueue=0 [0 1 0 0 0 0 0 2]

GODEBUG=schedtrace=1000,scheddetail=1 ./myapp   # chi tiết từng P và M
""",
                    language="bash",
                ),
                code(
                    "Số P và số goroutine",
                    """
fmt.Println(runtime.GOMAXPROCS(0)) // số P hiện tại
fmt.Println(runtime.NumCPU())      // số lõi logic hệ điều hành báo
fmt.Println(runtime.NumGoroutine())
""",
                    output="8\n8\n3",
                ),
            ],
            takeaways=[
                "G-M-P với run queue cục bộ và work stealing.",
                "Syscall chặn chỉ chiếm M, P được chuyển cho M khác.",
                "Preemption bất đồng bộ ngăn một goroutine chiếm P vô hạn.",
            ],
            exercises=["Chạy một chương trình có vòng lặp CPU nặng và quan sát schedtrace."],
        ),
        lesson(
            slug="cap-phat-stack-va-heap",
            title="Stack và heap: hai loại bộ nhớ",
            summary="Stack rẻ, heap đắt vì kéo theo GC — và trình biên dịch tự quyết định chỗ nào.",
            level="advanced",
            tags=["bo-nho", "hieu-nang", "runtime"],
            sections=[
                sec(
                    "Stack goroutine tự lớn",
                    "Mỗi goroutine bắt đầu với stack nhỏ (~2 KB) trên heap. Khi cần thêm, "
                    "runtime cấp phát stack lớn gấp đôi, copy nội dung sang và điều chỉnh con "
                    "trỏ. Nhờ vậy không cần đặt trước kích thước stack như với thread.",
                    "Cấp phát trên stack gần như miễn phí: chỉ là dịch con trỏ stack, và tự "
                    "giải phóng khi hàm trả về. Không có công việc nào cho GC.",
                ),
                sec(
                    "Heap và chi phí thật",
                    "Đối tượng trên heap phải được GC theo dõi. Chi phí không chỉ là lúc cấp "
                    "phát mà cả áp lực lên GC: nhiều đối tượng sống lâu nghĩa là GC chạy "
                    "thường xuyên hơn và mark nhiều hơn.",
                    "Runtime dùng size class và bộ nhớ cache theo P (mcache) nên cấp phát nhỏ "
                    "cũng khá nhanh, không cần khoá. Nhưng “khá nhanh” vẫn đắt hơn stack hàng "
                    "chục lần.",
                    note="Chỉ số đáng theo dõi: allocs/op trong benchmark và `go tool pprof -alloc_objects` ở production.",
                ),
            ],
            samples=[
                code(
                    "Đọc thống kê bộ nhớ",
                    """
var m runtime.MemStats
runtime.ReadMemStats(&m)

fmt.Printf("heap đang dùng: %d KB\\n", m.HeapAlloc/1024)
fmt.Printf("tổng đã cấp phát: %d MB\\n", m.TotalAlloc/1024/1024)
fmt.Printf("số lần GC: %d\\n", m.NumGC)
fmt.Printf("tổng thời gian pause: %v\\n", time.Duration(m.PauseTotalNs))
""",
                    output="heap đang dùng: 2048 KB\ntổng đã cấp phát: 128 MB\nsố lần GC: 42\ntổng thời gian pause: 3.2ms",
                ),
            ],
            takeaways=[
                "Stack goroutine tự lớn bằng cách copy sang vùng lớn hơn.",
                "Cấp phát stack gần như miễn phí; heap kéo theo chi phí GC.",
                "Theo dõi allocs/op và alloc_objects thay vì đoán.",
            ],
            exercises=["Đọc MemStats trước và sau một vòng lặp cấp phát 1 triệu struct nhỏ."],
        ),
        lesson(
            slug="escape-analysis",
            title="Escape analysis: vì sao biến của bạn lên heap",
            summary="`-gcflags=-m` cho biết chính xác biến nào escape và tại sao.",
            level="advanced",
            tags=["bo-nho", "hieu-nang", "cong-cu"],
            sections=[
                sec(
                    "Quy tắc quyết định",
                    "Trình biên dịch đặt biến trên stack nếu chứng minh được nó không sống "
                    "quá hàm. Biến escape khi: địa chỉ được trả về hoặc lưu vào cấu trúc sống "
                    "lâu hơn, kích thước không xác định lúc biên dịch, hoặc bị truyền vào "
                    "tham số `any`/interface.",
                    "Lời gọi `fmt.Println(x)` khiến x escape vì tham số là `...any`. Đó là lý "
                    "do log dày đặc trong hot path tạo áp lực GC đáng kể.",
                ),
                sec(
                    "Cách đọc kết quả",
                    "`go build -gcflags='-m'` in ra từng quyết định: “moved to heap”, "
                    "“escapes to heap”, “does not escape”, “inlining call to”. Thêm `-m -m` "
                    "để có lý do chi tiết hơn.",
                    "Đừng tối ưu escape một cách mù quáng. Hãy dùng pprof để tìm điểm nóng "
                    "trước, rồi mới xem escape analysis ở đúng hàm đó.",
                    note="Inlining và escape analysis liên quan chặt: hàm được inline có thể giữ biến trên stack, nên hàm nhỏ thường nhanh hơn bất ngờ.",
                ),
            ],
            samples=[
                code(
                    "Hai phiên bản, hai kết quả",
                    """
// Không escape: buffer nằm trên stack
func sumStack() int {
	var buf [64]int
	for i := range buf {
		buf[i] = i
	}
	total := 0
	for _, v := range buf {
		total += v
	}
	return total
}

// Escape: kích thước không biết lúc biên dịch
func sumHeap(n int) int {
	buf := make([]int, n) // escapes to heap
	for i := range buf {
		buf[i] = i
	}
	total := 0
	for _, v := range buf {
		total += v
	}
	return total
}
""",
                ),
                code(
                    "Xem quyết định của compiler",
                    """
go build -gcflags='-m' ./... 2>&1 | grep -E 'escapes|moved to heap'
# ./main.go:18:13: make([]int, n) escapes to heap
# ./main.go:31:2: moved to heap: cfg
""",
                    language="bash",
                ),
            ],
            takeaways=[
                "Biến escape khi sống lâu hơn hàm hoặc kích thước không xác định.",
                "Truyền vào `any`/interface thường gây escape.",
                "`-gcflags=-m` cho câu trả lời chính xác, không cần đoán.",
            ],
            exercises=[
                "Chạy -gcflags=-m trên một package của bạn và giải thích ba dòng escape đầu tiên."
            ],
        ),
        lesson(
            slug="garbage-collector-hoat-dong",
            title="Garbage collector: mark ba màu, chạy đồng thời",
            summary="GC của Go ưu tiên độ trễ thấp: pause dưới một mili giây, đổi lấy một phần CPU.",
            level="advanced",
            tags=["runtime", "hieu-nang", "bo-nho"],
            sections=[
                sec(
                    "Bốn pha",
                    "Mark setup (STW rất ngắn) bật write barrier; concurrent mark chạy song "
                    "song với chương trình, dùng khoảng 25% CPU; mark termination (STW ngắn) "
                    "kết thúc việc mark; sweep giải phóng dần khi có cấp phát mới.",
                    "Thuật toán ba màu: trắng là chưa thăm, xám là đã thăm nhưng chưa xét con, "
                    "đen là xong. Write barrier đảm bảo đối tượng mới được tham chiếu trong "
                    "lúc mark không bị bỏ sót.",
                ),
                sec(
                    "Hai núm điều chỉnh",
                    "`GOGC` (mặc định 100) nghĩa là GC chạy khi heap sống tăng gấp đôi so với "
                    "lần trước. Tăng GOGC lên 200–400 giảm số lần GC nhưng dùng nhiều RAM "
                    "hơn. `GOMEMLIMIT` (Go 1.19+) đặt trần bộ nhớ mềm — cực kỳ hữu ích trong "
                    "container để tránh bị OOM kill.",
                    "Mẫu cấu hình phổ biến cho container: GOMEMLIMIT khoảng 80–90% giới hạn "
                    "bộ nhớ của pod, và GOGC cao hơn mặc định. Khi tới gần trần, GC tự chạy "
                    "tích cực hơn thay vì để process bị giết.",
                    note="Tối ưu GC tốt nhất là cấp phát ít hơn. Điều chỉnh GOGC chỉ là bước sau khi đã giảm được rác.",
                ),
            ],
            samples=[
                code(
                    "Theo dõi GC",
                    """
GODEBUG=gctrace=1 ./myapp
# gc 12 @2.345s 1%: 0.018+3.2+0.021 ms clock, 0.14+0.52/3.1/0+0.17 ms cpu,
#   45->46->23 MB, 47 MB goal, 8 P
""",
                    language="bash",
                    explanation="45->46->23 MB là heap trước GC, tại đỉnh và sau GC; 47 MB goal là ngưỡng cho lần kế tiếp.",
                ),
                code(
                    "Cấu hình cho container",
                    """
GOMEMLIMIT=900MiB   # pod limit 1Gi
GOGC=200

// hoặc trong code:
debug.SetMemoryLimit(900 << 20)
debug.SetGCPercent(200)
""",
                    language="bash",
                ),
            ],
            takeaways=[
                "GC chạy đồng thời, pause thường dưới 1 ms.",
                "GOGC điều khiển tần suất, GOMEMLIMIT đặt trần bộ nhớ mềm.",
                "Cách tối ưu GC hiệu quả nhất là giảm cấp phát.",
            ],
            exercises=[
                "Chạy service với gctrace=1 và ghi lại tần suất GC trước/sau khi tăng GOGC."
            ],
        ),
        lesson(
            slug="pprof-cpu-va-bo-nho",
            title="pprof: profile CPU và bộ nhớ",
            summary="Công cụ biến câu hỏi “vì sao chậm” thành một danh sách hàm có số liệu.",
            level="intermediate",
            tags=["hieu-nang", "cong-cu", "van-hanh"],
            sections=[
                sec(
                    "Bật profile",
                    "Trong test: `go test -cpuprofile cpu.out -memprofile mem.out -bench .`. "
                    'Trong service: import `_ "net/http/pprof"` và mount nó trên một port '
                    "**nội bộ** (không public), rồi lấy profile bằng `go tool pprof`.",
                    "CPU profile lấy mẫu stack 100 lần mỗi giây nên chi phí rất thấp; có thể "
                    "bật ở production trong khoảng 30 giây một cách an toàn.",
                ),
                sec(
                    "Đọc profile",
                    "`top` cho danh sách hàm theo thời gian; phân biệt flat (thời gian trong "
                    "chính hàm) và cum (gồm cả hàm nó gọi). `list <Hàm>` cho số liệu theo "
                    "từng dòng. `web` vẽ đồ thị lời gọi. Flame graph cho thấy đường nào chiếm "
                    "phần lớn thời gian.",
                    "Với bộ nhớ có hai góc nhìn: `inuse_space` (đang chiếm — tìm rò rỉ) và "
                    "`alloc_objects` (tổng đã cấp phát — tìm áp lực GC). Chọn đúng góc nhìn "
                    "cho câu hỏi của bạn.",
                    note="Đừng bao giờ để endpoint /debug/pprof lộ ra Internet: nó tiết lộ cấu trúc chương trình và cho phép tạo tải.",
                ),
            ],
            samples=[
                code(
                    "Lấy và đọc profile",
                    """
# Từ service đang chạy
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
go tool pprof http://localhost:6060/debug/pprof/heap

# Trong pprof
(pprof) top10
(pprof) list processRequest
(pprof) web

# Từ benchmark
go test -bench=. -cpuprofile=cpu.out ./internal/parser
go tool pprof -http=:8081 cpu.out
""",
                    language="bash",
                ),
                code(
                    "Mount pprof trên port nội bộ",
                    """
import _ "net/http/pprof"

func main() {
	go func() {
		// Chỉ lắng nghe loopback, không expose ra ngoài
		log.Println(http.ListenAndServe("127.0.0.1:6060", nil))
	}()
	// ... server chính trên mux riêng
}
""",
                ),
            ],
            takeaways=[
                "CPU profile lấy mẫu, chi phí thấp, an toàn ở production.",
                "flat vs cum và `list` theo dòng là cách đọc chính.",
                "inuse_space cho rò rỉ, alloc_objects cho áp lực GC.",
            ],
            exercises=[
                "Profile một benchmark và dùng `list` để tìm dòng chiếm nhiều thời gian nhất."
            ],
        ),
        lesson(
            slug="runtime-trace",
            title="runtime/trace: khi pprof không đủ",
            summary="Trace cho thấy dòng thời gian của từng goroutine — công cụ đúng cho vấn đề độ trễ.",
            level="advanced",
            tags=["hieu-nang", "cong-cu", "dong-thoi"],
            sections=[
                sec(
                    "Trace khác pprof ở đâu",
                    "pprof trả lời “thời gian CPU đi đâu”. Trace trả lời “goroutine này chờ "
                    "cái gì và bao lâu”. Khi CPU thấp mà p99 cao, nguyên nhân là chờ đợi — và "
                    "chỉ trace nhìn thấy được.",
                    "Trace ghi lại sự kiện scheduler, syscall, GC, chặn trên channel và mutex, "
                    "kèm dấu thời gian. Chi phí cao hơn pprof nên chỉ bật trong vài giây.",
                ),
                sec(
                    "Vùng và task",
                    "`trace.NewTask` và `trace.WithRegion` cho phép đánh dấu các đoạn logic "
                    "nghiệp vụ, để trên dòng thời gian bạn thấy “giải mã JSON”, “truy vấn DB” "
                    "thay vì chỉ tên hàm. Đây là điều biến trace từ thú vị thành hữu dụng.",
                    "`go tool trace` mở UI web với các khung nhìn: goroutine analysis, network "
                    "blocking profile, synchronisation blocking profile, và scheduler latency.",
                    note="Nếu thấy nhiều goroutine ở trạng thái “runnable” mà không được chạy, bạn đang thiếu P — kiểm tra GOMAXPROCS.",
                ),
            ],
            samples=[
                code(
                    "Ghi trace và đánh dấu vùng",
                    """
f, _ := os.Create("trace.out")
defer f.Close()
trace.Start(f)
defer trace.Stop()

func handleOrder(ctx context.Context, id string) error {
	ctx, task := trace.NewTask(ctx, "handleOrder")
	defer task.End()

	trace.WithRegion(ctx, "load", func() {
		order = loadOrder(ctx, id)
	})
	trace.WithRegion(ctx, "validate", func() {
		err = validate(order)
	})
	return err
}
""",
                ),
                code(
                    "Mở UI",
                    """
go test -trace=trace.out -bench=Handler ./internal/api
go tool trace trace.out
""",
                    language="bash",
                ),
            ],
            takeaways=[
                "Trace cho biết goroutine chờ gì, pprof cho biết CPU ở đâu.",
                "Task và Region gắn nhãn nghiệp vụ lên dòng thời gian.",
                "Chỉ bật trace vài giây vì chi phí cao.",
            ],
            exercises=["Ghi trace của một handler và tìm đoạn chờ dài nhất trong dòng thời gian."],
        ),
        lesson(
            slug="sync-pool",
            title="sync.Pool: tái dùng đối tượng",
            summary="Giảm áp lực GC bằng cách tái dùng buffer — nhưng chỉ khi đã đo và thấy vấn đề.",
            level="advanced",
            tags=["hieu-nang", "bo-nho", "dong-thoi"],
            sections=[
                sec(
                    "Cách hoạt động",
                    "Pool giữ các đối tượng tạm theo từng P, nên Get/Put gần như không tranh "
                    "chấp. Đối tượng trong pool có thể bị GC thu hồi bất cứ lúc nào, vì thế "
                    "pool không phải là bộ nhớ đệm và không dùng để giới hạn tài nguyên.",
                    "Ứng dụng điển hình: buffer để tuần tự hoá JSON, `bytes.Buffer` cho response, "
                    "struct lớn dùng lại trong hot path. Đây chính là cách encoding/json và "
                    "net/http giảm cấp phát bên trong.",
                ),
                sec(
                    "Ba cạm bẫy",
                    "Một: quên reset đối tượng khi Put, làm dữ liệu cũ rò sang request khác — "
                    "vừa là bug vừa là lỗ bảo mật. Hai: giữ tham chiếu tới đối tượng sau khi "
                    "Put, dẫn tới hai chỗ dùng cùng buffer. Ba: pool các đối tượng có kích "
                    "thước rất khác nhau, khiến buffer nhỏ giữ mãi mảng khổng lồ.",
                    "Với vấn đề thứ ba, hãy bỏ đối tượng quá lớn thay vì Put lại. Và luôn "
                    "benchmark: với đối tượng nhỏ, pool có thể chậm hơn cấp phát thẳng.",
                    note="Quy tắc: chỉ thêm sync.Pool sau khi pprof chỉ ra chính chỗ đó là điểm nóng cấp phát.",
                ),
            ],
            samples=[
                code(
                    "Pool buffer đúng cách",
                    """
var bufPool = sync.Pool{
	New: func() any { return new(bytes.Buffer) },
}

func writeJSON(w http.ResponseWriter, v any) error {
	buf := bufPool.Get().(*bytes.Buffer)
	buf.Reset() // bắt buộc: xoá dữ liệu của lần dùng trước
	defer func() {
		if buf.Cap() <= 64*1024 { // không giữ buffer quá lớn
			bufPool.Put(buf)
		}
	}()

	if err := json.NewEncoder(buf).Encode(v); err != nil {
		return err
	}
	w.Header().Set("Content-Type", "application/json")
	_, err := w.Write(buf.Bytes())
	return err
}
""",
                ),
            ],
            takeaways=[
                "Pool theo P nên Get/Put rất nhanh, nhưng đối tượng có thể bị GC thu.",
                "Luôn Reset khi lấy ra; đừng giữ tham chiếu sau khi Put.",
                "Bỏ buffer quá lớn thay vì đưa lại vào pool.",
            ],
            exercises=["Thêm sync.Pool vào một hàm serialize và so sánh allocs/op trước/sau."],
        ),
        lesson(
            slug="giam-cap-phat-thuc-hanh",
            title="Bảy cách giảm cấp phát",
            summary="Danh sách các thủ pháp đã được chứng minh, xếp theo tỉ lệ lợi ích trên công sức.",
            level="advanced",
            tags=["hieu-nang", "bo-nho", "mau-hinh"],
            sections=[
                sec(
                    "Từ dễ tới khó",
                    "Một: cấp phát trước với `make([]T, 0, n)` và `sb.Grow(n)`. Hai: dùng "
                    "`strings.Builder` thay vì `+=`. Ba: `strconv` thay vì `fmt.Sprintf`. "
                    "Bốn: truyền slice để hàm ghi vào thay vì trả về slice mới.",
                    "Năm: tránh chuyển đổi `[]byte` ↔ `string` lặp lại. Sáu: dùng receiver giá "
                    "trị cho struct nhỏ để tránh escape. Bảy: sync.Pool cho buffer trong hot "
                    "path — làm cuối cùng vì phức tạp nhất.",
                ),
                sec(
                    "Kỷ luật đo lường",
                    "Mỗi thay đổi phải kèm benchmark trước/sau. Nếu allocs/op không giảm, hoàn "
                    "lại thay đổi — bạn vừa làm code khó đọc hơn mà không được gì.",
                    "Và luôn nhớ thứ tự ưu tiên: thuật toán đúng trước, rồi đến I/O và truy "
                    "vấn DB, cuối cùng mới tới vi tối ưu cấp phát. Một index thiếu trong DB "
                    "làm chậm gấp trăm lần mọi thứ bạn tiết kiệm được ở đây.",
                    note="Đừng đánh đổi tính rõ ràng cho một cải thiện 2% mà không ai đo được ở production.",
                ),
            ],
            samples=[
                code(
                    "Trước và sau",
                    """
// TRƯỚC: 3 cấp phát mỗi vòng
func joinSlow(items []string) string {
	out := ""
	for _, s := range items {
		out += s + ","
	}
	return out
}

// SAU: 1 cấp phát duy nhất
func joinFast(items []string) string {
	n := 0
	for _, s := range items {
		n += len(s) + 1
	}
	var sb strings.Builder
	sb.Grow(n)
	for _, s := range items {
		sb.WriteString(s)
		sb.WriteByte(',')
	}
	return sb.String()
}
""",
                    output="joinSlow-8   12043 ns/op  9856 B/op  99 allocs/op\njoinFast-8     412 ns/op   512 B/op   1 allocs/op",
                ),
                code(
                    "Ghi vào slice có sẵn",
                    """
// Cho người gọi tái dùng buffer giữa các lần gọi
func appendIDs(dst []int64, users []User) []int64 {
	for _, u := range users {
		dst = append(dst, u.ID)
	}
	return dst
}

buf := make([]int64, 0, 128)
for page := range pages {
	buf = appendIDs(buf[:0], page.Users) // buf[:0] giữ lại capacity
	process(buf)
}
""",
                ),
            ],
            takeaways=[
                "Cấp phát trước và strings.Builder cho phần lớn lợi ích với ít công sức.",
                "Mẫu `append(dst, ...)` cho phép người gọi tái dùng buffer.",
                "Mọi tối ưu phải có benchmark chứng minh, nếu không thì hoàn lại.",
            ],
            exercises=[
                "Tìm hàm có allocs/op cao nhất trong dự án và áp dụng hai thủ pháp đầu tiên."
            ],
        ),
        lesson(
            slug="gomaxprocs-va-container",
            title="GOMAXPROCS trong container",
            summary="Go đọc số lõi của máy chủ, không đọc CPU limit của container — nguồn của rất nhiều throttling.",
            level="advanced",
            tags=["runtime", "van-hanh", "hieu-nang"],
            sections=[
                sec(
                    "Vấn đề",
                    "Trên node 64 lõi, một pod với `cpu: 2` vẫn thấy GOMAXPROCS=64. Runtime "
                    "tạo tới 64 P và lập lịch như thể có 64 lõi, trong khi cgroup chỉ cho "
                    "2 lõi. Kết quả là CFS throttling: chương trình bị dừng theo chu kỳ, p99 "
                    "tăng vọt dù CPU trung bình thấp.",
                    "Triệu chứng nhận biết: `container_cpu_cfs_throttled_seconds_total` tăng, "
                    "độ trễ có dạng răng cưa theo chu kỳ 100 ms.",
                ),
                sec(
                    "Cách sửa",
                    "Đặt GOMAXPROCS bằng CPU limit (làm tròn lên), hoặc dùng "
                    "`go.uber.org/automaxprocs` để tự đọc cgroup. Từ Go 1.25, runtime nhận "
                    "biết giới hạn cgroup tốt hơn, nhưng đặt tường minh vẫn là cách chắc chắn "
                    "nhất và tự tài liệu hoá.",
                    "Đồng thời đặt GOMEMLIMIT theo memory limit. Hai biến này là cấu hình "
                    "bắt buộc cho mọi service Go chạy trong container.",
                    note="Một dòng `GOMAXPROCS=2` trong manifest đôi khi cải thiện p99 nhiều hơn cả tuần tối ưu code.",
                ),
            ],
            samples=[
                code(
                    "Cấu hình trong Kubernetes",
                    """
resources:
  limits:
    cpu: "2"
    memory: 1Gi
env:
  - name: GOMAXPROCS
    value: "2"
  - name: GOMEMLIMIT
    value: "900MiB"
""",
                    language="yaml",
                ),
                code(
                    "Hoặc tự động trong code",
                    """
import _ "go.uber.org/automaxprocs" // đọc cgroup lúc init

func main() {
	slog.Info("runtime", "gomaxprocs", runtime.GOMAXPROCS(0))
}
""",
                ),
            ],
            takeaways=[
                "GOMAXPROCS mặc định theo số lõi máy chủ, không theo CPU limit.",
                "Sai lệch này gây CFS throttling và p99 răng cưa.",
                "Đặt GOMAXPROCS và GOMEMLIMIT cho mọi service trong container.",
            ],
            exercises=["Kiểm tra manifest của một service và bổ sung hai biến môi trường này."],
        ),
        lesson(
            slug="phuong-phap-do-hieu-nang",
            title="Phương pháp tối ưu hiệu năng",
            summary="Đo, tìm điểm nóng, sửa một thứ, đo lại — vòng lặp kỷ luật thay cho phỏng đoán.",
            level="intermediate",
            tags=["hieu-nang", "chat-luong"],
            sections=[
                sec(
                    "Vòng lặp năm bước",
                    "Một: xác định mục tiêu bằng số (p99 dưới 200 ms, thông lượng 5000 rps). "
                    "Hai: đo hiện trạng bằng benchmark hoặc metrics production. Ba: profile để "
                    "tìm điểm nóng. Bốn: sửa **một** thứ. Năm: đo lại và so sánh thống kê.",
                    "Nếu bạn sửa ba thứ cùng lúc và kết quả tốt hơn, bạn không biết thứ nào có "
                    "tác dụng — và có thể một trong ba đang làm chậm đi.",
                ),
                sec(
                    "Nhìn đúng chỗ",
                    "Thứ tự tác động thường là: thuật toán và truy vấn DB (hàng chục tới hàng "
                    "trăm lần), số lần gọi mạng và tính tuần tự (nhiều lần), rồi mới tới cấp "
                    "phát và vi tối ưu (vài phần trăm tới vài chục phần trăm).",
                    "Đo ở production quan trọng hơn benchmark cục bộ: dữ liệu thật, phân phối "
                    "thật, cache thật. Benchmark là để so sánh hai phiên bản code, không phải "
                    "để dự đoán độ trễ thực tế.",
                    note="Ghi lại số liệu trước/sau vào PR description. Đó là cách duy nhất để sáu tháng sau còn biết vì sao đoạn code này trông như vậy.",
                ),
            ],
            samples=[
                code(
                    "Quy trình một lần tối ưu",
                    """
# 1. Đo hiện trạng, nhiều lần để có ý nghĩa thống kê
go test -bench=Parse -count=10 ./internal/parser > before.txt

# 2. Profile để biết sửa ở đâu
go test -bench=Parse -cpuprofile=cpu.out ./internal/parser
go tool pprof -http=:8081 cpu.out

# 3. Sửa một thứ, rồi đo lại
go test -bench=Parse -count=10 ./internal/parser > after.txt
benchstat before.txt after.txt
# Parse-8   18.3µs ± 2%   4.1µs ± 1%   -77.60%  (p=0.000 n=10+10)
""",
                    language="bash",
                ),
            ],
            takeaways=[
                "Đặt mục tiêu bằng số trước khi bắt đầu tối ưu.",
                "Sửa một thứ mỗi lần và so sánh bằng benchstat.",
                "Thuật toán và DB trước, vi tối ưu sau cùng.",
            ],
            exercises=["Chọn một hàm chậm, đi hết năm bước và ghi lại số liệu trước/sau."],
        ),
    ],
)
