"""Chương 4 — Phương thức và interface."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="phuong-thuc-interface",
    title="Phương thức và interface",
    summary=(
        "Cách Go làm đa hình mà không cần cây kế thừa: phương thức gắn vào kiểu "
        "và interface được thoả mãn một cách ngầm định."
    ),
    lessons=[
        lesson(
            slug="phuong-thuc-va-receiver",
            title="Phương thức và lựa chọn receiver",
            summary="Receiver giá trị hay con trỏ là quyết định ảnh hưởng tới cả tính đúng đắn và hiệu năng.",
            level="beginner",
            tags=["interface", "co-ban"],
            sections=[
                sec(
                    "Phương thức gắn vào kiểu, không vào class",
                    "Phương thức là hàm có receiver đặt trước tên: "
                    "`func (u User) FullName() string`. Có thể định nghĩa phương thức cho "
                    "bất kỳ kiểu do bạn khai báo, kể cả `type Celsius float64`, không chỉ "
                    "struct.",
                    "Không thể thêm phương thức cho kiểu của package khác — muốn vậy phải "
                    "định nghĩa kiểu mới bọc nó lại.",
                ),
                sec(
                    "Giá trị hay con trỏ",
                    "Receiver con trỏ khi phương thức cần sửa trạng thái, khi struct lớn, "
                    "hoặc khi kiểu chứa mutex. Receiver giá trị cho kiểu nhỏ và bất biến. "
                    "Nguyên tắc thực dụng: giữ nhất quán trong cùng một kiểu, đừng trộn.",
                    "Tập phương thức ảnh hưởng tới việc thoả mãn interface: nếu phương "
                    "thức có receiver con trỏ thì chỉ `*T` thoả interface, còn `T` thì "
                    "không. Đây là nguồn lỗi phổ biến với người mới.",
                    note="Go tự thêm & và * khi gọi phương thức trên biến có địa chỉ, nên `c.Inc()` hoạt động dù Inc có receiver con trỏ.",
                ),
            ],
            samples=[
                code(
                    "Tập phương thức và interface",
                    """
type Counter struct{ n int }

func (c *Counter) Inc()      { c.n++ }
func (c Counter) Value() int { return c.n }

type Incrementer interface{ Inc() }

var _ Incrementer = &Counter{} // hợp lệ
// var _ Incrementer = Counter{} // lỗi: Inc có receiver con trỏ
""",
                ),
                code(
                    "Phương thức trên kiểu không phải struct",
                    """
type Celsius float64

func (c Celsius) Fahrenheit() float64 { return float64(c)*9/5 + 32 }

fmt.Printf("%.1f\\n", Celsius(37).Fahrenheit())
""",
                    output="98.6",
                ),
            ],
            takeaways=[
                "Phương thức định nghĩa được cho mọi kiểu bạn khai báo.",
                "Receiver con trỏ khi cần sửa hoặc struct lớn; giữ nhất quán.",
                "Phương thức receiver con trỏ khiến chỉ `*T` thoả interface.",
            ],
            exercises=["Tạo `type Money int64` với các phương thức Add, String và test chúng."],
        ),
        lesson(
            slug="interface-co-ban",
            title="Interface và sự thoả mãn ngầm định",
            summary="Kiểu thoả interface chỉ bằng cách có đủ phương thức — không cần khai báo implements.",
            level="beginner",
            tags=["interface", "kien-truc"],
            sections=[
                sec(
                    "Không cần declare implements",
                    "Interface liệt kê tập phương thức. Bất kỳ kiểu nào có đủ các phương "
                    "thức đó đều thoả mãn interface, kể cả kiểu được viết trước khi "
                    "interface tồn tại. Nhờ vậy bạn có thể định nghĩa interface ở phía "
                    "người dùng, đúng nơi cần đến sự trừu tượng.",
                    "Cấu trúc bên trong một interface value gồm hai từ: con trỏ tới bảng "
                    "phương thức (itab) và con trỏ tới dữ liệu. Lời gọi phương thức là một "
                    "lần tra bảng rồi nhảy.",
                ),
                sec(
                    "Ai nên định nghĩa interface",
                    "Quy tắc Go: package tiêu thụ định nghĩa interface, package cung cấp "
                    "chỉ trả về struct cụ thể. Điều đó ngược với thói quen ở Java nhưng "
                    "giúp phụ thuộc chỉ đi một chiều và test dễ hơn nhiều.",
                    "Dùng `var _ Iface = (*Impl)(nil)` như một khẳng định lúc biên dịch "
                    "rằng Impl vẫn thoả interface — rẻ và rất hữu ích khi refactor.",
                    note="Interface trong Go nên nhỏ. `io.Reader` chỉ có một phương thức và là một trong những trừu tượng hữu ích nhất từng được thiết kế.",
                ),
            ],
            samples=[
                code(
                    "Định nghĩa ở phía tiêu thụ",
                    """
package report

// Interface được định nghĩa tại nơi dùng, chỉ gồm phương thức cần thiết.
type InvoiceReader interface {
	ByCustomer(ctx context.Context, id string) ([]Invoice, error)
}

type Service struct{ invoices InvoiceReader }

func (s Service) Monthly(ctx context.Context, id string) (Summary, error) {
	items, err := s.invoices.ByCustomer(ctx, id)
	if err != nil {
		return Summary{}, err
	}
	return summarise(items), nil
}
""",
                    explanation="Package store trả về *store.Postgres cụ thể; report tự khai báo phần nó cần.",
                ),
            ],
            takeaways=[
                "Thoả mãn interface là ngầm định, dựa trên tập phương thức.",
                "Package tiêu thụ nên định nghĩa interface, không phải package cung cấp.",
                "Interface value = con trỏ itab + con trỏ dữ liệu.",
            ],
            exercises=[
                "Tách một hàm phụ thuộc trực tiếp vào DB thành hàm nhận interface một phương thức."
            ],
        ),
        lesson(
            slug="interface-nho-va-chap-nhan",
            title="Interface nhỏ và nguyên tắc nhận vào",
            summary="“Nhận interface, trả struct” — câu châm ngôn gói gọn cách thiết kế API Go tốt.",
            level="intermediate",
            tags=["interface", "kien-truc"],
            sections=[
                sec(
                    "Vì sao interface nhỏ thắng",
                    "Interface một phương thức dễ hiện thực, dễ mô phỏng trong test và dễ "
                    "kết hợp. `io.Reader` cho phép cùng một hàm đọc từ file, socket, "
                    "buffer trong bộ nhớ hay dữ liệu nén, mà không hàm nào biết về nhau.",
                    "Interface lớn (10 phương thức) buộc mọi hiện thực phải viết đủ, kể cả "
                    "phương thức không dùng, và biến test double thành hàng trăm dòng vô nghĩa.",
                ),
                sec(
                    "Nhận interface, trả struct",
                    "Hàm nên nhận tham số ở dạng interface hẹp nhất đủ dùng, nhưng trả về "
                    "kiểu cụ thể để người gọi thấy hết khả năng. Trả về interface làm mất "
                    "thông tin và khiến việc thêm phương thức mới thành thay đổi phá vỡ.",
                    "Ngoại lệ hợp lý: khi thật sự cần trả về một trong nhiều hiện thực, ví "
                    "dụ hàm factory chọn backend theo cấu hình.",
                ),
            ],
            samples=[
                code(
                    "Cùng một hàm, nhiều nguồn dữ liệu",
                    """
func countLines(r io.Reader) (int, error) {
	scanner := bufio.NewScanner(r)
	n := 0
	for scanner.Scan() {
		n++
	}
	return n, scanner.Err()
}

// Dùng với string trong test:
n, _ := countLines(strings.NewReader("a\\nb\\n"))

// Dùng với file ở production:
f, _ := os.Open("access.log")
defer f.Close()
m, _ := countLines(f)
""",
                    output="2",
                ),
            ],
            takeaways=[
                "Interface càng nhỏ càng dễ kết hợp và dễ test.",
                "Nhận interface hẹp, trả về struct cụ thể.",
                "io.Reader/io.Writer là ví dụ mẫu mực về trừu tượng tối giản.",
            ],
            exercises=["Viết hàm xử lý CSV nhận `io.Reader` và test nó với `strings.NewReader`."],
        ),
        lesson(
            slug="type-assertion-va-type-switch",
            title="Type assertion và type switch",
            summary="Cách lấy lại kiểu cụ thể từ interface một cách an toàn.",
            level="intermediate",
            tags=["interface", "cu-phap"],
            sections=[
                sec(
                    "Dạng an toàn và dạng panic",
                    "`v, ok := x.(*Bytes)` không panic khi kiểu không khớp; dạng một giá "
                    "trị `v := x.(*Bytes)` sẽ panic. Trong code production hãy dùng dạng "
                    "hai giá trị, trừ khi bạn thật sự muốn dừng ngay vì bất biến bị vi phạm.",
                    "Assertion cũng hoạt động với interface đích: kiểm tra xem một giá trị "
                    "có thoả interface khác không, ví dụ `if f, ok := w.(io.Flusher)`.",
                ),
                sec(
                    "Type switch",
                    "`switch v := x.(type)` phân nhánh theo kiểu động, mỗi case cho biến v "
                    "đúng kiểu tương ứng. Dùng khi xử lý một tập kiểu đóng, ví dụ các "
                    "biến thể của một AST hoặc các loại error nội bộ.",
                    "Nếu bạn thấy type switch dài trên nhiều kiểu do mình sở hữu, thường "
                    "đó là dấu hiệu nên thêm một phương thức vào interface thay vì phân "
                    "nhánh bên ngoài.",
                    note="Kiểm tra khả năng mở rộng bằng interface phụ (như io.Flusher) là mẫu rất Go: thử assertion, nếu không có thì đi đường mặc định.",
                ),
            ],
            samples=[
                code(
                    "Phát hiện khả năng bổ sung",
                    """
func writeAndFlush(w io.Writer, data []byte) error {
	if _, err := w.Write(data); err != nil {
		return err
	}
	if f, ok := w.(interface{ Flush() error }); ok {
		return f.Flush()
	}
	return nil
}
""",
                ),
                code(
                    "Type switch",
                    """
func describe(v any) string {
	switch t := v.(type) {
	case nil:
		return "nil"
	case int, int64:
		return fmt.Sprintf("số nguyên %v", t)
	case string:
		return "chuỗi dài " + strconv.Itoa(len(t))
	case error:
		return "lỗi: " + t.Error()
	default:
		return fmt.Sprintf("kiểu khác: %T", t)
	}
}
""",
                    output="describe(42) // số nguyên 42",
                ),
            ],
            takeaways=[
                "Dùng dạng `v, ok :=` để assertion không panic.",
                "Assertion sang interface khác là cách phát hiện khả năng tuỳ chọn.",
                "Type switch dài trên kiểu của mình → nên thêm phương thức.",
            ],
            exercises=[
                "Viết hàm `size(v any) int` xử lý string, []byte, slice bất kỳ qua type switch."
            ],
        ),
        lesson(
            slug="any-va-reflection",
            title="any và reflection: khi nào chấp nhận được",
            summary="Reflection mạnh nhưng đắt và mất an toàn kiểu; chỉ dùng ở biên hệ thống.",
            level="advanced",
            tags=["interface", "reflection"],
            sections=[
                sec(
                    "any chỉ là interface rỗng",
                    "`any` là bí danh của `interface{}`: mọi giá trị đều thoả mãn. Nó hữu "
                    "ích ở biên như logging hay JSON, nhưng bên trong lõi nghiệp vụ thì "
                    "làm mất mọi bảo đảm mà compiler có thể cho bạn.",
                    "Kể từ khi có generics, phần lớn trường hợp trước đây phải dùng any "
                    "nay viết được với tham số kiểu, giữ nguyên an toàn kiểu.",
                ),
                sec(
                    "Chi phí của reflection",
                    "`reflect` cho phép đọc kiểu và trường lúc chạy, là nền tảng của "
                    "encoding/json và các ORM. Cái giá là chậm hơn nhiều lần code tĩnh, "
                    "cấp phát thêm, và lỗi chỉ xuất hiện lúc chạy.",
                    "Nguyên tắc: dùng reflection cho code hạ tầng tổng quát chạy một lần "
                    "mỗi request, không dùng trong vòng lặp nóng. Nếu hiệu năng quan "
                    "trọng, hãy sinh code (`go generate`) thay vì phản chiếu.",
                ),
            ],
            samples=[
                code(
                    "Đọc struct tag bằng reflection",
                    """
func columns(v any) []string {
	t := reflect.TypeOf(v)
	if t.Kind() == reflect.Pointer {
		t = t.Elem()
	}
	cols := make([]string, 0, t.NumField())
	for i := range t.NumField() {
		if tag := t.Field(i).Tag.Get("db"); tag != "" && tag != "-" {
			cols = append(cols, tag)
		}
	}
	return cols
}
""",
                    output="columns(User{}) // [id email created_at]",
                    explanation="Đây là hạt nhân của mọi mapper DB: đọc tag một lần rồi cache lại theo kiểu.",
                ),
            ],
            takeaways=[
                "`any` = `interface{}`; dùng ở biên, không dùng trong lõi.",
                "Generics đã thay thế phần lớn nhu cầu dùng any.",
                "Reflection đắt và không an toàn kiểu — cache kết quả hoặc sinh code.",
            ],
            exercises=[
                "Cache kết quả `columns` theo `reflect.Type` bằng `sync.Map` và benchmark hai phiên bản."
            ],
        ),
        lesson(
            slug="io-reader-writer",
            title="io.Reader, io.Writer và nghệ thuật kết hợp",
            summary="Hai interface một phương thức là nền tảng cho toàn bộ hệ sinh thái I/O của Go.",
            level="intermediate",
            tags=["interface", "thu-vien-chuan"],
            sections=[
                sec(
                    "Hai chữ ký nhỏ bé",
                    "`Read(p []byte) (n int, err error)` và "
                    "`Write(p []byte) (n int, err error)`. Mọi thứ trong Go đọc/ghi dữ "
                    "liệu đều nói cùng ngôn ngữ này: file, socket, gzip, hash, HTTP body, "
                    "bộ đệm trong bộ nhớ.",
                    "Vì thế `io.Copy(dst, src)` chuyển dữ liệu giữa bất kỳ hai thứ nào, và "
                    "nó tự dùng đường tối ưu nếu nguồn/đích có ReadFrom hoặc WriteTo.",
                ),
                sec(
                    "Kết hợp thành đường ống",
                    "`io.TeeReader` nhân đôi luồng đọc để vừa xử lý vừa băm. "
                    "`io.MultiWriter` ghi ra nhiều đích cùng lúc. `io.LimitReader` chặn "
                    "đọc quá nhiều byte — biện pháp bắt buộc khi đọc body từ client.",
                    "Tất cả đều hoạt động vì chúng chỉ là các hiện thực nhỏ của cùng hai "
                    "interface, ghép lại như ống nước.",
                    note="Luôn bọc body của request đến bằng io.LimitReader hoặc http.MaxBytesReader để tránh cạn bộ nhớ.",
                ),
            ],
            samples=[
                code(
                    "Vừa lưu file vừa tính checksum",
                    """
func saveWithChecksum(dst io.Writer, src io.Reader) (string, error) {
	h := sha256.New()
	tee := io.TeeReader(io.LimitReader(src, 32<<20), h)
	if _, err := io.Copy(dst, tee); err != nil {
		return "", err
	}
	return hex.EncodeToString(h.Sum(nil)), nil
}
""",
                    explanation="Chỉ một lần đi qua dữ liệu: ghi ra đích và cập nhật hash song song, giới hạn 32 MB.",
                ),
            ],
            takeaways=[
                "Reader/Writer là giao thức chung cho mọi I/O trong Go.",
                "io.Copy, TeeReader, MultiWriter, LimitReader ghép được như ống nước.",
                "Giới hạn kích thước đọc là yêu cầu an toàn, không phải tuỳ chọn.",
            ],
            exercises=["Viết hàm nén dữ liệu bằng gzip rồi ghi ra file, chỉ dùng io.Copy."],
        ),
        lesson(
            slug="stringer-va-fmt",
            title="Stringer, error và các interface của fmt",
            summary="Hiện thực String() hay Error() để giá trị của bạn tự in ra đẹp trong log.",
            level="beginner",
            tags=["interface", "thu-vien-chuan"],
            sections=[
                sec(
                    "fmt tìm gì",
                    "Khi in một giá trị, fmt kiểm tra lần lượt: có `Format` không, có "
                    "`Error() string` không, rồi có `String() string` không. Vì thế thêm "
                    "một phương thức là đủ để kiểu của bạn hiển thị đẹp ở mọi nơi.",
                    "Cẩn thận đệ quy vô hạn: nếu trong `String()` bạn dùng `%v` với chính "
                    "receiver, chương trình sẽ tràn stack. Hãy chuyển sang kiểu nền trước.",
                ),
                sec(
                    "Verb hay dùng",
                    "`%v` in mặc định, `%+v` thêm tên trường, `%#v` in cú pháp Go, `%T` in "
                    "kiểu, `%q` thêm dấu ngoặc kép. Khi debug struct, `%+v` là verb bạn sẽ "
                    "dùng nhiều nhất.",
                    "Với dữ liệu nhạy cảm, hiện thực `String()` để che bớt: token, mật "
                    "khẩu, số thẻ nên in ra dạng đã ẩn để không rơi vào log.",
                    note="Che dữ liệu nhạy cảm ngay trong String() là lớp phòng thủ tốt hơn nhiều so với hy vọng không ai log nó.",
                ),
            ],
            samples=[
                code(
                    "Stringer che dữ liệu nhạy cảm",
                    """
type Token string

func (t Token) String() string {
	if len(t) <= 4 {
		return "****"
	}
	return "****" + string(t[len(t)-4:])
}

fmt.Printf("%v\\n", Token("secret-abcd1234"))
""",
                    output="****1234",
                ),
                code(
                    "Tránh đệ quy trong String()",
                    """
type ID int

func (i ID) String() string { return fmt.Sprintf("ID-%d", int(i)) } // ép về int
""",
                    explanation="Nếu dùng `%d` với i thay vì int(i), fmt sẽ gọi lại String() và tràn stack.",
                ),
            ],
            takeaways=[
                "fmt ưu tiên Format, rồi Error, rồi String.",
                "`%+v` là verb hữu dụng nhất khi debug struct.",
                "Dùng String() để che dữ liệu nhạy cảm khỏi log.",
            ],
            exercises=[
                "Thêm String() cho một struct chứa email và số điện thoại, ẩn một phần dữ liệu."
            ],
        ),
        lesson(
            slug="interface-nil-cam-bay",
            title="Cạm bẫy interface nil",
            summary="Một interface chứa con trỏ nil thì không bằng nil — nguồn của những bug khó tìm nhất.",
            level="advanced",
            tags=["interface", "cam-bay"],
            sections=[
                sec(
                    "Hai từ, hai điều kiện",
                    "Interface value chỉ bằng nil khi **cả** con trỏ kiểu và con trỏ dữ "
                    "liệu đều nil. Nếu bạn gán một `*MyError` nil vào biến `error`, phần "
                    "kiểu đã được điền, nên `err != nil` là đúng dù dữ liệu là nil.",
                    "Kết quả: hàm “không có lỗi” lại bị người gọi coi là có lỗi, và thường "
                    "chỉ vỡ ra ở production.",
                ),
                sec(
                    "Cách phòng tránh",
                    "Đừng khai báo biến kiểu con trỏ lỗi cụ thể rồi trả về nó. Hãy trả về "
                    "`nil` tường minh ở nhánh thành công, hoặc dùng kiểu `error` ngay từ "
                    "biến trung gian.",
                    "`go vet` không bắt được mọi trường hợp này, nên hãy coi đó là mẫu cần "
                    "chú ý trong code review: bất kỳ hàm nào khai báo biến `*SomeError` "
                    "rồi `return that` đều đáng ngờ.",
                    note="Quy tắc an toàn: kiểu trả về của hàm phải là `error`, và mọi biến trung gian giữ lỗi cũng nên có kiểu `error`.",
                ),
            ],
            samples=[
                code(
                    "Bug và bản sửa",
                    """
type ValidationError struct{ Field string }

func (e *ValidationError) Error() string { return "sai trường " + e.Field }

// SAI: trả về interface không nil dù con trỏ là nil
func validateBad(v string) error {
	var err *ValidationError
	if v == "" {
		err = &ValidationError{Field: "name"}
	}
	return err // luôn != nil
}

// ĐÚNG
func validateGood(v string) error {
	if v == "" {
		return &ValidationError{Field: "name"}
	}
	return nil
}
""",
                    output='validateBad("ok") != nil  // true (bug!)\nvalidateGood("ok") != nil // false',
                ),
            ],
            takeaways=[
                "Interface nil cần cả phần kiểu và phần dữ liệu đều nil.",
                "Đừng trả về biến con trỏ lỗi cụ thể; trả `nil` tường minh.",
                "Biến trung gian giữ lỗi nên khai báo kiểu `error`.",
            ],
            exercises=[
                'Viết test chứng minh `validateBad("ok") != nil` rồi sửa hàm cho test chuyển sang pass.'
            ],
        ),
    ],
)
