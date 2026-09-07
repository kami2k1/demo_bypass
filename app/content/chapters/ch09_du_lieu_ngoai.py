"""Chương 9 — Dữ liệu và tích hợp bên ngoài."""

from __future__ import annotations

from app.content.builder import chapter, code, lesson, sec

CHAPTER = chapter(
    slug="du-lieu-ngoai",
    title="Dữ liệu và tích hợp",
    summary=(
        "database/sql, transaction, connection pool, cache, gRPC và message "
        "queue — nơi phần lớn độ trễ và sự cố thực tế xuất hiện."
    ),
    lessons=[
        lesson(
            slug="database-sql-co-ban",
            title="database/sql: interface chung cho mọi driver",
            summary="Thư viện chuẩn định nghĩa API, driver hiện thực nó — và bạn phải hiểu vòng đời Rows.",
            level="intermediate",
            tags=["du-lieu", "sql"],
            sections=[
                sec(
                    "sql.DB không phải một kết nối",
                    "`sql.DB` là một **pool** kết nối, an toàn cho nhiều goroutine, nên hãy "
                    "tạo một lần khi khởi động và tiêm vào các thành phần. `sql.Open` không "
                    "kết nối ngay; dùng `db.PingContext` để kiểm tra thật sự.",
                    "Driver được đăng ký bằng import blank: "
                    '`_ "github.com/jackc/pgx/v5/stdlib"`. Điều này cho phép đổi driver mà '
                    "phần còn lại của code không thay đổi.",
                ),
                sec(
                    "QueryRow, Query và Exec",
                    "`QueryRowContext` cho một hàng — lỗi không có hàng trả về "
                    "`sql.ErrNoRows`, hãy chuyển nó thành lỗi miền của bạn. "
                    "`QueryContext` cho nhiều hàng và **bắt buộc** `defer rows.Close()` cùng "
                    "kiểm tra `rows.Err()` sau vòng lặp. `ExecContext` cho INSERT/UPDATE.",
                    "Rows đang mở giữ một kết nối khỏi pool. Quét dữ liệu xong rồi hãy gọi "
                    "logic nghiệp vụ; đừng gọi API bên ngoài trong lúc vòng lặp rows còn mở.",
                    note="Bốn dòng bắt buộc khi dùng Query: kiểm tra err, defer Close, kiểm tra lỗi Scan, kiểm tra rows.Err().",
                ),
            ],
            samples=[
                code(
                    "Đọc nhiều hàng đúng cách",
                    """
func (s *Store) UsersByOrg(ctx context.Context, orgID string) ([]User, error) {
	rows, err := s.db.QueryContext(ctx,
		`SELECT id, email, created_at FROM users WHERE org_id = $1 ORDER BY created_at`,
		orgID)
	if err != nil {
		return nil, fmt.Errorf("truy vấn users: %w", err)
	}
	defer rows.Close()

	var users []User
	for rows.Next() {
		var u User
		if err := rows.Scan(&u.ID, &u.Email, &u.CreatedAt); err != nil {
			return nil, fmt.Errorf("quét hàng: %w", err)
		}
		users = append(users, u)
	}
	return users, rows.Err() // lỗi xảy ra giữa lúc lặp
}
""",
                ),
                code(
                    "Chuyển ErrNoRows thành lỗi miền",
                    """
func (s *Store) User(ctx context.Context, id string) (User, error) {
	var u User
	err := s.db.QueryRowContext(ctx,
		`SELECT id, email FROM users WHERE id = $1`, id).
		Scan(&u.ID, &u.Email)

	if errors.Is(err, sql.ErrNoRows) {
		return User{}, fmt.Errorf("user %s: %w", id, ErrNotFound)
	}
	return u, err
}
""",
                ),
            ],
            takeaways=[
                "`sql.DB` là pool dùng chung, tạo một lần lúc khởi động.",
                "Luôn defer rows.Close() và kiểm tra rows.Err().",
                "Đổi sql.ErrNoRows thành lỗi miền để tầng trên không phụ thuộc vào SQL.",
            ],
            exercises=["Viết hàm đếm bản ghi theo điều kiện và test bằng sqlmock hoặc DB tạm."],
        ),
        lesson(
            slug="transaction-va-isolation",
            title="Transaction và mức cô lập",
            summary="Mẫu defer rollback, hàm bọc transaction, và ý nghĩa thực tế của các isolation level.",
            level="advanced",
            tags=["du-lieu", "sql"],
            sections=[
                sec(
                    "Mẫu an toàn",
                    "Sau `BeginTx`, đặt ngay `defer tx.Rollback()`. Rollback sau khi Commit "
                    "thành công là no-op, nên mẫu này an toàn và đảm bảo không bao giờ để lại "
                    "transaction treo khi có return sớm hay panic.",
                    "Tốt hơn nữa: viết một hàm bọc nhận `func(*sql.Tx) error`, để mọi nơi "
                    "trong code dùng transaction theo cùng một cách và không thể quên rollback.",
                ),
                sec(
                    "Isolation level nghĩa là gì",
                    "Read Committed (mặc định của PostgreSQL) chặn dirty read nhưng cho phép "
                    "hai lần đọc trong cùng transaction thấy dữ liệu khác nhau. Repeatable "
                    "Read chặn điều đó. Serializable cho kết quả như thể các transaction chạy "
                    "lần lượt, nhưng sẽ trả lỗi serialization mà bạn **phải** retry.",
                    "Giữ transaction ngắn. Đừng gọi HTTP bên ngoài hay chờ người dùng trong "
                    "khi transaction mở — bạn đang giữ khoá và một kết nối của pool.",
                    note="Với Serializable, retry là phần bắt buộc của thiết kế, không phải xử lý ngoại lệ.",
                ),
            ],
            samples=[
                code(
                    "Hàm bọc transaction",
                    """
func (s *Store) InTx(ctx context.Context, fn func(*sql.Tx) error) error {
	tx, err := s.db.BeginTx(ctx, &sql.TxOptions{
		Isolation: sql.LevelReadCommitted,
	})
	if err != nil {
		return fmt.Errorf("mở transaction: %w", err)
	}
	defer tx.Rollback() // no-op nếu đã commit

	if err := fn(tx); err != nil {
		return err
	}
	return tx.Commit()
}
""",
                ),
                code(
                    "Chuyển tiền trong một transaction",
                    """
err := store.InTx(ctx, func(tx *sql.Tx) error {
	if _, err := tx.ExecContext(ctx,
		`UPDATE wallets SET cents = cents - $1 WHERE id = $2 AND cents >= $1`,
		amount, from); err != nil {
		return err
	}
	res, err := tx.ExecContext(ctx,
		`UPDATE wallets SET cents = cents + $1 WHERE id = $2`, amount, to)
	if err != nil {
		return err
	}
	if n, _ := res.RowsAffected(); n == 0 {
		return ErrNotFound
	}
	return nil
})
""",
                    explanation="Điều kiện `cents >= $1` đẩy việc kiểm tra số dư vào chính câu lệnh, tránh race giữa đọc và ghi.",
                ),
            ],
            takeaways=[
                "`defer tx.Rollback()` ngay sau BeginTx là mẫu an toàn.",
                "Hàm bọc transaction giúp toàn bộ code dùng chung một kỷ luật.",
                "Serializable cần retry; transaction phải ngắn.",
            ],
            exercises=["Thêm retry cho lỗi serialization và test bằng hai transaction song song."],
        ),
        lesson(
            slug="connection-pool-tuning",
            title="Cấu hình connection pool",
            summary="Ba tham số nhỏ quyết định service của bạn chịu tải tốt hay sụp khi cao điểm.",
            level="advanced",
            tags=["du-lieu", "hieu-nang", "van-hanh"],
            sections=[
                sec(
                    "Ba tham số",
                    "`SetMaxOpenConns` là trần số kết nối đồng thời; vượt quá thì goroutine "
                    "phải chờ. `SetMaxIdleConns` là số kết nối giữ rảnh để tái sử dụng — nên "
                    "đặt bằng MaxOpenConns nếu tải đều. `SetConnMaxLifetime` buộc kết nối bị "
                    "làm mới định kỳ, giúp phân phối lại tải sau khi DB failover.",
                    "Mặc định MaxOpenConns là không giới hạn: một đợt tải cao có thể mở hàng "
                    "nghìn kết nối và làm DB từ chối phục vụ. Đây là mặc định phải sửa.",
                ),
                sec(
                    "Chọn con số như thế nào",
                    "Điểm khởi đầu hợp lý: tổng số kết nối của **tất cả** instance phải nhỏ "
                    "hơn giới hạn của DB, chừa chỗ cho migration và công cụ vận hành. Với "
                    "PostgreSQL cho phép 100 kết nối và 5 pod, đặt MaxOpenConns khoảng 15.",
                    "Nhiều kết nối hơn không phải lúc nào cũng nhanh hơn: quá nhiều kết nối "
                    "gây tranh chấp trong DB và làm mọi truy vấn chậm đi. Hãy đo p99 chứ đừng "
                    "chỉ nhìn thông lượng.",
                    note="Nếu goroutine chờ lấy kết nối, độ trễ tăng nhưng CPU không tăng — dấu hiệu điển hình của pool quá nhỏ. `db.Stats().WaitCount` cho biết chính xác.",
                ),
            ],
            samples=[
                code(
                    "Cấu hình và theo dõi pool",
                    """
db.SetMaxOpenConns(15)
db.SetMaxIdleConns(15)
db.SetConnMaxLifetime(30 * time.Minute)
db.SetConnMaxIdleTime(5 * time.Minute)

// Xuất số liệu pool ra metrics
go func() {
	for range time.Tick(10 * time.Second) {
		s := db.Stats()
		gauge("db_in_use", float64(s.InUse))
		gauge("db_idle", float64(s.Idle))
		counter("db_wait_total", float64(s.WaitCount))
		gauge("db_wait_ms", float64(s.WaitDuration.Milliseconds()))
	}
}()
""",
                ),
            ],
            takeaways=[
                "MaxOpenConns mặc định không giới hạn — luôn đặt giá trị.",
                "Tổng kết nối của mọi instance phải nhỏ hơn giới hạn của DB.",
                "`db.Stats().WaitCount` là chỉ số phát hiện pool quá nhỏ.",
            ],
            exercises=["Thêm metrics pool vào một service và tạo tải để quan sát WaitCount tăng."],
        ),
        lesson(
            slug="repository-pattern",
            title="Tầng lưu trữ và ranh giới phụ thuộc",
            summary="Giữ SQL trong một tầng, để logic nghiệp vụ test được mà không cần database.",
            level="intermediate",
            tags=["du-lieu", "kien-truc"],
            sections=[
                sec(
                    "Ranh giới ở đâu",
                    "Tầng store nhận và trả kiểu miền, không để lộ `*sql.Rows` hay kiểu của "
                    "driver ra ngoài. Nhờ đó tầng nghiệp vụ không biết dữ liệu đến từ "
                    "PostgreSQL, HTTP hay bộ nhớ.",
                    "Đúng theo tinh thần Go: store trả về struct cụ thể, còn tầng nghiệp vụ "
                    "tự khai báo interface hẹp gồm các phương thức nó cần.",
                ),
                sec(
                    "Đừng trừu tượng hoá quá mức",
                    "Repository generic với `Find(criteria)` thường tái tạo lại SQL bằng Go, "
                    "phức tạp hơn và chậm hơn. Hãy viết phương thức theo đúng nhu cầu: "
                    "`UsersByOrg`, `PendingInvoices` — tên nói lên truy vấn.",
                    "Test tầng store bằng database thật (Docker hoặc testcontainers). Mock DB "
                    "chỉ kiểm tra rằng bạn đã gọi hàm nào, không kiểm tra SQL có đúng không.",
                    note="Quy tắc: mock ở ranh giới bạn không sở hữu (API bên thứ ba), dùng thật ở ranh giới bạn sở hữu (DB của chính bạn).",
                ),
            ],
            samples=[
                code(
                    "Store cụ thể, interface ở phía dùng",
                    """
// internal/store/postgres.go
type Postgres struct{ db *sql.DB }

func (p *Postgres) PendingInvoices(ctx context.Context, orgID string) ([]Invoice, error) {
	// ... SQL ở đây và chỉ ở đây
}

// internal/billing/service.go
type invoiceStore interface { // interface hẹp, do người dùng định nghĩa
	PendingInvoices(ctx context.Context, orgID string) ([]Invoice, error)
}

type Service struct{ store invoiceStore }

func (s Service) TotalDue(ctx context.Context, orgID string) (int64, error) {
	invs, err := s.store.PendingInvoices(ctx, orgID)
	if err != nil {
		return 0, err
	}
	var total int64
	for _, i := range invs {
		total += i.AmountCents
	}
	return total, nil
}
""",
                ),
                code(
                    "Test nghiệp vụ không cần DB",
                    """
type fakeStore struct{ invoices []Invoice }

func (f fakeStore) PendingInvoices(context.Context, string) ([]Invoice, error) {
	return f.invoices, nil
}

func TestTotalDue(t *testing.T) {
	svc := Service{store: fakeStore{invoices: []Invoice{{AmountCents: 1000}, {AmountCents: 500}}}}
	got, err := svc.TotalDue(context.Background(), "org-1")
	if err != nil || got != 1500 {
		t.Fatalf("got %d, %v", got, err)
	}
}
""",
                ),
            ],
            takeaways=[
                "SQL chỉ tồn tại trong tầng store; kiểu miền đi ra ngoài.",
                "Interface hẹp do tầng nghiệp vụ định nghĩa.",
                "Test store bằng DB thật, test nghiệp vụ bằng fake.",
            ],
            exercises=["Tách một handler gọi SQL trực tiếp thành store + service + fake test."],
        ),
        lesson(
            slug="migration-schema",
            title="Migration schema",
            summary="Schema là code: có phiên bản, chạy tự động, và luôn tương thích ngược một bước.",
            level="intermediate",
            tags=["du-lieu", "van-hanh"],
            sections=[
                sec(
                    "Nguyên tắc vận hành",
                    "Migration đánh số tăng dần, chỉ tiến không lùi trong production, và được "
                    "áp dụng trước khi phiên bản code mới nhận traffic. Lưu file SQL trong "
                    "repo và nhúng bằng `embed` để binary tự chạy được migration.",
                    "Mỗi migration phải tương thích với **cả** phiên bản code cũ và mới, vì "
                    "trong lúc rolling update hai phiên bản cùng chạy.",
                ),
                sec(
                    "Thay đổi phá vỡ, chia làm nhiều bước",
                    "Đổi tên cột không làm một lần. Bước 1: thêm cột mới, ghi vào cả hai. "
                    "Bước 2: backfill dữ liệu. Bước 3: chuyển code đọc cột mới. Bước 4: xoá "
                    "cột cũ. Mỗi bước là một lần triển khai riêng.",
                    "Với bảng lớn, hãy dùng `CREATE INDEX CONCURRENTLY` (PostgreSQL) để không "
                    "khoá bảng, và tránh `ALTER TABLE` yêu cầu viết lại toàn bộ dữ liệu trong "
                    "giờ cao điểm.",
                    note="Migration cần thời gian dài phải chạy như một job riêng, không nằm trong đường khởi động của service.",
                ),
            ],
            samples=[
                code(
                    "Migration nhúng trong binary",
                    """
//go:embed migrations/*.sql
var migrationFS embed.FS

func migrate(ctx context.Context, db *sql.DB) error {
	entries, err := fs.Glob(migrationFS, "migrations/*.sql")
	if err != nil {
		return err
	}
	slices.Sort(entries) // 0001_..., 0002_...

	for _, name := range entries {
		applied, err := isApplied(ctx, db, name)
		if err != nil || applied {
			if err != nil {
				return err
			}
			continue
		}
		body, _ := migrationFS.ReadFile(name)
		if err := runInTx(ctx, db, string(body), name); err != nil {
			return fmt.Errorf("migration %s: %w", name, err)
		}
	}
	return nil
}
""",
                ),
                code(
                    "Đổi tên cột an toàn",
                    """
-- 0007_add_full_name.sql (bước 1)
ALTER TABLE users ADD COLUMN full_name text;

-- 0008_backfill_full_name.sql (bước 2)
UPDATE users SET full_name = name WHERE full_name IS NULL;

-- 0009_drop_name.sql (bước 4, sau khi code mới đã chạy ổn định)
ALTER TABLE users DROP COLUMN name;
""",
                    language="sql",
                ),
            ],
            takeaways=[
                "Migration có phiên bản, chỉ tiến, chạy trước khi code mới nhận traffic.",
                "Mỗi migration tương thích với cả code cũ và mới.",
                "Đổi tên cột chia thành bốn bước triển khai.",
            ],
            exercises=["Viết kế hoạch bốn bước để đổi kiểu một cột từ int sang bigint."],
        ),
        lesson(
            slug="cache-va-invalidation",
            title="Cache và bài toán vô hiệu hoá",
            summary="Cache dễ thêm, khó đúng. TTL, stampede và cache-aside là ba thứ cần nắm.",
            level="advanced",
            tags=["du-lieu", "hieu-nang", "kien-truc"],
            sections=[
                sec(
                    "Cache-aside và TTL",
                    "Mẫu phổ biến nhất: đọc cache, miss thì đọc DB rồi ghi vào cache với TTL. "
                    "Đơn giản và chịu lỗi tốt — cache chết thì hệ thống chậm đi chứ không sai. "
                    "TTL ngắn giảm nguy cơ dữ liệu cũ; TTL dài giảm tải DB.",
                    "Khi ghi dữ liệu, hãy xoá key (invalidate) thay vì cập nhật cache. Cập "
                    "nhật tạo ra race giữa hai bên ghi và dễ để lại dữ liệu sai vĩnh viễn.",
                ),
                sec(
                    "Cache stampede",
                    "Khi một key nóng hết hạn, hàng nghìn request cùng miss và cùng đánh vào "
                    "DB. Cách chữa: dùng `singleflight` để chỉ một goroutine đi lấy dữ liệu, "
                    "phần còn lại chờ và dùng chung kết quả.",
                    "Thêm jitter vào TTL để các key không hết hạn cùng lúc. Với dữ liệu rất "
                    "nóng, dùng mẫu “serve stale while revalidate”: trả dữ liệu cũ ngay và "
                    "làm mới trong nền.",
                    note="Trước khi thêm cache, hãy chắc chắn truy vấn đã có index. Cache là cách che vấn đề chứ không sửa nó.",
                ),
            ],
            samples=[
                code(
                    "Cache-aside với singleflight",
                    """
type UserCache struct {
	inner  *lru.Cache[string, User]
	loader *singleflight.Group
	store  userStore
	ttl    time.Duration
}

func (c *UserCache) User(ctx context.Context, id string) (User, error) {
	if u, ok := c.inner.Get(id); ok {
		return u, nil
	}
	// Chỉ một goroutine cho mỗi id đi xuống DB
	v, err, _ := c.loader.Do(id, func() (any, error) {
		u, err := c.store.User(ctx, id)
		if err != nil {
			return nil, err
		}
		c.inner.Add(id, u)
		return u, nil
	})
	if err != nil {
		return User{}, err
	}
	return v.(User), nil
}
""",
                ),
                code(
                    "TTL có jitter",
                    """
func ttlWithJitter(base time.Duration) time.Duration {
	jitter := time.Duration(rand.Int64N(int64(base / 5))) // ±20%
	return base - base/10 + jitter
}
""",
                ),
            ],
            takeaways=[
                "Cache-aside + TTL là điểm khởi đầu đúng cho hầu hết trường hợp.",
                "Khi ghi, xoá key thay vì cập nhật cache.",
                "singleflight và TTL jitter chống cache stampede.",
            ],
            exercises=["Đo tỉ lệ hit của cache và thử ba giá trị TTL khác nhau dưới cùng một tải."],
        ),
        lesson(
            slug="grpc-va-protobuf",
            title="gRPC và Protocol Buffers",
            summary="Khi giao tiếp giữa các service nội bộ, hợp đồng sinh code thắng JSON viết tay.",
            level="advanced",
            tags=["du-lieu", "api", "kien-truc"],
            sections=[
                sec(
                    "Vì sao dùng gRPC nội bộ",
                    "File .proto là hợp đồng duy nhất; client và server đều sinh từ nó nên "
                    "không lệch nhau. Payload binary nhỏ hơn JSON, HTTP/2 cho phép nhiều "
                    "request trên một kết nối và hỗ trợ streaming hai chiều.",
                    "Đổi lại, gRPC khó debug bằng curl hơn và cần thêm bước sinh code trong "
                    "build. Với API công khai cho web/mobile, REST + JSON vẫn thường là lựa "
                    "chọn thực dụng hơn.",
                ),
                sec(
                    "Tiến hoá schema",
                    "Quy tắc tương thích: chỉ thêm field với số thứ tự mới, không bao giờ đổi "
                    "hay tái sử dụng số cũ, dùng `reserved` cho field đã xoá. Field mới ở "
                    "client cũ sẽ bị bỏ qua một cách an toàn.",
                    "Lỗi gRPC dùng mã trạng thái riêng (codes.NotFound, codes.InvalidArgument). "
                    "Hãy ánh xạ lỗi miền của bạn sang các mã này ở một chỗ, giống như với HTTP.",
                    note="Đặt deadline cho mọi lời gọi gRPC. Không có deadline, một service chậm sẽ lan sự cố ngược lên toàn bộ chuỗi gọi.",
                ),
            ],
            samples=[
                code(
                    "Định nghĩa service",
                    """
syntax = "proto3";
package billing.v1;

service Billing {
  rpc GetInvoice(GetInvoiceRequest) returns (Invoice);
  rpc StreamInvoices(StreamRequest) returns (stream Invoice);
}

message Invoice {
  string id = 1;
  int64 amount_cents = 2;
  reserved 3;            // field cũ đã xoá, không dùng lại số này
  string currency = 4;
}
""",
                    language="protobuf",
                ),
                code(
                    "Client có deadline",
                    """
conn, err := grpc.NewClient("billing:9000",
	grpc.WithTransportCredentials(insecure.NewCredentials()))
if err != nil {
	return err
}
defer conn.Close()

client := billingv1.NewBillingClient(conn)

ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
defer cancel()

inv, err := client.GetInvoice(ctx, &billingv1.GetInvoiceRequest{Id: id})
if status.Code(err) == codes.NotFound {
	return ErrNotFound
}
""",
                ),
            ],
            takeaways=[
                "proto là hợp đồng duy nhất, client/server sinh từ đó.",
                "Chỉ thêm field mới; dùng `reserved` cho field đã xoá.",
                "Luôn đặt deadline cho lời gọi gRPC.",
            ],
            exercises=[
                "Viết một service gRPC hai method và client gọi nó, có deadline và ánh xạ lỗi."
            ],
        ),
        lesson(
            slug="message-queue-va-idempotent",
            title="Message queue và xử lý idempotent",
            summary="Giao nhận “ít nhất một lần” là mặc định, nên consumer của bạn phải chịu được trùng lặp.",
            level="advanced",
            tags=["du-lieu", "kien-truc", "van-hanh"],
            sections=[
                sec(
                    "At-least-once nghĩa là sẽ có trùng lặp",
                    "Hầu hết queue đảm bảo giao ít nhất một lần: nếu consumer xử lý xong "
                    "nhưng chết trước khi ack, message sẽ được giao lại. Vì thế mọi handler "
                    "phải idempotent — xử lý hai lần cho cùng kết quả như một lần.",
                    "Cách phổ biến: mỗi message có id duy nhất; consumer lưu id đã xử lý vào "
                    "bảng có ràng buộc unique, và bỏ qua nếu insert vi phạm ràng buộc.",
                ),
                sec(
                    "Ack, retry và dead letter",
                    "Chỉ ack sau khi công việc đã bền vững (đã commit vào DB). Với lỗi tạm "
                    "thời thì nack để nhận lại; với lỗi vĩnh viễn (message sai định dạng) hãy "
                    "đưa vào dead-letter queue thay vì retry vô hạn.",
                    "Đếm số lần thử và giới hạn nó. Một message “độc” retry mãi có thể chiếm "
                    "hết consumer và làm nghẽn toàn bộ hàng đợi.",
                    note="Thứ tự message thường chỉ được bảo đảm trong một partition. Nếu logic của bạn cần thứ tự, hãy chọn partition key theo entity.",
                ),
            ],
            samples=[
                code(
                    "Consumer idempotent",
                    """
func (c *Consumer) handle(ctx context.Context, msg Message) error {
	return c.store.InTx(ctx, func(tx *sql.Tx) error {
		_, err := tx.ExecContext(ctx,
			`INSERT INTO processed_messages (id) VALUES ($1)`, msg.ID)
		if isUniqueViolation(err) {
			return nil // đã xử lý trước đó, bỏ qua
		}
		if err != nil {
			return err
		}
		return applyEffect(ctx, tx, msg) // hiệu ứng nghiệp vụ, cùng transaction
	})
}
""",
                    explanation="Ghi dấu đã xử lý và hiệu ứng nghiệp vụ nằm trong một transaction, nên hai việc luôn nhất quán.",
                ),
                code(
                    "Vòng lặp consumer với dead letter",
                    """
for msg := range queue.Messages(ctx) {
	err := c.handle(ctx, msg)
	switch {
	case err == nil:
		msg.Ack()
	case msg.Attempts >= 5:
		c.log.Error("chuyển vào dead letter", "id", msg.ID, "err", err)
		msg.DeadLetter()
	default:
		msg.Nack() // sẽ được giao lại với backoff
	}
}
""",
                ),
            ],
            takeaways=[
                "At-least-once nghĩa là handler phải idempotent.",
                "Ack chỉ sau khi kết quả đã bền vững.",
                "Giới hạn số lần thử và có dead-letter queue.",
            ],
            exercises=["Thêm bảng processed_messages và test xử lý cùng một message hai lần."],
        ),
    ],
)
