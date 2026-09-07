"""Chương 10 — Kiểm thử."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="kiem-thu",
    title="Kiểm thử",
    summary=(
        "Testing nằm trong thư viện chuẩn: table-driven test, subtest song song, "
        "httptest, benchmark, fuzzing và golden file — không cần framework."
    ),
    lessons=[
        lesson(
            slug="go-test-co-ban",
            title="go test: quy ước và vòng lặp cơ bản",
            summary="File _test.go, hàm TestXxx, và một API assertion tối giản đến mức gây tranh cãi.",
            level="beginner",
            tags=["kiem-thu", "cong-cu"],
            sections=[
                sec(
                    "Quy ước",
                    "Test nằm trong file kết thúc bằng `_test.go`, hàm có dạng "
                    "`func TestXxx(t *testing.T)`. File test cùng package thì thấy được cả "
                    "định danh nội bộ; đặt package `foo_test` thì chỉ thấy API công khai — "
                    "cách tốt để test đúng góc nhìn của người dùng.",
                    "`t.Errorf` báo lỗi nhưng tiếp tục; `t.Fatalf` dừng test ngay. Dùng "
                    "Fatalf khi các bước sau không còn ý nghĩa.",
                ),
                sec(
                    "Không có assert, và đó là chủ ý",
                    "Go không cung cấp `assertEqual`. Bạn viết `if got != want { t.Errorf(...) }`. "
                    "Thông điệp lỗi nên theo mẫu “got X, want Y” để người đọc log hiểu ngay "
                    "mà không cần mở code.",
                    "Với so sánh struct và slice, `reflect.DeepEqual` hoặc "
                    "`google/go-cmp` cho diff dễ đọc. go-cmp là một trong ít phụ thuộc test "
                    "thật sự đáng thêm.",
                    note="`go test ./... -count=1` bỏ qua cache kết quả test; hữu ích khi test phụ thuộc môi trường bên ngoài.",
                ),
            ],
            samples=[
                code(
                    "Test đầu tiên",
                    """
func TestSlugify(t *testing.T) {
	got := Slugify("Xin chào Go!")
	want := "xin-chao-go"
	if got != want {
		t.Errorf("Slugify() = %q, want %q", got, want)
	}
}
""",
                ),
                code(
                    "Các lệnh hay dùng",
                    """
go test ./...
go test -run TestSlugify ./internal/text
go test -v -race -count=1 ./...
go test -cover ./...
""",
                    language="bash",
                ),
            ],
            takeaways=[
                "File `_test.go`, hàm `TestXxx(t *testing.T)`.",
                "Package `foo_test` buộc test qua API công khai.",
                "Thông điệp lỗi theo mẫu “got X, want Y”.",
            ],
            exercises=["Viết test cho một hàm thuần trong dự án của bạn và chạy với -race."],
        ),
        lesson(
            slug="table-driven-test",
            title="Table-driven test",
            summary="Mẫu test đặc trưng của Go: dữ liệu là bảng, logic kiểm tra viết một lần.",
            level="beginner",
            tags=["kiem-thu", "mau-hinh"],
            sections=[
                sec(
                    "Cấu trúc",
                    "Một slice struct ẩn danh chứa tên trường hợp, input và kết quả mong đợi; "
                    "vòng lặp chạy từng dòng trong một subtest. Thêm trường hợp mới chỉ là "
                    "thêm một dòng dữ liệu.",
                    "Đặt tên trường hợp mô tả **hành vi** đang kiểm tra, không phải input: "
                    "“chuỗi rỗng trả về lỗi” tốt hơn “test 3”.",
                ),
                sec(
                    "Bao phủ biên",
                    "Bảng khuyến khích bạn nghĩ theo lớp tương đương: giá trị hợp lệ điển "
                    "hình, biên dưới, biên trên, giá trị âm, chuỗi rỗng, Unicode, giá trị "
                    "cực lớn. Đó là nơi bug thật sự trú ngụ.",
                    "Với hàm trả về lỗi, hãy kiểm tra loại lỗi bằng `errors.Is`, không so sánh "
                    "chuỗi thông điệp — thông điệp sẽ thay đổi và test sẽ vỡ vô cớ.",
                ),
            ],
            samples=[
                code(
                    "Bảng đầy đủ với trường hợp lỗi",
                    """
func TestParseDuration(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		want    time.Duration
		wantErr error
	}{
		{"giây", "30s", 30 * time.Second, nil},
		{"phút", "5m", 5 * time.Minute, nil},
		{"số âm", "-1s", -time.Second, nil},
		{"chuỗi rỗng", "", 0, ErrEmptyInput},
		{"đơn vị lạ", "10x", 0, ErrBadUnit},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ParseDuration(tt.input)
			if !errors.Is(err, tt.wantErr) {
				t.Fatalf("err = %v, want %v", err, tt.wantErr)
			}
			if got != tt.want {
				t.Errorf("got %v, want %v", got, tt.want)
			}
		})
	}
}
""",
                    output="--- PASS: TestParseDuration/chuỗi_rỗng\n--- PASS: TestParseDuration/đơn_vị_lạ",
                ),
            ],
            takeaways=[
                "Bảng dữ liệu + một vòng lặp = thêm test chỉ là thêm dòng.",
                "Tên trường hợp mô tả hành vi, không mô tả input.",
                "So sánh lỗi bằng `errors.Is`, không bằng chuỗi.",
            ],
            exercises=["Chuyển một test có nhiều khối lặp lại thành table-driven."],
        ),
        lesson(
            slug="subtest-va-parallel",
            title="Subtest, t.Parallel và t.Cleanup",
            summary="Chạy song song để bộ test nhanh hơn — nếu các trường hợp thật sự độc lập.",
            level="intermediate",
            tags=["kiem-thu", "dong-thoi"],
            sections=[
                sec(
                    "t.Run và cây test",
                    "`t.Run(name, fn)` tạo subtest có thể chạy chọn lọc: "
                    "`go test -run 'TestX/tên_con'`. Mỗi subtest có `*testing.T` riêng, nên "
                    "Fatalf chỉ dừng subtest đó.",
                    "`t.Cleanup(fn)` đăng ký dọn dẹp chạy khi test (và mọi subtest của nó) "
                    "kết thúc — rõ ràng hơn defer khi có nhiều lớp thiết lập.",
                ),
                sec(
                    "Song song hoá đúng cách",
                    "Gọi `t.Parallel()` ở đầu subtest để nó chạy song song với các subtest "
                    "song song khác. Điều kiện: không dùng chung state đáng kể, không phụ "
                    "thuộc thứ tự, không cùng ghi vào một file hay bảng.",
                    "Từ Go 1.22, biến vòng lặp là biến riêng mỗi vòng nên mẫu "
                    "`tt := tt` không còn cần thiết. Nếu vẫn hỗ trợ phiên bản cũ hơn thì hãy "
                    "giữ dòng đó.",
                    note="Song song hoá test chạm database sẽ tạo race trên dữ liệu; hãy cho mỗi test một schema hoặc prefix riêng.",
                ),
            ],
            samples=[
                code(
                    "Subtest song song với cleanup",
                    """
func TestHandlers(t *testing.T) {
	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			dir := t.TempDir() // tự xoá khi test xong
			srv := newTestServer(t, dir)
			t.Cleanup(srv.Close)

			resp := srv.get(tt.path)
			if resp.StatusCode != tt.wantStatus {
				t.Errorf("status = %d, want %d", resp.StatusCode, tt.wantStatus)
			}
		})
	}
}
""",
                ),
            ],
            takeaways=[
                "Subtest cho phép chạy chọn lọc và báo lỗi độc lập.",
                "`t.Parallel()` chỉ khi trường hợp thật sự độc lập.",
                "`t.TempDir` và `t.Cleanup` lo phần dọn dẹp.",
            ],
            exercises=["Thêm t.Parallel vào một bộ test và đo thời gian trước/sau."],
        ),
        lesson(
            slug="httptest",
            title="httptest: test HTTP không cần mạng",
            summary="ResponseRecorder cho handler, httptest.Server cho client — cả hai đều nhanh và đáng tin.",
            level="intermediate",
            tags=["kiem-thu", "web"],
            sections=[
                sec(
                    "Test handler",
                    "`httptest.NewRequest` tạo request giả, `httptest.NewRecorder` bắt "
                    "response. Gọi trực tiếp `handler.ServeHTTP(rec, req)` — không mở socket, "
                    "không cần port, chạy trong micro giây.",
                    "Test toàn bộ mux (kể cả middleware) thay vì từng handler rời rạc sẽ bao "
                    "phủ cả routing và thứ tự middleware, nơi bug thường ẩn.",
                ),
                sec(
                    "Test client",
                    "`httptest.NewServer(handler)` mở server thật trên port tạm, cho bạn URL "
                    "để client trong code gọi tới. Đây là cách đúng để test wrapper API bên "
                    "thứ ba: mô phỏng cả 200, 500, timeout và JSON sai định dạng.",
                    "Đừng mock `http.Client`. Với httptest bạn test cả đường đi thật của HTTP: "
                    "header, status, body, và cách code xử lý chúng.",
                    note="Mô phỏng timeout bằng handler có `time.Sleep` dài hơn timeout của client — cách kiểm tra nhánh lỗi hay bị bỏ quên.",
                ),
            ],
            samples=[
                code(
                    "Test handler qua mux đầy đủ",
                    """
func TestGetUser(t *testing.T) {
	mux := newRouter(testStore{})

	req := httptest.NewRequest(http.MethodGet, "/users/42", nil)
	rec := httptest.NewRecorder()

	mux.ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("status = %d, body = %s", rec.Code, rec.Body.String())
	}
	var got User
	if err := json.Unmarshal(rec.Body.Bytes(), &got); err != nil {
		t.Fatalf("body không phải JSON: %v", err)
	}
	if got.ID != 42 {
		t.Errorf("id = %d, want 42", got.ID)
	}
}
""",
                ),
                code(
                    "Test client với server giả",
                    """
func TestFetchUser_ServerError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
	}))
	defer srv.Close()

	client := NewAPIClient(srv.URL)
	_, err := client.FetchUser(context.Background(), "1")
	if err == nil {
		t.Fatal("mong đợi lỗi khi server trả 500")
	}
}
""",
                ),
            ],
            takeaways=[
                "NewRequest + NewRecorder để test handler cực nhanh.",
                "Test qua mux đầy đủ để bao phủ routing và middleware.",
                "httptest.Server thay cho mock client.",
            ],
            exercises=["Viết test cho nhánh timeout của HTTP client bằng handler có sleep."],
        ),
        lesson(
            slug="test-double-va-interface",
            title="Test double: fake, stub và spy",
            summary="Interface hẹp làm test double trở thành vài dòng struct, không cần thư viện sinh mock.",
            level="intermediate",
            tags=["kiem-thu", "kien-truc"],
            sections=[
                sec(
                    "Ba loại double",
                    "Stub trả về giá trị cố định. Fake là hiện thực đơn giản nhưng hoạt động "
                    "thật (ví dụ store trong bộ nhớ). Spy ghi lại các lời gọi để bạn kiểm tra "
                    "sau. Trong Go, cả ba đều chỉ là một struct nhỏ hiện thực interface.",
                    "Vì interface nên hẹp (1–3 phương thức), viết tay double thường nhanh hơn "
                    "cấu hình một thư viện mock, và code test đọc dễ hơn nhiều.",
                ),
                sec(
                    "Mock cái gì, dùng thật cái gì",
                    "Dùng thật với những gì bạn sở hữu và chạy nhanh: hàm thuần, DB trong "
                    "Docker, filesystem qua t.TempDir. Dùng double cho những gì bạn không sở "
                    "hữu hoặc chậm/không xác định: API bên thứ ba, đồng hồ hệ thống, số ngẫu "
                    "nhiên.",
                    "Với thời gian, hãy tiêm một `func() time.Time` thay vì gọi trực tiếp "
                    "`time.Now()`. Test thời gian trở nên xác định và không cần sleep.",
                    note="Nếu double của bạn dài hơn code nó thay thế, khả năng cao là interface quá rộng.",
                ),
            ],
            samples=[
                code(
                    "Fake store và spy notifier",
                    """
type fakeStore struct {
	users map[string]User
}

func (f *fakeStore) User(_ context.Context, id string) (User, error) {
	u, ok := f.users[id]
	if !ok {
		return User{}, ErrNotFound
	}
	return u, nil
}

type spyNotifier struct {
	sent []string
}

func (s *spyNotifier) Notify(_ context.Context, email string) error {
	s.sent = append(s.sent, email)
	return nil
}

func TestWelcomeFlow(t *testing.T) {
	spy := &spyNotifier{}
	svc := NewService(&fakeStore{users: map[string]User{"1": {Email: "a@b.c"}}}, spy)

	if err := svc.Welcome(context.Background(), "1"); err != nil {
		t.Fatal(err)
	}
	if len(spy.sent) != 1 || spy.sent[0] != "a@b.c" {
		t.Errorf("đã gửi %v", spy.sent)
	}
}
""",
                ),
                code(
                    "Tiêm đồng hồ",
                    """
type Service struct {
	now func() time.Time
}

func New() *Service { return &Service{now: time.Now} }

// trong test:
svc := &Service{now: func() time.Time {
	return time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)
}}
""",
                ),
            ],
            takeaways=[
                "Interface hẹp cho phép viết double bằng vài dòng.",
                "Dùng thật với thứ bạn sở hữu, double với thứ bạn không sở hữu.",
                "Tiêm đồng hồ để test thời gian xác định.",
            ],
            exercises=["Thay time.Now() trực tiếp trong một service bằng đồng hồ tiêm vào."],
        ),
        lesson(
            slug="benchmark",
            title="Benchmark và cách đọc kết quả",
            summary="`go test -bench` cho ns/op, B/op và allocs/op — ba con số dẫn đường mọi tối ưu.",
            level="intermediate",
            tags=["kiem-thu", "hieu-nang"],
            sections=[
                sec(
                    "Viết benchmark đúng",
                    "Hàm `BenchmarkXxx(b *testing.B)` chạy vòng lặp `for range b.N` (hoặc "
                    "`for i := 0; i < b.N; i++`). Đặt thiết lập nặng trước vòng lặp và gọi "
                    "`b.ResetTimer()`. Dùng `b.ReportAllocs()` để luôn thấy số cấp phát.",
                    "Cạm bẫy lớn nhất: compiler loại bỏ code không có tác dụng. Hãy gán kết "
                    "quả vào một biến ở phạm vi package, hoặc dùng `b.Keep` / "
                    "`runtime.KeepAlive` để giữ lại.",
                ),
                sec(
                    "Đọc và so sánh",
                    "Kết quả gồm số lần lặp, ns/op, B/op, allocs/op. Số cấp phát thường là "
                    "chỉ báo tốt nhất: giảm allocs/op gần như luôn giảm cả ns/op và áp lực GC.",
                    "So sánh hai phiên bản bằng `benchstat`: nó chạy thống kê trên nhiều lần "
                    "đo và cho biết khác biệt có ý nghĩa hay chỉ là nhiễu. Một lần đo đơn lẻ "
                    "không chứng minh được gì.",
                    note="Benchmark trên máy dev có nhiễu lớn. Dùng `-count=10` rồi benchstat, và tắt các tiến trình nặng khác.",
                ),
            ],
            samples=[
                code(
                    "Benchmark so sánh hai cách ghép chuỗi",
                    """
var sink string

func BenchmarkConcatPlus(b *testing.B) {
	b.ReportAllocs()
	for range b.N {
		s := ""
		for i := range 100 {
			s += strconv.Itoa(i)
		}
		sink = s
	}
}

func BenchmarkConcatBuilder(b *testing.B) {
	b.ReportAllocs()
	for range b.N {
		var sb strings.Builder
		sb.Grow(300)
		for i := range 100 {
			sb.WriteString(strconv.Itoa(i))
		}
		sink = sb.String()
	}
}
""",
                    output=(
                        "BenchmarkConcatPlus-8      64821    18294 ns/op   21560 B/op   99 allocs/op\n"
                        "BenchmarkConcatBuilder-8  892134     1342 ns/op     512 B/op    2 allocs/op"
                    ),
                ),
                code(
                    "So sánh bằng benchstat",
                    """
go test -bench=Concat -count=10 ./... > old.txt
# sửa code
go test -bench=Concat -count=10 ./... > new.txt
benchstat old.txt new.txt
""",
                    language="bash",
                ),
            ],
            takeaways=[
                "ResetTimer sau thiết lập; ReportAllocs để thấy cấp phát.",
                "Gán kết quả vào biến ngoài để compiler không loại bỏ code.",
                "Dùng -count nhiều lần + benchstat, đừng tin một lần đo.",
            ],
            exercises=["Benchmark hai cách nối slice và giảm allocs/op về mức tối thiểu."],
        ),
        lesson(
            slug="fuzzing",
            title="Fuzzing trong thư viện chuẩn",
            summary="Từ Go 1.18, `go test -fuzz` tự sinh input tìm panic và vi phạm bất biến.",
            level="advanced",
            tags=["kiem-thu", "bao-mat"],
            sections=[
                sec(
                    "Cách hoạt động",
                    "Hàm `FuzzXxx(f *testing.F)` khai báo vài input hạt giống bằng `f.Add` rồi "
                    "một hàm kiểm tra. Bộ fuzz biến đổi hạt giống, ưu tiên các input mở ra "
                    "đường code mới (coverage-guided), và chạy hàng triệu lần.",
                    "Khi tìm được input làm crash hoặc vi phạm điều kiện, Go lưu nó vào "
                    "`testdata/fuzz/` và từ đó nó trở thành test hồi quy thông thường.",
                ),
                sec(
                    "Viết thuộc tính kiểm tra",
                    "Fuzz mạnh nhất khi bạn kiểm tra một thuộc tính bất biến chứ không phải "
                    "một giá trị cụ thể. Ví dụ: encode rồi decode phải cho lại dữ liệu ban "
                    "đầu; parser không được panic với bất kỳ input nào; hàm chuẩn hoá phải "
                    "idempotent.",
                    "Ứng dụng rõ nhất: mọi thứ phân tích dữ liệu không tin cậy — parser, "
                    "decoder, hàm xử lý đầu vào từ người dùng. Đây chính là nơi lỗ hổng bảo "
                    "mật thường nằm.",
                    note="Chạy fuzz định kỳ (nightly) với `-fuzztime=10m`; chạy trong CI mỗi PR thì chỉ dùng corpus đã lưu.",
                ),
            ],
            samples=[
                code(
                    "Fuzz round-trip",
                    """
func FuzzEncodeDecode(f *testing.F) {
	f.Add("hello")
	f.Add("")
	f.Add("Việt Nam 🇻🇳")

	f.Fuzz(func(t *testing.T, in string) {
		encoded := Encode(in)
		decoded, err := Decode(encoded)
		if err != nil {
			t.Fatalf("decode(%q) lỗi: %v", encoded, err)
		}
		if decoded != in {
			t.Errorf("round-trip: got %q, want %q", decoded, in)
		}
	})
}
""",
                ),
                code(
                    "Chạy fuzz",
                    """
go test -run=Fuzz -fuzz=FuzzEncodeDecode -fuzztime=60s ./internal/codec
go test ./internal/codec   # chạy lại corpus đã lưu như test thường
""",
                    language="bash",
                ),
            ],
            takeaways=[
                "Fuzz là coverage-guided, tự tìm đường code chưa chạm tới.",
                "Kiểm tra thuộc tính bất biến, không kiểm tra giá trị cụ thể.",
                "Input gây lỗi được lưu thành test hồi quy tự động.",
            ],
            exercises=["Viết fuzz test cho hàm parse cấu hình của bạn và chạy 60 giây."],
        ),
        lesson(
            slug="coverage-va-chien-luoc",
            title="Coverage và chiến lược kiểm thử",
            summary="Coverage là công cụ tìm chỗ chưa test, không phải mục tiêu để đạt KPI.",
            level="intermediate",
            tags=["kiem-thu", "chat-luong"],
            sections=[
                sec(
                    "Dùng coverage cho đúng việc",
                    "`go test -coverprofile` rồi `go tool cover -html` cho bản đồ màu: đỏ là "
                    "chưa chạy. Giá trị thật của nó là chỉ ra các nhánh lỗi bạn quên test, "
                    "chứ không phải con số phần trăm.",
                    "100% coverage không có nghĩa là không có bug: bạn có thể chạy qua mọi "
                    "dòng mà không kiểm tra kết quả nào. Ngược lại, 60% coverage tập trung "
                    "vào logic nghiệp vụ cốt lõi có thể đủ tốt.",
                ),
                sec(
                    "Kim tự tháp thực dụng",
                    "Nhiều test đơn vị nhanh cho logic thuần; một lớp test tích hợp vừa phải "
                    "cho store và handler (dùng DB thật trong Docker); rất ít test end-to-end "
                    "cho các luồng quan trọng nhất. Bộ test phải chạy dưới một phút, nếu "
                    "không sẽ không ai chạy nó.",
                    "Ưu tiên viết test cho: code có nhiều nhánh điều kiện, code xử lý tiền và "
                    "quyền truy cập, và mọi bug từng xảy ra ở production (test hồi quy).",
                    note="Bộ test tốt là bộ test bạn tin tưởng: khi nó xanh, bạn dám triển khai; khi nó đỏ, bạn biết có gì đó thật sự sai.",
                ),
            ],
            samples=[
                code(
                    "Xem coverage theo hàm và theo dòng",
                    """
go test -coverprofile=cover.out ./...
go tool cover -func=cover.out | tail -20
go tool cover -html=cover.out -o cover.html
""",
                    language="bash",
                    output="total:\t(statements)\t78.4%",
                ),
            ],
            takeaways=[
                "Coverage chỉ ra chỗ chưa test, không đo chất lượng test.",
                "Ưu tiên nhánh điều kiện, tiền, quyền và bug từng xảy ra.",
                "Bộ test phải nhanh, nếu không nó sẽ bị bỏ qua.",
            ],
            exercises=["Chạy coverage, tìm một nhánh lỗi chưa test và viết test cho nó."],
        ),
        lesson(
            slug="golden-file-va-testdata",
            title="Golden file và thư mục testdata",
            summary="Với output lớn, so sánh với file mẫu và cập nhật bằng cờ `-update`.",
            level="intermediate",
            tags=["kiem-thu", "mau-hinh"],
            sections=[
                sec(
                    "Khi nào dùng golden file",
                    "Khi kết quả là một khối lớn: HTML render, JSON response, code sinh ra, "
                    "báo cáo. Viết chuỗi mong đợi ngay trong test sẽ không đọc được và mỗi "
                    "thay đổi nhỏ lại phải sửa tay.",
                    "Thư mục `testdata` được toolchain Go bỏ qua khi build, nên đặt mọi "
                    "fixture ở đó là an toàn.",
                ),
                sec(
                    "Cờ -update",
                    'Định nghĩa `var update = flag.Bool("update", false, ...)`. Khi chạy '
                    "`go test -update`, test ghi lại file golden thay vì so sánh. Bạn xem "
                    "diff trong git để xác nhận thay đổi là đúng ý.",
                    "Rủi ro: cập nhật golden một cách vô thức sẽ che mất hồi quy. Vì thế diff "
                    "của file golden phải được đọc kỹ trong code review — nó chính là mô tả "
                    "thay đổi hành vi.",
                    note="Chuẩn hoá output trước khi so sánh: bỏ timestamp, id ngẫu nhiên, thứ tự map — nếu không test sẽ nhấp nháy.",
                ),
            ],
            samples=[
                code(
                    "Test golden file",
                    """
var update = flag.Bool("update", false, "ghi lại file golden")

func TestRenderInvoice(t *testing.T) {
	got := RenderInvoice(sampleInvoice())

	golden := filepath.Join("testdata", "invoice.golden.html")
	if *update {
		if err := os.WriteFile(golden, []byte(got), 0o644); err != nil {
			t.Fatal(err)
		}
		return
	}

	want, err := os.ReadFile(golden)
	if err != nil {
		t.Fatalf("thiếu file golden, chạy lại với -update: %v", err)
	}
	if diff := cmp.Diff(string(want), got); diff != "" {
		t.Errorf("output khác file golden (-want +got):\\n%s", diff)
	}
}
""",
                ),
            ],
            takeaways=[
                "Golden file cho output lớn; testdata được toolchain bỏ qua.",
                "Cờ `-update` để cập nhật, rồi đọc diff trong git.",
                "Chuẩn hoá phần không xác định để test không nhấp nháy.",
            ],
            exercises=["Thêm golden test cho một trang HTML và thử đổi template để xem diff."],
        ),
    ],
)
