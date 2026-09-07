"""Chương 6 — Đồng thời: goroutine, channel và đồng bộ hoá."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="dong-thoi",
    title="Đồng thời",
    summary=(
        "Lý do người ta chọn Go cho hệ thống mạng: goroutine giá vài kilobyte, "
        "channel như đường ống, và một bộ công cụ đồng bộ hoá nhỏ mà đủ."
    ),
    lessons=[
        lesson(
            slug="goroutine-co-ban",
            title="Goroutine: luồng thực thi giá rẻ",
            summary="Từ khoá `go` khởi chạy một hàm đồng thời với chi phí khởi tạo khoảng 2 KB stack.",
            level="beginner",
            tags=["dong-thoi", "runtime"],
            sections=[
                sec(
                    "Nhẹ hơn OS thread hàng trăm lần",
                    "Một OS thread thường chiếm 1–8 MB stack ảo và cần syscall để tạo. "
                    "Goroutine bắt đầu với stack khoảng 2 KB, tự lớn lên khi cần, và được "
                    "runtime của Go lập lịch trong user space. Vì thế chạy 100.000 "
                    "goroutine là bình thường, còn 100.000 thread thì không.",
                    "Runtime dùng mô hình G-M-P: G là goroutine, M là OS thread, P là "
                    "logical processor (mặc định bằng số lõi). Mỗi P có hàng đợi cục bộ và "
                    "có thể “trộm việc” từ P khác khi rảnh.",
                ),
                sec(
                    "Điều bạn phải tự lo",
                    "`go f()` trả về ngay, không có handle để chờ hay huỷ. Bạn phải tự "
                    "quản lý vòng đời bằng WaitGroup, channel hoặc context. Nếu hàm main "
                    "kết thúc, toàn bộ goroutine bị chấm dứt đột ngột.",
                    "Goroutine bị chặn mãi trên một channel không ai đọc sẽ rò rỉ: nó giữ "
                    "stack và mọi thứ nó tham chiếu, mãi mãi. Đó là loại rò rỉ bộ nhớ phổ "
                    "biến nhất trong Go.",
                    note="Nguyên tắc: khi khởi chạy một goroutine, hãy biết trước nó kết thúc bằng cách nào và ai chờ nó.",
                ),
            ],
            samples=[
                code(
                    "Khởi chạy và chờ",
                    """
func main() {
	var wg sync.WaitGroup
	for i := range 3 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			fmt.Println("worker", i) // Go 1.22+: i là biến riêng mỗi vòng
		}()
	}
	wg.Wait()
	fmt.Println("xong")
}
""",
                    output="worker 0\nworker 2\nworker 1\nxong",
                    explanation="Thứ tự in không xác định — đó là bản chất của thực thi đồng thời.",
                ),
                code(
                    "Chi phí thực tế",
                    """
before := runtime.NumGoroutine()
done := make(chan struct{})
for range 100_000 {
	go func() { <-done }()
}
fmt.Println(runtime.NumGoroutine()-before) // ~100000
close(done)
""",
                    output="100000",
                ),
            ],
            takeaways=[
                "Goroutine khởi đầu ~2 KB stack và được lập lịch trong user space.",
                "Runtime dùng mô hình G-M-P với work stealing.",
                "Mỗi goroutine cần một kế hoạch kết thúc rõ ràng để không rò rỉ.",
            ],
            exercises=[
                "Viết chương trình khởi chạy 10.000 goroutine và đo bộ nhớ bằng runtime.ReadMemStats."
            ],
        ),
        lesson(
            slug="channel-co-ban",
            title="Channel: giao tiếp thay vì chia sẻ",
            summary="“Đừng giao tiếp bằng cách chia sẻ bộ nhớ; hãy chia sẻ bộ nhớ bằng cách giao tiếp.”",
            level="beginner",
            tags=["dong-thoi", "channel"],
            sections=[
                sec(
                    "Gửi, nhận và đồng bộ hoá",
                    "`ch := make(chan int)` tạo channel không buffer. Phép gửi `ch <- v` "
                    "chặn tới khi có ai nhận, và phép nhận `v := <-ch` chặn tới khi có ai "
                    "gửi. Nhờ vậy channel không buffer vừa truyền dữ liệu vừa đồng bộ hai "
                    "goroutine tại một điểm.",
                    "Channel có kiểu, nên compiler kiểm tra dữ liệu chảy qua. "
                    "`chan<- int` chỉ gửi, `<-chan int` chỉ nhận — dùng ở chữ ký hàm để "
                    "diễn đạt hướng luồng dữ liệu.",
                ),
                sec(
                    "Quyền sở hữu dữ liệu",
                    "Mẫu tư duy hữu ích: giá trị gửi vào channel coi như đã chuyển quyền sở "
                    "hữu. Bên gửi không nên tiếp tục sửa nó, bên nhận toàn quyền. Làm vậy "
                    "bạn tránh được data race mà không cần mutex nào.",
                    "Nếu gửi con trỏ hoặc slice qua channel, hãy nhớ dữ liệu nền vẫn dùng "
                    "chung; “chuyển quyền sở hữu” là kỷ luật của bạn, không phải điều "
                    "compiler áp đặt.",
                    note="Quy ước: bên gửi là bên đóng channel, và chỉ đóng một lần. Đóng channel là tín hiệu “không còn dữ liệu nữa”.",
                ),
            ],
            samples=[
                code(
                    "Channel không buffer như điểm gặp",
                    """
func main() {
	result := make(chan string)

	go func() {
		time.Sleep(50 * time.Millisecond)
		result <- "dữ liệu đã sẵn sàng"
	}()

	fmt.Println(<-result) // chặn tới khi goroutine gửi
}
""",
                    output="dữ liệu đã sẵn sàng",
                ),
                code(
                    "Hướng channel trong chữ ký",
                    """
func produce(out chan<- int) { // chỉ được gửi
	defer close(out)
	for i := range 3 {
		out <- i
	}
}

func consume(in <-chan int) { // chỉ được nhận
	for v := range in {
		fmt.Print(v, " ")
	}
}
""",
                    output="0 1 2",
                ),
            ],
            takeaways=[
                "Channel không buffer đồng bộ hai goroutine tại điểm truyền dữ liệu.",
                "Dùng channel một chiều trong chữ ký để nêu rõ hướng dữ liệu.",
                "Bên gửi đóng channel; đóng nghĩa là hết dữ liệu.",
            ],
            exercises=["Viết hàm `ping/pong` hai goroutine trao đổi 5 lượt qua hai channel."],
        ),
        lesson(
            slug="channel-buffer-va-dong",
            title="Channel có buffer, đóng và range",
            summary="Buffer biến channel thành hàng đợi; đóng channel là cách phát tín hiệu kết thúc.",
            level="intermediate",
            tags=["dong-thoi", "channel"],
            sections=[
                sec(
                    "Buffer làm gì và không làm gì",
                    "`make(chan T, n)` cho phép gửi n giá trị mà chưa cần ai nhận. Buffer "
                    "hấp thụ chênh lệch tốc độ ngắn hạn giữa bên sản xuất và bên tiêu thụ. "
                    "Nó **không** giải quyết được việc bên tiêu thụ chậm hơn về lâu dài — "
                    "khi đầy, bên gửi lại bị chặn.",
                    "Chọn kích thước buffer có lý do: bằng số worker, bằng số job của một "
                    "lô. Buffer khổng lồ chỉ che giấu vấn đề và làm tăng độ trễ nhìn thấy.",
                ),
                sec(
                    "Đóng channel và mẫu comma ok",
                    "`close(ch)` khiến mọi phép nhận tiếp theo trả về ngay với zero value. "
                    "`v, ok := <-ch` cho biết channel đã đóng chưa. `for v := range ch` "
                    "lặp tới khi channel đóng — cách đọc gọn nhất.",
                    "Gửi vào channel đã đóng gây panic; đóng hai lần cũng panic. Vì thế chỉ "
                    "bên gửi được đóng, và với nhiều bên gửi thì dùng WaitGroup rồi đóng "
                    "trong một goroutine điều phối.",
                    note="Nhận từ channel nil chặn mãi mãi. Điều này nghe như bug nhưng lại là mẹo hữu ích để “vô hiệu hoá” một nhánh trong select.",
                ),
            ],
            samples=[
                code(
                    "Nhiều bên gửi, một bên đóng",
                    """
func fanIn(sources ...<-chan int) <-chan int {
	out := make(chan int, len(sources))
	var wg sync.WaitGroup
	for _, src := range sources {
		wg.Add(1)
		go func(c <-chan int) {
			defer wg.Done()
			for v := range c {
				out <- v
			}
		}(src)
	}
	go func() {
		wg.Wait()
		close(out) // đóng đúng một lần, sau khi mọi bên gửi xong
	}()
	return out
}
""",
                ),
                code(
                    "comma ok với channel",
                    """
ch := make(chan int, 2)
ch <- 1
close(ch)

v, ok := <-ch
fmt.Println(v, ok) // 1 true
v, ok = <-ch
fmt.Println(v, ok) // 0 false — đã đóng và rỗng
""",
                    output="1 true\n0 false",
                ),
            ],
            takeaways=[
                "Buffer hấp thụ dao động ngắn hạn, không sửa được chênh lệch tốc độ lâu dài.",
                "`for range ch` đọc tới khi channel đóng.",
                "Gửi vào channel đã đóng hoặc đóng hai lần đều panic.",
            ],
            exercises=[
                "Viết fan-in cho 3 nguồn và kiểm tra không bị rò rỉ goroutine bằng goleak hoặc runtime.NumGoroutine."
            ],
        ),
        lesson(
            slug="select-va-timeout",
            title="select, timeout và huỷ bỏ",
            summary="select chờ nhiều kênh cùng lúc — nền tảng của timeout và graceful shutdown.",
            level="intermediate",
            tags=["dong-thoi", "channel"],
            sections=[
                sec(
                    "Ngữ nghĩa của select",
                    "select chặn tới khi một trong các case sẵn sàng; nếu nhiều case sẵn "
                    "sàng, một case được chọn ngẫu nhiên để không có kênh nào bị bỏ đói. "
                    "Thêm `default` biến select thành thao tác không chặn.",
                    "Kết hợp với `time.After` cho timeout, với `ctx.Done()` cho huỷ bỏ, và "
                    "với channel nil để tắt tạm một nhánh.",
                ),
                sec(
                    "Timeout đúng cách",
                    "`time.After` tạo một timer mới mỗi lần select được đánh giá; trong "
                    "vòng lặp nóng nên dùng `time.NewTimer` và reset để tránh rác. Tốt hơn "
                    "nữa: dùng `context.WithTimeout` và truyền context xuống tận cùng, để "
                    "toàn bộ ngăn xếp lời gọi cùng dừng.",
                    "Luôn cân nhắc điều gì xảy ra khi timeout xảy ra trong lúc goroutine "
                    "nền vẫn đang gửi: nếu không ai nhận nữa, nó sẽ bị chặn mãi. Dùng "
                    "channel có buffer 1 hoặc select với ctx.Done() ở phía gửi.",
                    note="Đây là nguồn rò rỉ goroutine tinh vi nhất: bên nhận bỏ đi sau timeout, bên gửi bị chặn vĩnh viễn.",
                ),
            ],
            samples=[
                code(
                    "select với timeout và context",
                    """
func fetchWithTimeout(ctx context.Context, url string) (string, error) {
	ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
	defer cancel()

	result := make(chan string, 1) // buffer 1: bên gửi không bị chặn nếu ta bỏ đi
	errc := make(chan error, 1)

	go func() {
		body, err := download(url)
		if err != nil {
			errc <- err
			return
		}
		result <- body
	}()

	select {
	case body := <-result:
		return body, nil
	case err := <-errc:
		return "", err
	case <-ctx.Done():
		return "", fmt.Errorf("tải %s: %w", url, ctx.Err())
	}
}
""",
                ),
                code(
                    "Thử không chặn",
                    """
select {
case job := <-queue:
	process(job)
default:
	// hàng đợi rỗng, làm việc khác thay vì chờ
}
""",
                ),
            ],
            takeaways=[
                "select chọn ngẫu nhiên giữa các case cùng sẵn sàng.",
                "`default` biến select thành thao tác không chặn.",
                "Cho channel kết quả buffer 1 để bên gửi không bị chặn sau timeout.",
            ],
            exercises=[
                "Viết hàm gọi hai API song song và trả về kết quả nào về trước, huỷ phần còn lại."
            ],
        ),
        lesson(
            slug="waitgroup-va-dong-bo",
            title="sync.WaitGroup và chờ tập goroutine",
            summary="Add trước khi go, Done trong defer, Wait ở goroutine điều phối.",
            level="beginner",
            tags=["dong-thoi", "dong-bo"],
            sections=[
                sec(
                    "Ba lệnh, một kỷ luật",
                    "`wg.Add(1)` phải gọi **trước** khi khởi chạy goroutine, không phải "
                    "bên trong nó — nếu không, Wait có thể trở về trước khi Add kịp chạy. "
                    "`defer wg.Done()` là dòng đầu tiên trong goroutine. `wg.Wait()` chặn "
                    "tới khi bộ đếm về 0.",
                    "WaitGroup không truyền được kết quả hay lỗi. Muốn thu kết quả, dùng "
                    "slice có chỉ số cố định (mỗi goroutine ghi vào ô riêng) hoặc channel.",
                ),
                sec(
                    "Không copy WaitGroup",
                    "WaitGroup chứa trạng thái nội bộ nên phải truyền bằng con trỏ. Copy nó "
                    "vào một hàm khác sẽ tạo bộ đếm riêng và Wait không bao giờ khớp; "
                    "`go vet` bắt được lỗi này.",
                    "Khi cần cả chờ và thu lỗi, `errgroup.Group` là lựa chọn tốt hơn — nó "
                    "gói WaitGroup cùng việc lan truyền lỗi và huỷ context.",
                ),
            ],
            samples=[
                code(
                    "Thu kết quả song song an toàn",
                    """
func fetchAll(urls []string) []string {
	results := make([]string, len(urls)) // mỗi goroutine ghi một ô riêng
	var wg sync.WaitGroup

	for i, url := range urls {
		wg.Add(1)
		go func() {
			defer wg.Done()
			results[i] = fetch(url)
		}()
	}
	wg.Wait()
	return results
}
""",
                    explanation="Không cần mutex vì mỗi goroutine ghi vào một chỉ số khác nhau của slice.",
                ),
            ],
            takeaways=[
                "`Add` trước `go`, `Done` trong `defer`.",
                "Truyền WaitGroup bằng con trỏ, đừng copy.",
                "Ghi vào ô riêng của slice để thu kết quả không cần mutex.",
            ],
            exercises=["Chuyển ví dụ trên sang errgroup để dừng sớm khi có một lỗi."],
        ),
        lesson(
            slug="mutex-va-rwmutex",
            title="sync.Mutex và RWMutex",
            summary="Khi dữ liệu phải dùng chung, mutex là công cụ đơn giản và nhanh — nếu dùng đúng.",
            level="intermediate",
            tags=["dong-thoi", "dong-bo"],
            sections=[
                sec(
                    "Bảo vệ dữ liệu, không bảo vệ code",
                    "Mutex nên nằm ngay cạnh dữ liệu nó bảo vệ, và mọi truy cập tới dữ liệu "
                    "đó phải đi qua nó. Đặt mutex làm trường có tên (`mu sync.Mutex`) thay "
                    "vì nhúng, để Lock/Unlock không lọt ra API công khai.",
                    "`defer mu.Unlock()` ngay sau Lock là mẫu an toàn nhất; nhưng nếu vùng "
                    "tới hạn nhỏ và hàm dài, mở khoá tường minh sớm sẽ giảm tranh chấp.",
                ),
                sec(
                    "RWMutex và giới hạn của nó",
                    "`RLock` cho phép nhiều bên đọc song song, `Lock` là độc quyền. RWMutex "
                    "chỉ thắng khi đọc nhiều hơn ghi rất nhiều lần và vùng tới hạn đủ dài; "
                    "với vùng tới hạn cực ngắn, chi phí bookkeeping làm nó chậm hơn Mutex "
                    "thường.",
                    "Khi tranh chấp trở thành điểm nghẽn, giải pháp thường không phải là "
                    "khoá tinh vi hơn mà là chia dữ liệu thành nhiều shard, mỗi shard một "
                    "mutex — hoặc chuyển sang mô hình một goroutine sở hữu dữ liệu.",
                    note="Mutex trong Go không đệ quy: gọi Lock hai lần trong cùng goroutine sẽ deadlock ngay lập tức.",
                ),
            ],
            samples=[
                code(
                    "Struct tự bảo vệ",
                    """
type Cache struct {
	mu    sync.RWMutex
	items map[string]string
}

func NewCache() *Cache {
	return &Cache{items: make(map[string]string)}
}

func (c *Cache) Get(k string) (string, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	v, ok := c.items[k]
	return v, ok
}

func (c *Cache) Set(k, v string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.items[k] = v
}
""",
                ),
                code(
                    "Sharding để giảm tranh chấp",
                    """
type ShardedCache struct {
	shards [16]struct {
		mu    sync.Mutex
		items map[string]string
	}
}

func (s *ShardedCache) shard(k string) int {
	return int(fnv32(k) % uint32(len(s.shards)))
}
""",
                    explanation="Mười sáu mutex độc lập giảm xác suất hai goroutine giành cùng một khoá.",
                ),
            ],
            takeaways=[
                "Đặt mutex cạnh dữ liệu và cho nó tên, đừng nhúng.",
                "RWMutex chỉ thắng khi đọc áp đảo và vùng tới hạn đủ dài.",
                "Chống tranh chấp bằng sharding hoặc mô hình sở hữu dữ liệu.",
            ],
            exercises=["Benchmark Cache với Mutex và RWMutex ở tỉ lệ đọc/ghi 99:1 và 50:50."],
        ),
        lesson(
            slug="atomic-va-once",
            title="sync/atomic và sync.Once",
            summary="Với bộ đếm và cờ đơn giản, atomic nhanh hơn mutex; Once đảm bảo khởi tạo đúng một lần.",
            level="advanced",
            tags=["dong-thoi", "dong-bo", "hieu-nang"],
            sections=[
                sec(
                    "Kiểu atomic có sẵn",
                    "Từ Go 1.19, `atomic.Int64`, `atomic.Bool`, `atomic.Pointer[T]` cho API "
                    "gọn và an toàn hơn các hàm atomic.AddInt64 kiểu cũ. Chúng đảm bảo thao "
                    "tác đọc–sửa–ghi diễn ra không thể chia cắt, ở mức chỉ thị CPU.",
                    "Atomic chỉ phù hợp cho một biến đơn lẻ. Cần cập nhật hai biến sao cho "
                    "nhất quán với nhau thì phải dùng mutex — nếu không bạn có hai thao tác "
                    "atomic nhưng tổng thể vẫn không nguyên tử.",
                ),
                sec(
                    "sync.Once cho khởi tạo lười",
                    "`once.Do(fn)` chạy fn đúng một lần, kể cả khi hàng trăm goroutine gọi "
                    "cùng lúc; các goroutine khác chờ tới khi fn xong. Đây là cách chuẩn để "
                    "khởi tạo tài nguyên nặng theo yêu cầu.",
                    "Từ Go 1.21 có `sync.OnceValue` và `sync.OnceValues` trả về luôn giá trị "
                    "đã khởi tạo, giúp bỏ đi biến toàn cục trung gian.",
                    note="Nếu fn trong Once panic, Once vẫn coi như đã chạy; lần gọi sau sẽ không thử lại.",
                ),
            ],
            samples=[
                code(
                    "Bộ đếm atomic",
                    """
type Metrics struct {
	requests atomic.Int64
	errors   atomic.Int64
}

func (m *Metrics) Observe(err error) {
	m.requests.Add(1)
	if err != nil {
		m.errors.Add(1)
	}
}

func (m *Metrics) Snapshot() (int64, int64) {
	return m.requests.Load(), m.errors.Load()
}
""",
                ),
                code(
                    "OnceValue cho cấu hình lười",
                    """
var loadConfig = sync.OnceValue(func() Config {
	data, err := os.ReadFile("config.json")
	if err != nil {
		panic(err) // lỗi khởi động: dừng ngay là đúng
	}
	var c Config
	json.Unmarshal(data, &c)
	return c
})

// Mọi lời gọi sau đều dùng lại kết quả đã cache.
cfg := loadConfig()
""",
                ),
            ],
            takeaways=[
                "Kiểu atomic mới (atomic.Int64…) an toàn và gọn hơn API cũ.",
                "Atomic chỉ nguyên tử cho một biến, không cho một bất biến nhiều biến.",
                "`sync.OnceValue` là cách gọn nhất cho khởi tạo lười có trả về giá trị.",
            ],
            exercises=["Thay một bộ đếm dùng mutex bằng atomic.Int64 rồi benchmark hai phiên bản."],
        ),
        lesson(
            slug="context-huy-va-deadline",
            title="context: huỷ bỏ, deadline và giá trị",
            summary="Context là sợi dây truyền tín hiệu huỷ xuyên qua toàn bộ ngăn xếp lời gọi.",
            level="intermediate",
            tags=["dong-thoi", "context", "van-hanh"],
            sections=[
                sec(
                    "Vì sao mọi API đều nhận context",
                    "Khi client ngắt kết nối hoặc request quá deadline, mọi việc đang làm "
                    "cho request đó nên dừng: truy vấn DB, gọi HTTP đi ra, vòng lặp xử lý. "
                    "Context là cách thống nhất để truyền tín hiệu đó xuống mọi tầng.",
                    "Quy ước: `ctx` là tham số đầu tiên, không lưu context vào struct, "
                    "không truyền nil (dùng `context.Background()` hoặc `context.TODO()`).",
                ),
                sec(
                    "Bốn hàm tạo và context value",
                    "`WithCancel` cho huỷ thủ công, `WithTimeout`/`WithDeadline` cho giới "
                    "hạn thời gian, `WithValue` cho dữ liệu theo phạm vi request. Luôn "
                    "`defer cancel()` để giải phóng timer và goroutine nội bộ.",
                    "`WithValue` chỉ nên dùng cho dữ liệu xuyên tầng như request id hay "
                    "trace id, với key là kiểu riêng không xuất. Đừng truyền tham số nghiệp "
                    "vụ qua context — nó biến chữ ký hàm thành lời hứa mờ mịt.",
                    note="Huỷ context không dừng được code đang tính toán; hàm của bạn phải chủ động kiểm tra ctx.Done() hoặc ctx.Err().",
                ),
            ],
            samples=[
                code(
                    "Truyền context xuống mọi tầng",
                    """
func (s *Service) Report(ctx context.Context, id string) (Report, error) {
	ctx, cancel := context.WithTimeout(ctx, 3*time.Second)
	defer cancel()

	rows, err := s.db.QueryContext(ctx, "SELECT ... WHERE user = $1", id)
	if err != nil {
		return Report{}, fmt.Errorf("truy vấn: %w", err)
	}
	defer rows.Close()

	for rows.Next() {
		if err := ctx.Err(); err != nil { // dừng sớm khi bị huỷ
			return Report{}, err
		}
		// ...
	}
	return report, rows.Err()
}
""",
                ),
                code(
                    "Key riêng cho context value",
                    """
type ctxKey int

const requestIDKey ctxKey = iota

func WithRequestID(ctx context.Context, id string) context.Context {
	return context.WithValue(ctx, requestIDKey, id)
}

func RequestID(ctx context.Context) string {
	id, _ := ctx.Value(requestIDKey).(string)
	return id
}
""",
                    explanation="Kiểu key không xuất ra ngoài nên không package nào khác có thể ghi đè giá trị này.",
                ),
            ],
            takeaways=[
                "`ctx` luôn là tham số đầu tiên và không lưu vào struct.",
                "Luôn `defer cancel()` sau các hàm With*.",
                "Vòng lặp dài phải tự kiểm tra `ctx.Err()` để dừng sớm.",
            ],
            exercises=[
                "Thêm context vào một hàm gọi HTTP và kiểm tra nó dừng khi client ngắt kết nối."
            ],
        ),
        lesson(
            slug="worker-pool",
            title="Worker pool: giới hạn mức song song",
            summary="Không phải lúc nào cũng nên tạo một goroutine cho mỗi việc — pool giữ tải trong tầm kiểm soát.",
            level="intermediate",
            tags=["dong-thoi", "mau-hinh", "hieu-nang"],
            sections=[
                sec(
                    "Vì sao cần giới hạn",
                    "Goroutine rẻ, nhưng tài nguyên phía sau thì không: kết nối DB, hạn "
                    "mức API, băng thông đĩa. Tạo 10.000 goroutine cùng gọi một DB có 20 "
                    "kết nối chỉ tạo ra hàng đợi dài và timeout.",
                    "Worker pool cố định N goroutine đọc từ một channel job. N nên xuất phát "
                    "từ tài nguyên hạn chế nhất, không phải từ số CPU.",
                ),
                sec(
                    "Cấu trúc chuẩn",
                    "Một channel jobs, một channel results, N worker, một goroutine đóng "
                    "results sau khi mọi worker xong. Bên gửi job đóng channel jobs khi hết "
                    "việc; vòng `for range jobs` của worker tự kết thúc.",
                    "Biến thể nhẹ hơn: dùng semaphore bằng channel có buffer N để giới hạn "
                    "số goroutine chạy đồng thời mà không cần cấu trúc pool đầy đủ.",
                ),
            ],
            samples=[
                code(
                    "Worker pool đầy đủ",
                    """
func process(ctx context.Context, jobs []Job, workers int) []Result {
	jobCh := make(chan Job)
	resCh := make(chan Result, len(jobs))

	var wg sync.WaitGroup
	for range workers {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for job := range jobCh {
				resCh <- handle(ctx, job)
			}
		}()
	}

	go func() {
		defer close(jobCh)
		for _, j := range jobs {
			select {
			case jobCh <- j:
			case <-ctx.Done():
				return
			}
		}
	}()

	wg.Wait()
	close(resCh)

	out := make([]Result, 0, len(jobs))
	for r := range resCh {
		out = append(out, r)
	}
	return out
}
""",
                ),
                code(
                    "Semaphore bằng channel",
                    """
sem := make(chan struct{}, 8) // tối đa 8 việc song song
var wg sync.WaitGroup

for _, url := range urls {
	wg.Add(1)
	sem <- struct{}{}
	go func() {
		defer wg.Done()
		defer func() { <-sem }()
		fetch(url)
	}()
}
wg.Wait()
""",
                ),
            ],
            takeaways=[
                "Chọn số worker theo tài nguyên hạn chế nhất, không theo số CPU.",
                "Bên gửi job đóng channel jobs; worker dùng `for range`.",
                "Semaphore bằng channel là giải pháp gọn khi không cần pool đầy đủ.",
            ],
            exercises=[
                "Đổi worker pool trên để trả lỗi đầu tiên và huỷ toàn bộ công việc còn lại."
            ],
        ),
        lesson(
            slug="pipeline-va-fan-out",
            title="Pipeline, fan-out và fan-in",
            summary="Ghép các stage nhỏ bằng channel để xử lý dòng dữ liệu với mức song song điều khiển được.",
            level="advanced",
            tags=["dong-thoi", "mau-hinh", "channel"],
            sections=[
                sec(
                    "Một stage trông như thế nào",
                    "Mỗi stage là một hàm nhận channel vào, trả channel ra, và chạy một "
                    "goroutine đọc–biến đổi–ghi. Stage tự đóng channel ra khi channel vào "
                    "đóng, nên tín hiệu kết thúc lan truyền tự nhiên từ đầu tới cuối.",
                    "Fan-out: nhiều stage giống nhau đọc từ cùng một channel để tăng thông "
                    "lượng. Fan-in: gộp nhiều channel ra thành một để tầng sau xử lý.",
                ),
                sec(
                    "Kết thúc sạch",
                    "Mỗi stage phải có nhánh `<-ctx.Done()` ở phép gửi, nếu không khi tầng "
                    "cuối dừng sớm, các tầng trước sẽ bị chặn vĩnh viễn và rò rỉ goroutine. "
                    "Đây là điểm khác biệt giữa một pipeline demo và một pipeline dùng được "
                    "ở production.",
                    "Áp lực ngược (backpressure) có sẵn miễn phí: nếu tầng cuối chậm, "
                    "channel đầy dần và tầng đầu tự chậm lại — không cần cơ chế điều tiết "
                    "nào thêm.",
                    note="Kiểm tra rò rỉ pipeline bằng cách so `runtime.NumGoroutine()` trước và sau khi huỷ context giữa đường.",
                ),
            ],
            samples=[
                code(
                    "Pipeline ba stage có huỷ",
                    """
func generate(ctx context.Context, nums ...int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for _, n := range nums {
			select {
			case out <- n:
			case <-ctx.Done():
				return
			}
		}
	}()
	return out
}

func square(ctx context.Context, in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in {
			select {
			case out <- n * n:
			case <-ctx.Done():
				return
			}
		}
	}()
	return out
}

func main() {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	for v := range square(ctx, generate(ctx, 1, 2, 3, 4)) {
		fmt.Print(v, " ")
	}
}
""",
                    output="1 4 9 16",
                ),
                code(
                    "Fan-out ba worker rồi fan-in",
                    """
src := generate(ctx, nums...)

workers := make([]<-chan int, 3)
for i := range workers {
	workers[i] = square(ctx, src) // ba stage cùng đọc một nguồn
}

for v := range fanIn(ctx, workers...) {
	use(v)
}
""",
                ),
            ],
            takeaways=[
                "Stage nhận channel vào, trả channel ra, tự đóng khi nguồn đóng.",
                "Mọi phép gửi cần nhánh ctx.Done() để không rò rỉ.",
                "Channel cho backpressure miễn phí.",
            ],
            exercises=["Xây pipeline đọc file → parse JSON → lọc → ghi CSV với fan-out 4 worker."],
        ),
        lesson(
            slug="race-detector",
            title="Data race và race detector",
            summary="`go test -race` là công cụ tìm bug đồng thời hiệu quả nhất bạn có.",
            level="intermediate",
            tags=["dong-thoi", "kiem-thu", "cong-cu"],
            sections=[
                sec(
                    "Data race là gì",
                    "Hai goroutine truy cập cùng một vùng nhớ, ít nhất một là ghi, và không "
                    "có đồng bộ hoá giữa chúng. Kết quả không xác định: giá trị sai, map "
                    "hỏng, hoặc crash ngẫu nhiên rất khó tái tạo.",
                    "Race detector theo dõi truy cập bộ nhớ lúc chạy và báo ngay khi phát "
                    "hiện hai truy cập xung đột, kèm stack trace của cả hai bên. Nó chỉ tìm "
                    "được race trên đường code thực sự chạy, nên độ phủ test rất quan trọng.",
                ),
                sec(
                    "Đưa vào quy trình",
                    "Chạy `go test -race ./...` trong CI. Chi phí là chậm hơn 2–10 lần và "
                    "tốn thêm bộ nhớ, nên thường không bật ở production; nhưng bật trên môi "
                    "trường staging chịu tải là cách rất hiệu quả để lộ ra race hiếm.",
                    "Khi detector báo lỗi, đừng “chữa” bằng cách thêm sleep. Hãy xác định "
                    "dữ liệu nào đang dùng chung rồi chọn một trong ba cách: mutex, atomic, "
                    "hoặc thiết kế lại để chỉ một goroutine sở hữu dữ liệu.",
                    note="Không có báo cáo race không chứng minh code đúng; nó chỉ có nghĩa là những đường bạn đã chạy chưa lộ race.",
                ),
            ],
            samples=[
                code(
                    "Race điển hình",
                    """
func TestCounterRace(t *testing.T) {
	count := 0
	var wg sync.WaitGroup
	for range 100 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			count++ // đọc–sửa–ghi không đồng bộ
		}()
	}
	wg.Wait()
}
""",
                    output="WARNING: DATA RACE\nWrite at 0x00c0000140a8 by goroutine 8\nPrevious write at 0x00c0000140a8 by goroutine 7",
                ),
                code(
                    "Ba cách sửa",
                    """
var counter atomic.Int64      // 1) atomic
counter.Add(1)

var mu sync.Mutex             // 2) mutex
mu.Lock(); count++; mu.Unlock()

results := make([]int, n)     // 3) mỗi goroutine một ô riêng
results[i] = compute(i)
""",
                ),
            ],
            takeaways=[
                "Data race = truy cập đồng thời không đồng bộ, ít nhất một là ghi.",
                "`go test -race ./...` nên là bước bắt buộc trong CI.",
                "Sửa race bằng đồng bộ hoá hoặc thiết kế lại quyền sở hữu, không bằng sleep.",
            ],
            exercises=[
                "Chạy test trên với -race, đọc báo cáo, rồi sửa bằng cả ba cách và so sánh."
            ],
        ),
        lesson(
            slug="errgroup-va-ro-ri-goroutine",
            title="errgroup và phòng chống rò rỉ goroutine",
            summary="errgroup gộp WaitGroup, lan truyền lỗi và huỷ context — cộng thêm cách phát hiện rò rỉ.",
            level="advanced",
            tags=["dong-thoi", "mau-hinh", "van-hanh"],
            sections=[
                sec(
                    "errgroup.WithContext",
                    "`g, ctx := errgroup.WithContext(parent)` cho một group mà khi bất kỳ "
                    "hàm nào trả lỗi, ctx bị huỷ và các hàm còn lại nhận được tín hiệu dừng. "
                    "`g.Wait()` trả về lỗi đầu tiên. `g.SetLimit(n)` giới hạn số goroutine "
                    "chạy cùng lúc.",
                    "Đây gần như luôn là lựa chọn tốt hơn WaitGroup thủ công khi các tác vụ "
                    "song song có thể thất bại.",
                ),
                sec(
                    "Phát hiện rò rỉ",
                    "Rò rỉ goroutine hiện ra dưới dạng `runtime.NumGoroutine()` tăng đơn "
                    "điệu theo thời gian và bộ nhớ tăng dần. Trong test, `go.uber.org/goleak` "
                    "kiểm tra sau mỗi test rằng không còn goroutine lạ.",
                    "Ở production, endpoint `/debug/pprof/goroutine?debug=2` in stack của "
                    "mọi goroutine; nếu thấy hàng nghìn goroutine cùng đứng ở một dòng "
                    "`chan send`, bạn đã tìm ra chỗ rò rỉ.",
                    note="Ba nguyên nhân rò rỉ hàng đầu: gửi vào channel không ai đọc, nhận từ channel không ai đóng, và quên gọi cancel().",
                ),
            ],
            samples=[
                code(
                    "errgroup với giới hạn và huỷ",
                    """
func fetchAll(ctx context.Context, urls []string) ([]string, error) {
	g, ctx := errgroup.WithContext(ctx)
	g.SetLimit(8)

	out := make([]string, len(urls))
	for i, url := range urls {
		g.Go(func() error {
			body, err := fetch(ctx, url)
			if err != nil {
				return fmt.Errorf("tải %s: %w", url, err)
			}
			out[i] = body
			return nil
		})
	}
	if err := g.Wait(); err != nil {
		return nil, err // các request còn lại đã bị huỷ qua ctx
	}
	return out, nil
}
""",
                ),
                code(
                    "Kiểm tra rò rỉ trong test",
                    """
func TestMain(m *testing.M) {
	goleak.VerifyTestMain(m)
}
""",
                    explanation="Một dòng này biến mọi test thành bài kiểm tra rò rỉ goroutine.",
                ),
            ],
            takeaways=[
                "errgroup = WaitGroup + lan truyền lỗi + huỷ context.",
                "`SetLimit` giới hạn song song mà không cần pool riêng.",
                "goleak trong test và pprof ở production để bắt rò rỉ.",
            ],
            exercises=["Thêm goleak vào bộ test và sửa các rò rỉ mà nó phát hiện."],
        ),
    ],
)
