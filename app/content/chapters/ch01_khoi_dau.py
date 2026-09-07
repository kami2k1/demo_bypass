"""Chương 1 — Khởi đầu với Go."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="khoi-dau",
    title="Khởi đầu với Go",
    summary=(
        "Vì sao Go tồn tại, cách cài đặt bộ công cụ, chương trình đầu tiên và "
        "vòng lặp sửa – biên dịch – chạy nhanh đến mức thay đổi cách bạn làm việc."
    ),
    lessons=[
        lesson(
            slug="tai-sao-chon-go",
            title="Tại sao chọn Go",
            summary=(
                "Go sinh ra để giải quyết bài toán tốc độ ở ba mặt: tốc độ biên dịch, "
                "tốc độ chạy và tốc độ con người đọc hiểu code."
            ),
            level="beginner",
            tags=["tong-quan", "hieu-nang"],
            sections=[
                sec(
                    "Bối cảnh ra đời",
                    "Năm 2007 tại Google, ba kỹ sư Robert Griesemer, Rob Pike và Ken "
                    "Thompson phải chờ hàng chục phút để biên dịch lại một binary C++ "
                    "khổng lồ. Họ tự hỏi: nếu thiết kế lại một ngôn ngữ hệ thống ngay "
                    "từ đầu, với mạng và nhiều lõi CPU là chuyện mặc định, thì nó sẽ "
                    "như thế nào? Go là câu trả lời.",
                    "Kết quả là một ngôn ngữ biên dịch tĩnh, thu gom rác tự động, "
                    "có mô hình đồng thời gọn nhẹ, và cú pháp nhỏ đến mức có thể đọc "
                    "hết đặc tả trong một buổi chiều.",
                ),
                sec(
                    "Ba loại “nhanh” cần phân biệt",
                    "Nhanh khi biên dịch: một service cỡ vài chục nghìn dòng thường "
                    "build lại trong 1–3 giây, nên bạn giữ được nhịp làm việc liên tục. "
                    "Nhanh khi chạy: binary là mã máy gốc, không cần máy ảo khởi động, "
                    "process thường sẵn sàng nhận request sau vài chục mili giây. "
                    "Nhanh khi bảo trì: chỉ một cách viết vòng lặp, một cách format "
                    "code, nên người mới vào dự án đọc hiểu rất nhanh.",
                    "Nói Go là “ngôn ngữ nhanh nhất thế giới” thì nên hiểu theo nghĩa "
                    "tổng thể vòng đời phần mềm. Trên các benchmark tính toán thuần, "
                    "C, C++, Rust thường vẫn dẫn trước một khoảng; nhưng tính cả thời "
                    "gian biên dịch, thời gian khởi động và thời gian một đội ngũ đưa "
                    "tính năng lên production, Go rất khó bị đánh bại.",
                    note=(
                        "Hãy nhớ con số này khi tranh luận: Go thường đạt 80–95% hiệu "
                        "năng của C cho code mạng và xử lý dữ liệu, nhưng biên dịch "
                        "nhanh hơn hàng chục lần."
                    ),
                ),
            ],
            samples=[
                code(
                    "Một HTTP server hoàn chỉnh trong 11 dòng",
                    """
package main

import (
	"fmt"
	"net/http"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "Go xin chào!")
	})
	http.ListenAndServe(":8080", nil)
}
""",
                    output="curl localhost:8080\nGo xin chào!",
                    explanation=(
                        "Không cần thư viện ngoài, không cần application server. "
                        "Thư viện chuẩn đã có sẵn một HTTP server dùng được ở production."
                    ),
                )
            ],
            takeaways=[
                "Go được thiết kế để chữa đúng nỗi đau: build chậm và code khó đọc.",
                "“Nhanh” gồm ba chiều: biên dịch, thực thi và tốc độ bảo trì.",
                "Thư viện chuẩn đủ mạnh để viết service mạng mà không cần framework.",
            ],
            exercises=[
                "Đo thời gian `go build` của một repo Go bất kỳ rồi so với một dự án bạn đang làm.",
                "Liệt kê ba đặc điểm ngôn ngữ bạn dùng hằng ngày mà Go cố tình không có.",
            ],
        ),
        lesson(
            slug="cai-dat-va-cong-cu",
            title="Cài đặt Go và bộ công cụ",
            summary=(
                "Một lần tải về là có compiler, formatter, test runner, profiler và "
                "trình quản lý phụ thuộc — tất cả trong một binary `go`."
            ),
            level="beginner",
            tags=["tong-quan", "cong-cu"],
            sections=[
                sec(
                    "Cài đặt",
                    "Tải bản phát hành từ go.dev/dl rồi giải nén vào /usr/local/go, "
                    "hoặc dùng trình quản lý gói của hệ điều hành. Thêm "
                    "/usr/local/go/bin vào PATH là xong; Go không cần biến môi trường "
                    "GOPATH nữa kể từ khi có module.",
                    "Kiểm tra bằng `go version` và `go env`. Hai biến hay dùng là "
                    "GOBIN (nơi `go install` đặt binary) và GOMODCACHE (nơi cache "
                    "phụ thuộc đã tải).",
                ),
                sec(
                    "Bộ công cụ đi kèm",
                    "`go build` biên dịch, `go test` chạy test và benchmark, `go fmt` "
                    "định dạng, `go vet` phát hiện lỗi logic phổ biến, `go mod` quản lý "
                    "phụ thuộc, `go tool pprof` phân tích hiệu năng. Không cần chọn "
                    "giữa hàng chục build tool cạnh tranh nhau.",
                    "Hệ quả thực tế: một dự án Go mới chỉ cần hai file để chạy được — "
                    "go.mod và main.go. Không có file cấu hình build hàng trăm dòng.",
                    note="Chạy `go help` một lần để thấy toàn bộ subcommand; danh sách ngắn đến mức đọc hết được.",
                ),
            ],
            samples=[
                code(
                    "Kiểm tra môi trường",
                    """
go version
go env GOOS GOARCH GOMODCACHE
go help build
""",
                    language="bash",
                    output="go version go1.23.4 linux/amd64\nlinux\namd64\n/root/go/pkg/mod",
                ),
            ],
            takeaways=[
                "Một binary `go` gộp toàn bộ vòng đời phát triển.",
                "Module thay thế GOPATH: đặt code ở đâu cũng được.",
                "`go env` là nơi tra mọi đường dẫn khi có sự cố môi trường.",
            ],
            exercises=[
                "Chạy `go env -w GOBIN=$HOME/bin` rồi `go install` một tool nhỏ và kiểm tra file sinh ra."
            ],
        ),
        lesson(
            slug="hello-world-dau-tien",
            title="Chương trình đầu tiên",
            summary="Cấu trúc tối thiểu của một chương trình Go: package, import, hàm main.",
            level="beginner",
            tags=["co-ban", "cu-phap"],
            sections=[
                sec(
                    "Ba thành phần bắt buộc",
                    "Mọi file Go mở đầu bằng khai báo package. Chương trình thực thi "
                    "được phải thuộc `package main` và có hàm `main()` không tham số, "
                    "không giá trị trả về. Import liệt kê các package dùng trong file, "
                    "và trình biên dịch báo lỗi nếu bạn import mà không dùng.",
                    "Sự nghiêm khắc đó gây bất ngờ lúc đầu nhưng loại bỏ hẳn tình trạng "
                    "import rác tích tụ theo năm tháng trong dự án lớn.",
                ),
                sec(
                    "Chạy ngay hay biên dịch trước",
                    "`go run main.go` biên dịch vào thư mục tạm rồi chạy — tiện khi thử "
                    "nghiệm. `go build` tạo binary trong thư mục hiện tại để mang đi "
                    "triển khai. Cả hai đều nhanh tới mức bạn có thể coi Go như ngôn ngữ "
                    "script trong lúc phát triển.",
                    "Binary sinh ra là tĩnh: copy sang máy Linux khác cùng kiến trúc là "
                    "chạy được, không cần cài runtime.",
                ),
            ],
            samples=[
                code(
                    "main.go",
                    """
package main

import "fmt"

func main() {
	fmt.Println("Xin chào, Go!")
}
""",
                    output="Xin chào, Go!",
                ),
                code(
                    "Hai cách thực thi",
                    """
go run main.go
go build -o hello . && ./hello
""",
                    language="bash",
                    explanation="`go run` cho vòng lặp thử nghiệm nhanh, `go build` cho artefact triển khai.",
                ),
            ],
            takeaways=[
                "Chương trình thực thi cần `package main` và hàm `main()`.",
                "Import không dùng là lỗi biên dịch, không phải cảnh báo.",
                "Binary Go mặc định liên kết tĩnh nên dễ triển khai.",
            ],
            exercises=["Thử xoá dòng import `fmt` và đọc kỹ thông báo lỗi của compiler."],
        ),
        lesson(
            slug="go-run-build-install",
            title="go run, go build và go install",
            summary="Ba lệnh trông giống nhau nhưng phục vụ ba mục đích khác nhau trong vòng đời dự án.",
            level="beginner",
            tags=["cong-cu", "co-ban"],
            sections=[
                sec(
                    "Phân biệt",
                    "`go run` biên dịch rồi chạy ngay, artefact nằm trong thư mục tạm và "
                    "bị xoá sau đó. `go build` ghi binary ra thư mục làm việc. "
                    "`go install` biên dịch rồi đặt binary vào GOBIN để dùng như một "
                    "lệnh hệ thống.",
                    "Trong CI bạn hầu như luôn dùng `go build ./...` để chắc chắn mọi "
                    "package biên dịch được, kể cả package không được main import tới.",
                ),
                sec(
                    "Cache biên dịch",
                    "Go lưu kết quả biên dịch từng package trong build cache. Lần build "
                    "đầu của một dự án lớn có thể mất vài giây; các lần sau chỉ biên dịch "
                    "lại package thay đổi và những package phụ thuộc vào nó, nên thường "
                    "về dưới một giây.",
                    "Có thể xem cache đang chiếm bao nhiêu bằng `go env GOCACHE` và dọn "
                    "bằng `go clean -cache` khi cần build lại từ đầu để kiểm chứng.",
                    note="Đừng dọn cache trong CI trừ khi đang gỡ lỗi: bạn sẽ mất chính lợi thế tốc độ của Go.",
                ),
            ],
            samples=[
                code(
                    "Ba lệnh, ba kết quả",
                    """
go run ./cmd/api
go build -o bin/api ./cmd/api
go install ./cmd/api
go build ./...
""",
                    language="bash",
                    explanation="`./...` là mẫu khớp toàn bộ package con của module hiện tại.",
                ),
            ],
            takeaways=[
                "`go run` để thử, `go build` để đóng gói, `go install` để cài lệnh.",
                "`go build ./...` là bước gác cổng tối thiểu trong CI.",
                "Build cache theo package là lý do build lại nhanh đến vậy.",
            ],
            exercises=["Chạy `go build ./...` hai lần liên tiếp và so sánh thời gian bằng `time`."],
        ),
        lesson(
            slug="go-module-va-phu-thuoc",
            title="Go module và quản lý phụ thuộc",
            summary="go.mod khai báo phụ thuộc, go.sum khoá chúng lại bằng hash — tái lập build một cách xác định.",
            level="beginner",
            tags=["cong-cu", "phu-thuoc"],
            sections=[
                sec(
                    "Khởi tạo và thêm phụ thuộc",
                    "`go mod init example.com/myapp` tạo file go.mod chứa đường dẫn "
                    "module và phiên bản Go tối thiểu. Khi bạn import một package ngoài "
                    "rồi chạy `go mod tidy`, Go tải phiên bản phù hợp, ghi vào go.mod và "
                    "lưu checksum vào go.sum.",
                    "Cơ chế chọn phiên bản gọi là Minimal Version Selection: Go lấy "
                    "phiên bản nhỏ nhất thoả mãn mọi yêu cầu, thay vì phiên bản mới nhất. "
                    "Nhờ đó build hôm nay và build sáu tháng sau cho cùng kết quả.",
                ),
                sec(
                    "Kỷ luật vận hành",
                    "Luôn commit cả go.mod và go.sum. `go mod tidy` nên chạy trước khi "
                    "commit để loại bỏ phụ thuộc không còn dùng. Trong CI, thêm "
                    "`go mod verify` để phát hiện phụ thuộc bị sửa đổi.",
                    "Với thư viện phát hành ra ngoài, quy tắc import path có hậu tố "
                    "phiên bản từ v2 trở đi (ví dụ example.com/lib/v2) giúp hai phiên bản "
                    "lớn cùng tồn tại trong một binary.",
                ),
            ],
            samples=[
                code(
                    "Vòng làm việc với module",
                    """
go mod init example.com/golang-tour
go get github.com/google/uuid@v1.6.0
go mod tidy
go mod verify
""",
                    language="bash",
                ),
                code(
                    "go.mod sau khi tidy",
                    """
module example.com/golang-tour

go 1.23

require github.com/google/uuid v1.6.0
""",
                    language="text",
                ),
            ],
            takeaways=[
                "go.mod là ý định, go.sum là bằng chứng toàn vẹn.",
                "Minimal Version Selection cho build tái lập được.",
                "`go mod tidy` trước mỗi commit giữ danh sách phụ thuộc sạch.",
            ],
            exercises=[
                "Thêm một phụ thuộc, chạy tidy, rồi xoá import và tidy lại để xem go.mod thay đổi."
            ],
        ),
        lesson(
            slug="cau-truc-package",
            title="Package và cách tổ chức mã nguồn",
            summary="Một thư mục là một package; chữ cái đầu của tên quyết định phạm vi truy cập.",
            level="beginner",
            tags=["co-ban", "kien-truc"],
            sections=[
                sec(
                    "Quy tắc hiển thị",
                    "Định danh bắt đầu bằng chữ in hoa được xuất ra ngoài package; chữ "
                    "thường thì chỉ dùng nội bộ. Không có từ khoá public/private, chỉ có "
                    "quy ước viết hoa — ít cú pháp hơn nhưng vẫn đủ diễn đạt.",
                    "Thư mục đặc biệt tên `internal` chặn mọi import từ ngoài cây thư mục "
                    "chứa nó. Đây là cách chuẩn để giữ chi tiết triển khai không bị dự án "
                    "khác phụ thuộc vào.",
                ),
                sec(
                    "Bố cục thường gặp",
                    "Một layout dùng được cho phần lớn service: `cmd/<binary>` chứa hàm "
                    "main, `internal/<domain>` chứa logic nghiệp vụ, `pkg/` chỉ dùng khi "
                    "bạn thật sự muốn chia sẻ code ra ngoài. Tên package nên là danh từ "
                    "số ít, ngắn, không viết tắt kỳ dị: `store`, `billing`, `httpapi`.",
                    "Tránh package tên `utils` hay `common`: chúng hút mọi thứ vào và "
                    "sớm trở thành nút thắt phụ thuộc.",
                    note="Tên package xuất hiện ở mọi lời gọi: `billing.Charge()` đọc tốt hơn `billingutils.DoCharge()`.",
                ),
            ],
            samples=[
                code(
                    "Bố cục thư mục",
                    """
myapp/
├── cmd/api/main.go
├── internal/billing/invoice.go
├── internal/store/postgres.go
├── go.mod
└── go.sum
""",
                    language="text",
                ),
                code(
                    "Xuất và không xuất",
                    """
package billing

type Invoice struct {
	ID     string
	amount int64
}

func (i Invoice) Amount() int64 { return i.amount }

func normalise(cents int64) int64 { return max(cents, 0) }
""",
                    explanation="`Invoice` và `Amount` dùng được từ ngoài; `amount` và `normalise` thì không.",
                ),
            ],
            takeaways=[
                "Chữ in hoa đầu tên = xuất ra ngoài; không cần từ khoá truy cập.",
                "`internal/` là hàng rào phụ thuộc do compiler thực thi.",
                "Đặt tên package theo nghiệp vụ, đừng tạo `utils`.",
            ],
            exercises=[
                "Thử import một package trong `internal/` từ module khác và đọc thông báo lỗi."
            ],
        ),
        lesson(
            slug="gofmt-va-go-vet",
            title="gofmt, go vet và văn hoá code sạch",
            summary="Go xoá bỏ tranh luận về style bằng một formatter duy nhất và một linter đi kèm.",
            level="beginner",
            tags=["cong-cu", "chat-luong"],
            sections=[
                sec(
                    "Một cách format duy nhất",
                    "`gofmt` không có tuỳ chọn cấu hình. Tab để thụt lề, dấu ngoặc theo "
                    "một kiểu, import được nhóm và sắp xếp. Mọi dự án Go trên thế giới "
                    "trông như nhau, nên đọc code lạ không mất chi phí thích nghi.",
                    "Hệ quả bất ngờ: diff trong code review chỉ còn phản ánh thay đổi "
                    "logic, vì không ai đụng vào khoảng trắng nữa.",
                ),
                sec(
                    "Bắt lỗi trước khi chạy",
                    "`go vet` phát hiện các sai sót mà compiler cho qua: chuỗi format "
                    "không khớp tham số, copy struct chứa mutex, so sánh sai với hàm, "
                    "vòng lặp bắt biến sai. Nên đưa vào CI cùng với `go build` và "
                    "`go test`.",
                    "Nếu muốn nghiêm hơn, `staticcheck` bổ sung hàng trăm quy tắc; nhưng "
                    "chỉ riêng vet đã chặn được nhóm lỗi hay xuất hiện nhất.",
                    note="Cấu hình editor chạy `gofmt` khi lưu file; đừng bao giờ format thủ công.",
                ),
            ],
            samples=[
                code(
                    "Kiểm tra định dạng trong CI",
                    """
test -z "$(gofmt -l .)" || { gofmt -l .; exit 1; }
go vet ./...
""",
                    language="bash",
                    explanation="`gofmt -l` in ra file chưa đúng định dạng; danh sách rỗng nghĩa là đạt.",
                ),
                code(
                    "Lỗi mà vet bắt được",
                    """
name := "Go"
fmt.Printf("chào %d\\n", name)
""",
                    output="vet: Printf format %d has arg name of wrong type string",
                ),
            ],
            takeaways=[
                "gofmt không cấu hình được — đó là tính năng, không phải hạn chế.",
                "go vet chặn lớp lỗi mà compiler bỏ qua.",
                "Đưa cả hai vào CI để code review tập trung vào logic.",
            ],
            exercises=["Viết một `Printf` sai kiểu tham số rồi chạy `go vet ./...`."],
        ),
        lesson(
            slug="toc-do-bien-dich",
            title="Vì sao Go biên dịch nhanh",
            summary="Không header file, không template instantiation, đồ thị phụ thuộc phẳng và cache theo package.",
            level="intermediate",
            tags=["hieu-nang", "cong-cu"],
            sections=[
                sec(
                    "Thiết kế nhắm vào tốc độ biên dịch",
                    "C++ chậm biên dịch phần lớn vì mỗi translation unit phải phân tích "
                    "lại hàng nghìn dòng header và sinh mã cho template. Go bỏ hẳn khái "
                    "niệm header: thông tin xuất ra của một package được lưu ở dạng đã "
                    "biên dịch, nên package phụ thuộc chỉ đọc metadata gọn nhẹ.",
                    "Thêm nữa, Go cấm import vòng và yêu cầu khai báo phụ thuộc tường "
                    "minh. Đồ thị phụ thuộc vì thế là DAG, cho phép biên dịch song song "
                    "theo tầng và bỏ qua toàn bộ nhánh không thay đổi.",
                ),
                sec(
                    "Con số thực tế",
                    "Một service khoảng 50 nghìn dòng thường build sạch trong 3–6 giây "
                    "và build lại sau khi sửa một file trong khoảng 0,5–1,5 giây. Cùng "
                    "khối lượng đó ở C++ có thể mất nhiều phút, còn ở Rust thì thời gian "
                    "monomorphisation và tối ưu LLVM cũng lớn hơn đáng kể.",
                    "Vòng lặp phản hồi ngắn thay đổi hành vi lập trình: bạn chạy test "
                    "sau mỗi thay đổi nhỏ thay vì gom lại một mẻ lớn, nên lỗi được phát "
                    "hiện khi ngữ cảnh còn trong đầu.",
                    note="Đây là chiều “nhanh” dễ bị bỏ qua nhất khi so sánh ngôn ngữ, nhưng lại tác động mạnh nhất tới năng suất hằng ngày.",
                ),
            ],
            samples=[
                code(
                    "Đo build lạnh và build nóng",
                    """
go clean -cache
time go build ./...      # build lạnh
time go build ./...      # build nóng, gần như tức thì
go build -x ./... 2>&1 | head -20   # xem từng bước compiler thực hiện
""",
                    language="bash",
                    output="real 0m4.812s   # lạnh\nreal 0m0.214s   # nóng",
                ),
            ],
            takeaways=[
                "Không header + không template = ít việc lặp lại cho compiler.",
                "Cấm import vòng cho phép biên dịch song song và cache theo package.",
                "Build lại dưới một giây thay đổi cách bạn viết và kiểm thử code.",
            ],
            exercises=[
                "Đo `go build` lạnh/nóng trên chính dự án này và ghi lại số liệu.",
                "Giải thích vì sao thêm một import mới có thể làm build lại chậm hơn hẳn.",
            ],
        ),
        lesson(
            slug="doc-tai-lieu-go-doc",
            title="Đọc và viết tài liệu với go doc",
            summary="Comment đặt đúng chỗ trở thành tài liệu chính thức, tra cứu được ngay từ dòng lệnh.",
            level="beginner",
            tags=["cong-cu", "chat-luong"],
            sections=[
                sec(
                    "Tra cứu không cần rời terminal",
                    "`go doc fmt.Printf` in ra chữ ký và mô tả của hàm. `go doc -all "
                    "strings` liệt kê toàn bộ API của package. Vì tài liệu sinh trực tiếp "
                    "từ mã nguồn đang dùng, nó luôn khớp với phiên bản bạn build.",
                    "Trang pkg.go.dev là cùng dữ liệu đó ở dạng web, bao gồm cả module "
                    "của bên thứ ba.",
                ),
                sec(
                    "Viết tài liệu đúng quy ước",
                    "Comment tài liệu là khối comment ngay trên khai báo, mở đầu bằng "
                    "chính tên định danh: `// Charge trừ tiền từ ví...`. Câu đầu tiên "
                    "được dùng làm mô tả ngắn trong danh sách, nên hãy viết nó như một "
                    "câu hoàn chỉnh.",
                    "Ví dụ dạng `Example` trong file test cũng xuất hiện trong tài liệu "
                    "và được `go test` chạy như test thật, nên tài liệu không bao giờ "
                    "lỗi thời.",
                    note="Tài liệu nên nói *vì sao* và *hợp đồng sử dụng*; đừng diễn giải lại từng dòng code.",
                ),
            ],
            samples=[
                code(
                    "Tra tài liệu",
                    """
go doc net/http.ListenAndServe
go doc -all ./internal/billing
""",
                    language="bash",
                ),
                code(
                    "Comment tài liệu đúng chuẩn",
                    """
// Charge trừ số tiền cents khỏi ví của khách hàng.
// Trả về ErrInsufficientFunds nếu số dư không đủ; số dư không bị thay đổi
// khi có lỗi.
func Charge(ctx context.Context, walletID string, cents int64) error {
	// ...
	return nil
}
""",
                ),
            ],
            takeaways=[
                "`go doc` cho tài liệu khớp chính xác phiên bản đang dùng.",
                "Comment tài liệu bắt đầu bằng tên định danh và là câu hoàn chỉnh.",
                "Example test vừa là tài liệu vừa là test.",
            ],
            exercises=["Viết comment tài liệu cho một hàm bạn đã có và kiểm tra bằng `go doc`."],
        ),
    ],
)
