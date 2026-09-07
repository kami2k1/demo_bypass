"""Chương 3 — Kiểu dữ liệu tổng hợp."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="du-lieu",
    title="Kiểu dữ liệu tổng hợp",
    summary=(
        "Array, slice, map, string, struct, con trỏ, embedding và generics — "
        "cách Go biểu diễn dữ liệu và vì sao hiểu bộ nhớ nền lại quan trọng."
    ),
    lessons=[
        lesson(
            slug="slice-va-mang",
            title="Array và slice: khác nhau ở đâu",
            summary="Array có độ dài thuộc kiểu; slice là khung nhìn ba trường trỏ vào một mảng nền.",
            level="beginner",
            tags=["kieu-du-lieu", "bo-nho"],
            sections=[
                sec(
                    "Array: độ dài là phần của kiểu",
                    "`[3]int` và `[4]int` là hai kiểu khác nhau. Array được truyền theo "
                    "giá trị, nghĩa là copy toàn bộ phần tử. Vì cứng nhắc như vậy, array "
                    "ít dùng trực tiếp, thường chỉ xuất hiện khi cần kích thước cố định "
                    "như một buffer hoặc hash 32 byte.",
                    "Trong thực tế, gần như mọi API Go nhận và trả slice.",
                ),
                sec(
                    "Slice: con trỏ + len + cap",
                    "Một slice là struct ba trường: con trỏ tới phần tử đầu của mảng nền, "
                    "độ dài hiện tại và capacity. Copy slice chỉ copy ba trường đó, nên "
                    "hai slice có thể cùng nhìn vào một mảng nền và thấy thay đổi của nhau.",
                    "`s[1:3]` tạo khung nhìn mới không cấp phát bộ nhớ. Đây là lý do cắt "
                    "slice cực rẻ, nhưng cũng là nguồn của lỗi chia sẻ dữ liệu ngoài ý muốn.",
                    note=(
                        "Một slice nhỏ cắt ra từ mảng lớn vẫn giữ toàn bộ mảng nền sống "
                        "trong bộ nhớ. Nếu chỉ cần vài phần tử từ file 100 MB, hãy copy "
                        "sang slice mới."
                    ),
                ),
            ],
            samples=[
                code(
                    "Chia sẻ mảng nền",
                    """
base := []int{1, 2, 3, 4, 5}
view := base[1:3] // len=2 cap=4

view[0] = 99
fmt.Println(base, view, len(view), cap(view))

isolated := make([]int, len(view))
copy(isolated, view)
isolated[0] = -1
fmt.Println(base, isolated)
""",
                    output="[1 99 3 4 5] [99 3] 2 4\n[1 99 3 4 5] [-1 3]",
                ),
            ],
            takeaways=[
                "Độ dài là phần của kiểu array, nên array kém linh hoạt.",
                "Slice là ba trường: con trỏ, len, cap.",
                "Cắt slice không copy dữ liệu; dùng `copy` khi cần tách biệt.",
            ],
            exercises=["Viết hàm nhận slice lớn và trả về 3 phần tử đầu mà không giữ mảng nền."],
        ),
        lesson(
            slug="append-va-capacity",
            title="append và chiến lược tăng trưởng",
            summary="Hiểu append giúp tránh cả hai lỗi kinh điển: cấp phát lại thừa và ghi đè dữ liệu chung.",
            level="intermediate",
            tags=["kieu-du-lieu", "hieu-nang", "bo-nho"],
            sections=[
                sec(
                    "Khi nào mảng nền được cấp phát lại",
                    "Nếu len < cap, append ghi vào ô trống có sẵn và trả về slice cùng "
                    "mảng nền. Nếu len == cap, runtime cấp phát mảng mới lớn hơn, copy dữ "
                    "liệu sang rồi trả về slice trỏ vào mảng mới. Vì thế **luôn phải gán "
                    "lại** kết quả của append.",
                    "Hệ số tăng trưởng xấp xỉ gấp đôi với slice nhỏ và giảm dần về khoảng "
                    "1,25 lần khi slice lớn, nhằm cân bằng giữa số lần copy và bộ nhớ thừa.",
                ),
                sec(
                    "Cấp phát trước khi biết kích thước",
                    "Nếu biết trước số phần tử, `make([]T, 0, n)` loại bỏ toàn bộ chuỗi "
                    "cấp phát lại. Với vòng lặp thêm hàng nghìn phần tử, đây thường là "
                    "tối ưu đơn giản nhất mang lại khác biệt đo được.",
                    "Cạm bẫy chia sẻ: append vào một slice cắt ra từ slice khác có thể ghi "
                    "đè phần tử của slice gốc nếu còn capacity dư. Dùng full slice "
                    "expression `s[a:b:b]` để chặn hành vi này.",
                ),
            ],
            samples=[
                code(
                    "Quan sát len và cap",
                    """
s := make([]int, 0)
for i := range 5 {
	s = append(s, i)
	fmt.Printf("len=%d cap=%d\\n", len(s), cap(s))
}
""",
                    output="len=1 cap=1\nlen=2 cap=2\nlen=3 cap=4\nlen=4 cap=4\nlen=5 cap=8",
                ),
                code(
                    "Chặn ghi đè bằng full slice expression",
                    """
base := []int{1, 2, 3, 4, 5}

risky := base[:2]        // cap=5, append sẽ ghi vào base[2]
risky = append(risky, 99)

safe := base[:2:2]       // cap=2, append buộc cấp phát mới
safe = append(safe, 77)
""",
                    explanation="`base[:2:2]` giới hạn capacity, nên append không thể chạm vào phần còn lại của mảng nền.",
                ),
            ],
            takeaways=[
                "Luôn gán lại kết quả của append.",
                "`make([]T, 0, n)` khi biết trước kích thước.",
                "`s[a:b:b]` chặn append ghi đè dữ liệu dùng chung.",
            ],
            exercises=["Benchmark hai vòng lặp append 100k phần tử: có và không cấp phát trước."],
        ),
        lesson(
            slug="map-va-cach-dung",
            title="Map: bảng băm của Go",
            summary="Cú pháp gọn, hiệu năng tốt, nhưng không an toàn cho truy cập đồng thời.",
            level="beginner",
            tags=["kieu-du-lieu", "bo-nho"],
            sections=[
                sec(
                    "Cú pháp và mẫu comma ok",
                    "`make(map[string]int)` hoặc literal `map[string]int{...}`. Đọc key "
                    "không tồn tại trả về zero value, nên cần dạng hai giá trị "
                    "`v, ok := m[k]` để phân biệt “không có” với “có nhưng bằng 0”.",
                    "Key phải là kiểu so sánh được: số, string, bool, con trỏ, struct chỉ "
                    "chứa các kiểu so sánh được. Slice và map không thể làm key.",
                ),
                sec(
                    "Những điều dễ vấp",
                    "Thứ tự lặp là ngẫu nhiên. Không lấy được địa chỉ của phần tử map, "
                    "nên với map[string]Struct bạn phải đọc ra, sửa, rồi ghi lại — hoặc "
                    "dùng map[string]*Struct.",
                    "Map không an toàn khi nhiều goroutine ghi song song; runtime chủ động "
                    "phát hiện và panic. Hãy bảo vệ bằng mutex hoặc dùng sync.Map cho các "
                    "mẫu đọc nhiều ghi ít.",
                    note="Xoá phần tử không làm map co lại; nếu map từng rất lớn, hãy tạo map mới để giải phóng bộ nhớ.",
                ),
            ],
            samples=[
                code(
                    "Comma ok và sửa struct trong map",
                    """
counts := map[string]int{"go": 1}

if v, ok := counts["rust"]; !ok {
	fmt.Println("chưa có key rust, zero value =", v)
}

type stat struct{ Hits int }
byPath := map[string]*stat{"/": {}}
byPath["/"].Hits++ // dùng con trỏ để sửa tại chỗ

delete(counts, "go")
fmt.Println(len(counts), byPath["/"].Hits)
""",
                    output="chưa có key rust, zero value = 0\n0 1",
                ),
            ],
            takeaways=[
                "Dùng `v, ok := m[k]` để phân biệt thiếu key và giá trị zero.",
                "Không lấy địa chỉ phần tử map; dùng con trỏ nếu cần sửa tại chỗ.",
                "Ghi map đồng thời gây panic — phải tự đồng bộ hoá.",
            ],
            exercises=["Viết bộ đếm tần suất từ cho một đoạn văn rồi in top 5 theo số lần."],
        ),
        lesson(
            slug="string-rune-va-utf8",
            title="String, byte và rune",
            summary="String Go là chuỗi byte bất biến mã hoá UTF-8 — hiểu đúng điều này tránh được lỗi cắt chữ.",
            level="intermediate",
            tags=["kieu-du-lieu", "unicode"],
            sections=[
                sec(
                    "Byte hay ký tự?",
                    "`len(s)` trả về số **byte**, không phải số ký tự. Với chuỗi ASCII hai "
                    'con số này trùng nhau, nhưng "Việt" dài 5 byte trong khi chỉ có 4 '
                    "ký tự. Đếm ký tự thì dùng `utf8.RuneCountInString`.",
                    "Index `s[i]` trả về một byte (uint8). Muốn ký tự thì `range` qua "
                    "chuỗi hoặc chuyển sang `[]rune`.",
                ),
                sec(
                    "Bất biến và hệ quả hiệu năng",
                    "Không thể sửa string tại chỗ. Nối chuỗi trong vòng lặp bằng `+=` sẽ "
                    "cấp phát lại mỗi lần; dùng `strings.Builder` để gom vào một buffer.",
                    "Chuyển `[]byte(s)` và `string(b)` đều copy dữ liệu. Trong đường dẫn "
                    "nóng, hãy chọn một biểu diễn và giữ nguyên nó thay vì đổi qua đổi lại.",
                    note="Cắt chuỗi theo byte có thể chẻ đôi một ký tự nhiều byte và sinh ra ký tự lỗi khi hiển thị.",
                ),
            ],
            samples=[
                code(
                    "Đếm và cắt đúng cách",
                    """
s := "Việt"
fmt.Println(len(s), utf8.RuneCountInString(s))

fmt.Printf("%c\\n", []rune(s)[1]) // ký tự thứ hai

var b strings.Builder
for range 3 {
	b.WriteString("go ")
}
fmt.Println(b.String())
""",
                    output="5 4\nệ\ngo go go",
                ),
            ],
            takeaways=[
                "`len(string)` là số byte; dùng RuneCountInString để đếm ký tự.",
                "String bất biến: nối trong vòng lặp phải dùng strings.Builder.",
                "Chuyển đổi string ↔ []byte có copy, tránh lặp lại trong hot path.",
            ],
            exercises=[
                "Viết hàm `truncate(s string, n int) string` cắt theo rune, không làm hỏng ký tự."
            ],
        ),
        lesson(
            slug="struct-va-tag",
            title="Struct, so sánh và struct tag",
            summary="Struct là bố cục bộ nhớ tường minh, còn tag là metadata cho các thư viện phản chiếu.",
            level="beginner",
            tags=["kieu-du-lieu", "kien-truc"],
            sections=[
                sec(
                    "Bố cục và khởi tạo",
                    "Struct nhóm các trường liền nhau trong bộ nhớ, không có header ẩn. "
                    "Nên khởi tạo bằng tên trường (`User{ID: 1}`) thay vì theo vị trí, để "
                    "thêm trường mới không phá vỡ code cũ.",
                    "Struct có thể so sánh bằng `==` nếu mọi trường đều so sánh được, và "
                    "khi đó dùng được làm key của map — rất tiện cho các key phức hợp.",
                ),
                sec(
                    "Struct tag",
                    "Tag là chuỗi literal đặt sau kiểu trường, được các package như "
                    "encoding/json, database/sql hay validator đọc qua reflection. Đây là "
                    "cách Go tách biểu diễn ngoài (JSON, DB) khỏi tên trường trong code.",
                    "Tag chỉ là chuỗi, compiler không kiểm tra nội dung. `go vet` bắt được "
                    "một số lỗi cú pháp tag, nhưng gõ sai tên tag thì bạn chỉ phát hiện "
                    "qua test.",
                ),
            ],
            samples=[
                code(
                    "Struct dùng làm key và struct tag",
                    """
type route struct {
	Method string
	Path   string
}

hits := map[route]int{}
hits[route{"GET", "/health"}]++

type User struct {
	ID        int64     `json:"id" db:"id"`
	Email     string    `json:"email" db:"email"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	password  string    `json:"-"`
}
""",
                    explanation="Trường `password` viết thường nên không được export và cũng không xuất hiện trong JSON.",
                ),
            ],
            takeaways=[
                "Khởi tạo struct theo tên trường để an toàn khi mở rộng.",
                "Struct so sánh được có thể làm key của map.",
                "Struct tag là metadata cho reflection, không được compiler kiểm tra.",
            ],
            exercises=[
                "Định nghĩa struct `Order` với tag JSON snake_case và kiểm tra bằng json.Marshal."
            ],
        ),
        lesson(
            slug="con-tro",
            title="Con trỏ mà không có số học con trỏ",
            summary="Go có con trỏ để chia sẻ và sửa đổi, nhưng không cho phép cộng trừ địa chỉ.",
            level="beginner",
            tags=["bo-nho", "co-ban"],
            sections=[
                sec(
                    "Lấy địa chỉ và giải tham chiếu",
                    "`&x` cho con trỏ tới x, `*p` đọc hoặc ghi giá trị được trỏ. Không có "
                    "phép cộng con trỏ, nên không thể vượt biên mảng bằng số học địa chỉ. "
                    "Đây là một trong những lý do Go an toàn bộ nhớ hơn C.",
                    "Con trỏ nil được giải tham chiếu sẽ panic ngay tại chỗ, kèm stack "
                    "trace — dễ chẩn đoán hơn hành vi không xác định.",
                ),
                sec(
                    "Khi nào dùng con trỏ",
                    "Ba lý do chính đáng: cần sửa giá trị của người gọi, struct lớn muốn "
                    "tránh copy, hoặc cần biểu diễn “không có giá trị” bằng nil. Ngoài ba "
                    "trường hợp đó, truyền theo giá trị thường đơn giản và an toàn hơn.",
                    "Escape analysis quyết định biến nằm trên stack hay heap. Trả về `&x` "
                    "từ hàm là hợp lệ; runtime sẽ tự đưa x lên heap, không có lỗi dangling "
                    "pointer như C.",
                    note="Con trỏ tới struct nhỏ (vài trường) đôi khi chậm hơn copy vì thêm một lần truy cập bộ nhớ và gây áp lực cho GC.",
                ),
            ],
            samples=[
                code(
                    "Sửa giá trị của người gọi",
                    """
type Counter struct{ n int }

func (c *Counter) Inc() { c.n++ }        // receiver con trỏ: sửa được
func (c Counter) Value() int { return c.n } // receiver giá trị: chỉ đọc

func newCounter() *Counter {
	c := Counter{} // escape analysis đưa lên heap vì địa chỉ được trả về
	return &c
}

c := newCounter()
c.Inc()
fmt.Println(c.Value())
""",
                    output="1",
                ),
            ],
            takeaways=[
                "Không có số học con trỏ nên không thể vượt biên bằng địa chỉ.",
                "Dùng con trỏ khi cần sửa, khi struct lớn, hoặc khi cần nil.",
                "Trả về địa chỉ biến cục bộ là an toàn nhờ escape analysis.",
            ],
            exercises=["So sánh benchmark truyền struct 8 trường theo giá trị và theo con trỏ."],
        ),
        lesson(
            slug="embedding-va-composition",
            title="Embedding: kết hợp thay vì kế thừa",
            summary="Go không có kế thừa lớp; embedding thăng cấp phương thức mà vẫn giữ quan hệ “có một”.",
            level="intermediate",
            tags=["kien-truc", "kieu-du-lieu"],
            sections=[
                sec(
                    "Trường ẩn danh",
                    "Nhúng một kiểu vào struct bằng cách khai báo nó không tên. Các "
                    "phương thức và trường của kiểu nhúng được thăng cấp lên struct ngoài, "
                    "gọi trực tiếp được — nhưng đó là uỷ quyền, không phải kế thừa.",
                    "Không có tính đa hình theo lớp: kiểu ngoài không thể được dùng ở nơi "
                    "yêu cầu kiểu nhúng, trừ khi thoả mãn cùng interface.",
                ),
                sec(
                    "Ứng dụng thực tế",
                    "Nhúng `sync.Mutex` để struct tự có Lock/Unlock. Nhúng một interface "
                    "để tạo decorator chỉ ghi đè vài phương thức. Nhúng struct cơ sở để "
                    "chia sẻ các trường chung như ID và timestamp.",
                    "Khi hai kiểu nhúng có phương thức cùng tên, lời gọi trở nên nhập "
                    "nhằng và compiler báo lỗi; bạn phải chỉ rõ đường dẫn.",
                    note="Nhúng mutex là tiện, nhưng nó cũng xuất Lock/Unlock ra API công khai — thường nên đặt mutex làm trường có tên.",
                ),
            ],
            samples=[
                code(
                    "Embedding struct và interface",
                    """
type Base struct {
	ID        string
	CreatedAt time.Time
}

func (b Base) Age() time.Duration { return time.Since(b.CreatedAt) }

type Invoice struct {
	Base                // phương thức Age được thăng cấp
	AmountCents int64
}

type loggingStore struct {
	Store               // interface nhúng: chỉ ghi đè Save
	log *slog.Logger
}

func (l loggingStore) Save(ctx context.Context, inv Invoice) error {
	l.log.Info("saving", "id", inv.ID)
	return l.Store.Save(ctx, inv)
}
""",
                    explanation="`loggingStore` chỉ cần định nghĩa Save; các phương thức còn lại của Store tự động có sẵn.",
                ),
            ],
            takeaways=[
                "Embedding thăng cấp phương thức nhưng không tạo quan hệ kế thừa.",
                "Nhúng interface là cách viết decorator gọn nhất.",
                "Trùng tên phương thức giữa hai kiểu nhúng gây lỗi nhập nhằng.",
            ],
            exercises=[
                "Viết decorator đo thời gian cho một interface có 4 phương thức, chỉ hiện thực 1."
            ],
        ),
        lesson(
            slug="generics-co-ban",
            title="Generics: tham số kiểu và ràng buộc",
            summary="Từ Go 1.18, hàm và kiểu có thể nhận tham số kiểu với ràng buộc biểu diễn bằng interface.",
            level="intermediate",
            tags=["generics", "kieu-du-lieu"],
            sections=[
                sec(
                    "Cú pháp và ràng buộc",
                    "`func Map[T, U any](in []T, f func(T) U) []U` khai báo hai tham số "
                    "kiểu. Ràng buộc là interface: `any` cho phép mọi kiểu, "
                    "`comparable` cho kiểu so sánh được, còn interface chứa tập kiểu "
                    "(`int | float64`) giới hạn theo danh sách.",
                    "Package `constraints` trong x/exp cung cấp các ràng buộc quen dùng "
                    "như Ordered; nhiều trường hợp nay đã được `cmp.Ordered` trong thư "
                    "viện chuẩn thay thế.",
                ),
                sec(
                    "Khi nào nên dùng",
                    "Generics đáng dùng cho cấu trúc dữ liệu và hàm tiện ích thao tác "
                    "trên bộ sưu tập: Map, Filter, Keys, Set, LRU cache. Ngược lại, khi "
                    "hành vi khác nhau theo kiểu, interface vẫn là lựa chọn đúng.",
                    "Đừng generic hoá sớm. Một hàm cụ thể đọc dễ hơn một hàm generic với "
                    "ba tham số kiểu và ràng buộc rối rắm.",
                ),
            ],
            samples=[
                code(
                    "Map, Filter và Set generic",
                    """
func Map[T, U any](in []T, f func(T) U) []U {
	out := make([]U, 0, len(in))
	for _, v := range in {
		out = append(out, f(v))
	}
	return out
}

type Set[T comparable] struct {
	items map[T]struct{}
}

func NewSet[T comparable](values ...T) *Set[T] {
	s := &Set[T]{items: make(map[T]struct{}, len(values))}
	for _, v := range values {
		s.items[v] = struct{}{}
	}
	return s
}

func (s *Set[T]) Has(v T) bool {
	_, ok := s.items[v]
	return ok
}
""",
                    output='Map([]int{1,2}, strconv.Itoa) // []string{"1","2"}',
                ),
            ],
            takeaways=[
                "Ràng buộc kiểu được viết như interface, có thể liệt kê tập kiểu.",
                "`comparable` cần thiết khi tham số kiểu làm key của map.",
                "Generics cho cấu trúc dữ liệu; interface cho hành vi đa dạng.",
            ],
            exercises=["Viết `GroupBy[T any, K comparable](items []T, key func(T) K) map[K][]T`."],
        ),
        lesson(
            slug="sap-xep-va-slices-package",
            title="Sắp xếp và package slices/maps",
            summary="Từ Go 1.21, các tiện ích generic cho slice và map đã vào thư viện chuẩn.",
            level="beginner",
            tags=["thu-vien-chuan", "generics"],
            sections=[
                sec(
                    "slices và maps",
                    "`slices.Sort`, `slices.SortFunc`, `slices.Contains`, "
                    "`slices.BinarySearch`, `slices.Clone`, `maps.Keys`, `maps.Values` "
                    "thay thế phần lớn code lặp tay trước đây. Chúng generic nên không "
                    "cần chuyển đổi qua interface{}.",
                    "`sort.Slice` cũ vẫn dùng được, nhưng `slices.SortFunc` với hàm so "
                    "sánh trả về số âm/0/dương thì rõ nghĩa hơn và nhanh hơn nhờ không "
                    "dùng reflection.",
                ),
                sec(
                    "Sắp xếp ổn định và nhiều tiêu chí",
                    "`slices.SortStableFunc` giữ nguyên thứ tự tương đối của các phần tử "
                    "bằng nhau — quan trọng khi sắp xếp nhiều lần theo từng tiêu chí. "
                    "Với nhiều tiêu chí trong một lần, hãy so sánh lần lượt và trả về "
                    "ngay khi khác nhau, dùng `cmp.Compare` cho gọn.",
                    "Nhớ rằng lặp map không có thứ tự: muốn output ổn định, hãy lấy key ra "
                    "slice rồi sắp xếp.",
                ),
            ],
            samples=[
                code(
                    "Sắp xếp nhiều tiêu chí",
                    """
type User struct {
	Name string
	Age  int
}

users := []User{{"An", 30}, {"Bảo", 25}, {"An", 25}}

slices.SortFunc(users, func(a, b User) int {
	if c := cmp.Compare(a.Name, b.Name); c != 0 {
		return c
	}
	return cmp.Compare(a.Age, b.Age)
})

keys := slices.Sorted(maps.Keys(map[string]int{"b": 2, "a": 1}))
fmt.Println(users, keys)
""",
                    output="[{An 25} {An 30} {Bảo 25}] [a b]",
                ),
            ],
            takeaways=[
                "Ưu tiên `slices`/`maps` generic thay vì tự viết vòng lặp.",
                "`SortFunc` trả về âm/0/dương; `cmp.Compare` giúp viết gọn.",
                "Sắp xếp key khi cần output ổn định từ map.",
            ],
            exercises=["Sắp xếp danh sách đơn hàng theo trạng thái rồi theo ngày giảm dần."],
        ),
    ],
)
