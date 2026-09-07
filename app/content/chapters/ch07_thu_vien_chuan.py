"""Chương 7 — Thư viện chuẩn."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="thu-vien-chuan",
    title="Thư viện chuẩn",
    summary=(
        "Go nổi tiếng vì “batteries included”. Chương này đi qua các package bạn "
        "sẽ dùng hằng ngày: fmt, strings, time, json, os, bufio, regexp, flag, embed."
    ),
    lessons=[
        lesson(
            slug="fmt-va-in-du-lieu",
            title="fmt: in, định dạng và ghép chuỗi",
            summary="Một package nhỏ nhưng có mặt trong mọi file Go — nắm các verb là tiết kiệm rất nhiều thời gian debug.",
            level="beginner",
            tags=["thu-vien-chuan", "co-ban"],
            sections=[
                sec(
                    "Ba nhóm hàm",
                    "`Print*` ghi ra stdout, `Fprint*` ghi ra bất kỳ io.Writer, `Sprint*` "
                    "trả về string. Hậu tố `f` nghĩa là có chuỗi định dạng, `ln` nghĩa là "
                    "thêm ký tự xuống dòng.",
                    "Trong code thư viện, hãy ưu tiên `Fprintf(w, ...)` để người gọi quyết "
                    "định đích ghi; đừng in thẳng ra stdout từ trong hàm nghiệp vụ.",
                ),
                sec(
                    "Verb cần nhớ",
                    "`%v` giá trị mặc định, `%+v` kèm tên trường, `%#v` cú pháp Go, `%T` "
                    "kiểu, `%q` chuỗi trong ngoặc kép, `%d/%f/%s` theo kiểu, `%x` hex, "
                    "`%p` con trỏ. `%w` chỉ dùng trong `fmt.Errorf` để bọc lỗi.",
                    "`fmt.Sprintf` cấp phát một chuỗi mới mỗi lần gọi. Trong vòng lặp nóng "
                    "hoặc log tần suất cao, dùng `strings.Builder` hoặc `strconv` sẽ nhanh "
                    "hơn đáng kể.",
                    note="`%v` với một struct chứa con trỏ sẽ in địa chỉ; dùng `%+v` trên giá trị được trỏ nếu muốn thấy nội dung.",
                ),
            ],
            samples=[
                code(
                    "Verb thường dùng",
                    """
type User struct {
	ID   int
	Name string
}
u := User{1, "An"}

fmt.Printf("%v\\n", u)   // {1 An}
fmt.Printf("%+v\\n", u)  // {ID:1 Name:An}
fmt.Printf("%#v\\n", u)  // main.User{ID:1, Name:"An"}
fmt.Printf("%T\\n", u)   // main.User
fmt.Printf("%q\\n", u.Name) // "An"
fmt.Printf("%08.3f\\n", 3.14159) // 0003.142
""",
                    output='{1 An}\n{ID:1 Name:An}\nmain.User{ID:1, Name:"An"}\nmain.User\n"An"\n0003.142',
                ),
            ],
            takeaways=[
                "Fprintf cho thư viện, Printf cho chương trình dòng lệnh.",
                "`%+v` là verb debug hữu dụng nhất.",
                "Sprintf cấp phát; tránh trong hot path.",
            ],
            exercises=["In một bảng thẳng cột bằng `%-10s` và `%6d`."],
        ),
        lesson(
            slug="strings-va-strconv",
            title="strings và strconv",
            summary="Xử lý chuỗi và chuyển đổi số — hai package đơn giản nhưng có nhiều chi tiết đáng biết.",
            level="beginner",
            tags=["thu-vien-chuan", "kieu-du-lieu"],
            sections=[
                sec(
                    "strings: những hàm hay dùng",
                    "`Split`, `Join`, `TrimSpace`, `Contains`, `HasPrefix`, `ReplaceAll`, "
                    "`Fields`, `EqualFold` (so sánh không phân biệt hoa thường), `Cut` (tách "
                    "một lần tại dấu phân cách, trả về cả cờ tìm thấy).",
                    "`strings.Builder` cho ghép chuỗi hiệu quả; `strings.NewReader` biến "
                    "string thành io.Reader để dùng với mọi API I/O — rất tiện trong test.",
                ),
                sec(
                    "strconv: chuyển đổi có kiểm soát",
                    "`Atoi`/`Itoa` cho int, `ParseFloat`, `ParseBool`, `ParseInt` với cơ số "
                    "và bit size tường minh. Tất cả đều trả về lỗi khi input sai — đừng bỏ "
                    "qua lỗi đó, vì đây là biên nhận dữ liệu ngoài.",
                    '`strconv.Itoa(n)` nhanh hơn `fmt.Sprintf("%d", n)` vài lần vì không '
                    "đi qua reflection và không phân tích chuỗi định dạng.",
                ),
            ],
            samples=[
                code(
                    "Cut, EqualFold và parse an toàn",
                    """
key, value, found := strings.Cut("timeout=30s", "=")
fmt.Println(key, value, found)

fmt.Println(strings.EqualFold("Go", "GO"))

n, err := strconv.Atoi("30")
if err != nil {
	// input không phải số: xử lý ở biên
}

port, err := strconv.ParseInt("8080", 10, 32)
fmt.Println(n, port, err)
""",
                    output="timeout 30s true\ntrue\n30 8080 <nil>",
                ),
            ],
            takeaways=[
                "`strings.Cut` gọn hơn Split khi chỉ cần tách một lần.",
                "`strings.NewReader` biến string thành io.Reader cho test.",
                "`strconv.Itoa` nhanh hơn Sprintf cho việc đơn giản.",
            ],
            exercises=["Viết parser cho chuỗi `k1=v1;k2=v2` trả về map, dùng strings.Cut."],
        ),
        lesson(
            slug="time-va-mui-gio",
            title="time: thời điểm, khoảng và múi giờ",
            summary="Monotonic clock, Duration có kiểu, và lý do không bao giờ so sánh Time bằng dấu bằng.",
            level="intermediate",
            tags=["thu-vien-chuan", "van-hanh"],
            sections=[
                sec(
                    "Time và Duration",
                    "`time.Duration` là int64 nano giây nhưng có kiểu riêng, nên "
                    "`5*time.Second` đọc rõ và không lẫn lộn đơn vị. `time.Time` chứa cả "
                    "wall clock và monotonic clock; `time.Since` dùng monotonic nên không "
                    "bị ảnh hưởng khi hệ thống đồng bộ NTP.",
                    "Không so sánh Time bằng `==` vì nó chứa cả monotonic reading và con trỏ "
                    "location. Dùng `t1.Equal(t2)`.",
                ),
                sec(
                    "Định dạng theo mẫu tham chiếu",
                    "Go không dùng %Y-%m-%d mà dùng chính thời điểm tham chiếu "
                    "`2006-01-02 15:04:05` làm mẫu. Lạ lúc đầu nhưng dễ nhớ vì mẫu chính là "
                    "một ví dụ. Ở API, hãy dùng `time.RFC3339`.",
                    "Luôn lưu thời gian ở UTC và chỉ chuyển sang múi giờ địa phương khi "
                    'hiển thị. `time.LoadLocation("Asia/Ho_Chi_Minh")` cần tzdata trên hệ '
                    'thống; trong container tối giản, import `_ "time/tzdata"` để nhúng dữ '
                    "liệu múi giờ vào binary.",
                    note="Bug kinh điển trong container: LoadLocation trả lỗi vì image scratch không có /usr/share/zoneinfo.",
                ),
            ],
            samples=[
                code(
                    "Đo thời gian và định dạng",
                    """
start := time.Now()
work()
elapsed := time.Since(start) // dùng monotonic clock
fmt.Printf("mất %v (%.2f ms)\\n", elapsed, float64(elapsed.Microseconds())/1000)

t := time.Date(2026, 9, 7, 13, 30, 0, 0, time.UTC)
fmt.Println(t.Format(time.RFC3339))
fmt.Println(t.Format("02/01/2006 15:04"))

loc, err := time.LoadLocation("Asia/Ho_Chi_Minh")
if err == nil {
	fmt.Println(t.In(loc).Format("15:04 -0700"))
}
""",
                    output="mất 1.2ms (1.20 ms)\n2026-09-07T13:30:00Z\n07/09/2026 13:30\n20:30 +0700",
                ),
            ],
            takeaways=[
                "Duration có kiểu riêng nên đơn vị luôn tường minh.",
                "So sánh Time bằng `Equal`, không bằng `==`.",
                "Lưu UTC, hiển thị theo local; nhúng tzdata khi cần.",
            ],
            exercises=["Viết hàm định dạng khoảng thời gian thành “2 giờ 5 phút” từ một Duration."],
        ),
        lesson(
            slug="encoding-json",
            title="encoding/json: mã hoá và giải mã",
            summary="Struct tag điều khiển toàn bộ hình dạng JSON, và những cạm bẫy về zero value.",
            level="beginner",
            tags=["thu-vien-chuan", "web"],
            sections=[
                sec(
                    "Marshal và Unmarshal",
                    "`json.Marshal(v)` sinh []byte, `json.Unmarshal(data, &v)` giải mã vào "
                    "con trỏ. Với stream, `json.NewEncoder(w).Encode(v)` và "
                    "`json.NewDecoder(r).Decode(&v)` tránh phải giữ toàn bộ dữ liệu trong "
                    "bộ nhớ — đây là dạng nên dùng trong HTTP handler.",
                    'Chỉ trường được export mới được mã hoá. Tag `json:"name,omitempty"` '
                    'đổi tên và bỏ trường khi giá trị là zero; `json:"-"` loại hẳn trường.',
                ),
                sec(
                    "Cạm bẫy zero value và omitempty",
                    "`omitempty` không phân biệt “không gửi” với “gửi giá trị 0”. Nếu API cần "
                    "phân biệt, dùng con trỏ (`*int`) hoặc `json.RawMessage` rồi tự kiểm tra. "
                    "Ngược lại, khi giải mã, trường thiếu sẽ giữ nguyên giá trị hiện tại của "
                    "struct — không bị reset về zero.",
                    "`DisallowUnknownFields` giúp phát hiện client gửi sai tên trường thay vì "
                    "âm thầm bỏ qua. Số trong JSON giải mã vào `any` sẽ thành float64, dễ gây "
                    "bất ngờ khi so sánh.",
                    note="Với tiền tệ, đừng dùng float64. Hãy lưu số nguyên đơn vị nhỏ nhất (cents) hoặc dùng string.",
                ),
            ],
            samples=[
                code(
                    "Decode có kiểm soát trong handler",
                    """
type CreateUser struct {
	Email string  `json:"email"`
	Age   *int    `json:"age,omitempty"` // phân biệt thiếu và 0
}

func handler(w http.ResponseWriter, r *http.Request) {
	var in CreateUser
	dec := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20))
	dec.DisallowUnknownFields()

	if err := dec.Decode(&in); err != nil {
		http.Error(w, "JSON không hợp lệ", http.StatusBadRequest)
		return
	}
	if in.Age == nil {
		// client không gửi trường age
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}
""",
                ),
            ],
            takeaways=[
                "Dùng Encoder/Decoder cho stream, Marshal/Unmarshal cho dữ liệu nhỏ.",
                "`omitempty` không phân biệt thiếu và zero — dùng con trỏ nếu cần.",
                "Giới hạn kích thước body và bật DisallowUnknownFields ở API công khai.",
            ],
            exercises=[
                "Viết struct cho một payload JSON lồng nhau và test round-trip Marshal/Unmarshal."
            ],
        ),
        lesson(
            slug="os-va-file",
            title="os và làm việc với file",
            summary="Đọc, ghi, quyền truy cập và cách ghi file an toàn bằng rename nguyên tử.",
            level="beginner",
            tags=["thu-vien-chuan", "io"],
            sections=[
                sec(
                    "Đọc và ghi cơ bản",
                    "`os.ReadFile`/`os.WriteFile` cho file nhỏ, gọn trong một dòng. Với file "
                    "lớn, `os.Open` rồi đọc theo khối qua bufio để không nạp hết vào bộ nhớ.",
                    "`os.Args` cho tham số dòng lệnh, `os.Getenv`/`os.LookupEnv` cho biến môi "
                    "trường (LookupEnv phân biệt “không đặt” với “đặt rỗng”), `os.Exit` để "
                    "kết thúc với mã trạng thái — nhưng nhớ os.Exit không chạy defer.",
                ),
                sec(
                    "Ghi file an toàn",
                    "Ghi trực tiếp lên file đích khiến file bị hỏng nếu process chết giữa "
                    "đường. Mẫu an toàn: ghi ra file tạm cùng thư mục, `Sync()` để đẩy xuống "
                    "đĩa, rồi `os.Rename` — rename trong cùng filesystem là nguyên tử.",
                    "Kiểm tra sự tồn tại bằng `errors.Is(err, os.ErrNotExist)` sau khi thao "
                    "tác, không phải bằng `os.Stat` trước đó — kiểm tra rồi mới dùng là mẫu "
                    "có race.",
                    note='`filepath.Join` thay vì nối chuỗi bằng "/" để code chạy đúng trên mọi hệ điều hành.',
                ),
            ],
            samples=[
                code(
                    "Ghi nguyên tử",
                    """
func writeAtomic(path string, data []byte) error {
	dir := filepath.Dir(path)
	tmp, err := os.CreateTemp(dir, ".tmp-*")
	if err != nil {
		return err
	}
	defer os.Remove(tmp.Name()) // dọn nếu có lỗi giữa đường

	if _, err := tmp.Write(data); err != nil {
		tmp.Close()
		return err
	}
	if err := tmp.Sync(); err != nil {
		tmp.Close()
		return err
	}
	if err := tmp.Close(); err != nil {
		return err
	}
	return os.Rename(tmp.Name(), path)
}
""",
                ),
            ],
            takeaways=[
                "ReadFile/WriteFile cho file nhỏ; stream cho file lớn.",
                "Ghi tạm + Sync + Rename để không bao giờ để lại file hỏng.",
                "`os.Exit` bỏ qua defer — dọn dẹp trước khi gọi.",
            ],
            exercises=["Viết hàm đọc file cấu hình, trả về lỗi rõ ràng khi file không tồn tại."],
        ),
        lesson(
            slug="bufio-va-scanner",
            title="bufio: đệm và quét dòng",
            summary="Một lớp đệm mỏng biến hàng nghìn syscall thành vài chục.",
            level="intermediate",
            tags=["thu-vien-chuan", "io", "hieu-nang"],
            sections=[
                sec(
                    "Vì sao cần đệm",
                    "Mỗi lời gọi Read trên file hay socket là một syscall. Đọc từng byte "
                    "nghĩa là hàng triệu syscall. `bufio.Reader` đọc một khối lớn vào bộ "
                    "nhớ rồi phục vụ các lời gọi nhỏ từ đó.",
                    "`bufio.Writer` làm điều ngược lại và **bắt buộc** phải `Flush()` trước "
                    "khi kết thúc, nếu không phần dữ liệu còn trong đệm sẽ mất.",
                ),
                sec(
                    "Scanner và giới hạn dòng",
                    "`bufio.Scanner` quét theo dòng (mặc định), theo từ hoặc theo rune. Nó "
                    "có giới hạn 64 KB cho một token; dòng dài hơn sẽ khiến Scan trả về false "
                    "kèm `bufio.ErrTooLong`. Tăng bằng `scanner.Buffer(buf, max)`.",
                    "Luôn kiểm tra `scanner.Err()` sau vòng lặp: `Scan()` trả về false cả khi "
                    "hết dữ liệu và khi có lỗi, và bỏ qua điều này là bug âm thầm hay gặp.",
                    note="Xử lý log JSON theo dòng với Scanner + json.Unmarshal cho từng dòng là mẫu rất hiệu quả và tốn ít bộ nhớ.",
                ),
            ],
            samples=[
                code(
                    "Đọc file lớn theo dòng",
                    """
func countErrors(path string) (int, error) {
	f, err := os.Open(path)
	if err != nil {
		return 0, err
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 0, 64*1024), 1024*1024) // cho phép dòng tới 1 MB

	count := 0
	for scanner.Scan() {
		if strings.Contains(scanner.Text(), `"level":"ERROR"`) {
			count++
		}
	}
	return count, scanner.Err() // đừng bỏ qua lỗi này
}
""",
                ),
                code(
                    "Writer phải Flush",
                    """
w := bufio.NewWriter(f)
defer w.Flush() // thiếu dòng này là mất dữ liệu

for _, line := range lines {
	fmt.Fprintln(w, line)
}
""",
                ),
            ],
            takeaways=[
                "Đệm gộp nhiều thao tác nhỏ thành ít syscall.",
                "bufio.Writer phải Flush, thường bằng defer.",
                "Luôn kiểm tra `scanner.Err()` sau vòng lặp Scan.",
            ],
            exercises=["Đo thời gian đếm dòng của file 100 MB có và không có bufio."],
        ),
        lesson(
            slug="regexp",
            title="regexp: biểu thức chính quy tuyến tính",
            summary="Go dùng RE2 nên không có backtracking bùng nổ, nhưng cũng không có lookahead.",
            level="intermediate",
            tags=["thu-vien-chuan", "hieu-nang"],
            sections=[
                sec(
                    "RE2: đánh đổi có chủ đích",
                    "Engine RE2 đảm bảo thời gian chạy tuyến tính theo độ dài input, nên "
                    "không thể bị tấn công ReDoS. Cái giá là không hỗ trợ lookahead, "
                    "lookbehind và backreference.",
                    "Nếu bạn cần các tính năng đó, thường có thể viết lại bằng hai bước xử "
                    "lý đơn giản — và code sẽ dễ đọc hơn regex phức tạp.",
                ),
                sec(
                    "Biên dịch một lần",
                    "`regexp.MustCompile` ở cấp package biên dịch lúc khởi động và panic ngay "
                    "nếu pattern sai — đúng chỗ để phát hiện lỗi. Đừng bao giờ compile regex "
                    "trong vòng lặp hay trong handler.",
                    "Với các việc đơn giản như kiểm tra tiền tố hay tách theo dấu, "
                    "`strings.HasPrefix` và `strings.Cut` nhanh hơn regex hàng chục lần.",
                    note="Regex biên dịch trong hot path là một trong những nguyên nhân chậm dễ sửa nhất mà pprof hay chỉ ra.",
                ),
            ],
            samples=[
                code(
                    "Nhóm có tên và biên dịch một lần",
                    """
var logLine = regexp.MustCompile(
	`^(?P<ip>\\S+) \\S+ \\S+ \\[(?P<time>[^\\]]+)\\] "(?P<method>\\w+) (?P<path>\\S+)`,
)

func parse(line string) map[string]string {
	m := logLine.FindStringSubmatch(line)
	if m == nil {
		return nil
	}
	out := make(map[string]string, len(m))
	for i, name := range logLine.SubexpNames() {
		if i > 0 && name != "" {
			out[name] = m[i]
		}
	}
	return out
}
""",
                    output="map[ip:10.0.0.1 method:GET path:/api time:...]",
                ),
            ],
            takeaways=[
                "RE2 cho thời gian tuyến tính nhưng không có lookahead/backreference.",
                "MustCompile ở cấp package, không compile trong vòng lặp.",
                "Việc đơn giản thì dùng strings, nhanh hơn regex nhiều.",
            ],
            exercises=[
                "Thay một regex kiểm tra tiền tố bằng strings.HasPrefix và benchmark hai cách."
            ],
        ),
        lesson(
            slug="flag-va-cli",
            title="flag: chương trình dòng lệnh",
            summary="Package flag đủ cho phần lớn CLI; biết khi nào cần công cụ mạnh hơn.",
            level="beginner",
            tags=["thu-vien-chuan", "cong-cu"],
            sections=[
                sec(
                    "Khai báo và phân tích",
                    "`flag.String`, `flag.Int`, `flag.Bool`, `flag.Duration` khai báo cờ và "
                    "trả về con trỏ; gọi `flag.Parse()` một lần trong main. Dạng `*Var` cho "
                    "phép ghi trực tiếp vào một biến hoặc struct cấu hình.",
                    "Cờ không khai báo sẽ gây lỗi và in usage — hành vi mặc định hợp lý cho "
                    "công cụ nội bộ.",
                ),
                sec(
                    "Khi nào cần hơn thế",
                    "flag không hỗ trợ subcommand kiểu `git commit`. Với CLI nhiều lệnh con, "
                    "bạn có thể tự tạo nhiều `flag.NewFlagSet` hoặc dùng thư viện như cobra. "
                    "Nhưng đừng thêm phụ thuộc chỉ để có hai cờ.",
                    "Mẫu tốt cho service: đọc cấu hình từ cờ, có giá trị mặc định từ biến môi "
                    "trường. Nhờ vậy chạy local thì tiện mà container thì đúng chuẩn 12-factor.",
                ),
            ],
            samples=[
                code(
                    "Cấu hình từ cờ và env",
                    """
type Config struct {
	Addr    string
	Timeout time.Duration
}

func parseConfig(args []string) (Config, error) {
	fs := flag.NewFlagSet("api", flag.ContinueOnError)
	var c Config
	fs.StringVar(&c.Addr, "addr", envOr("ADDR", ":8080"), "địa chỉ lắng nghe")
	fs.DurationVar(&c.Timeout, "timeout", 15*time.Second, "timeout xử lý request")
	if err := fs.Parse(args); err != nil {
		return Config{}, err
	}
	return c, nil
}

func envOr(key, def string) string {
	if v, ok := os.LookupEnv(key); ok {
		return v
	}
	return def
}
""",
                    explanation="Tách hàm nhận []string giúp test cấu hình mà không cần chạm vào os.Args.",
                ),
            ],
            takeaways=[
                "flag.Parse gọi một lần trong main.",
                "Dùng FlagSet riêng để hàm cấu hình test được.",
                "Cờ với mặc định từ env là mẫu tiện cho cả local và container.",
            ],
            exercises=[
                "Viết CLI nhận `-input` và `-workers` rồi test hàm parseConfig với nhiều bộ tham số."
            ],
        ),
        lesson(
            slug="embed-tai-nguyen",
            title="embed: nhúng tài nguyên vào binary",
            summary="Template, migration, file tĩnh nằm ngay trong binary — triển khai chỉ còn một file.",
            level="intermediate",
            tags=["thu-vien-chuan", "van-hanh"],
            sections=[
                sec(
                    "Cách dùng",
                    "Import `embed` rồi đặt chỉ thị `//go:embed` ngay trên biến kiểu string, "
                    "[]byte hoặc `embed.FS`. Nội dung file được đưa vào binary lúc biên dịch, "
                    "nên không còn phụ thuộc đường dẫn lúc chạy.",
                    "Đường dẫn trong chỉ thị là tương đối với file Go và không được ra ngoài "
                    "package. Không thể nhúng file ngoài cây module.",
                ),
                sec(
                    "Vì sao điều này quan trọng",
                    "Trước embed, triển khai một web app Go phải kèm thư mục templates và "
                    "static, dễ lệch phiên bản. Nay `docker build` chỉ cần copy một binary "
                    "vào image scratch — image vài chục MB và không có gì để lệch.",
                    "`embed.FS` thoả interface `fs.FS`, nên dùng trực tiếp được với "
                    "`http.FileServerFS` và `template.ParseFS`.",
                    note="Trong lúc phát triển, bạn có thể chuyển giữa embed.FS và os.DirFS bằng một biến cấu hình để sửa template không cần build lại.",
                ),
            ],
            samples=[
                code(
                    "Nhúng template và file tĩnh",
                    """
import "embed"

//go:embed templates/*.html
var templateFS embed.FS

//go:embed static
var staticFS embed.FS

var tmpl = template.Must(template.ParseFS(templateFS, "templates/*.html"))

func main() {
	mux := http.NewServeMux()
	mux.Handle("/static/", http.FileServerFS(staticFS))
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		tmpl.ExecuteTemplate(w, "index.html", nil)
	})
	http.ListenAndServe(":8080", mux)
}
""",
                ),
            ],
            takeaways=[
                "`//go:embed` đưa tài nguyên vào binary lúc biên dịch.",
                "embed.FS thoả fs.FS nên dùng được với template và FileServer.",
                "Một binary duy nhất làm việc triển khai đơn giản hẳn.",
            ],
            exercises=["Nhúng một file JSON dữ liệu mẫu và đọc nó trong test."],
        ),
    ],
)
