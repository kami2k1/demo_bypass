"""Interactive HTML/CSS demos that illustrate Go runtime behaviour."""

from __future__ import annotations

from app.content.models import Demo

DEMOS: tuple[Demo, ...] = (
    Demo(
        slug="goroutine-scheduler",
        title="Bộ lập lịch G-M-P",
        summary=(
            "Mô phỏng cách runtime gán goroutine (G) vào logical processor (P) "
            "rồi chạy trên OS thread (M), kèm hàng đợi chờ."
        ),
        template="demos/goroutine_scheduler.html",
        concept="runtime scheduler",
        related_lesson="goroutine-co-ban",
    ),
    Demo(
        slug="channel-pipeline",
        title="Pipeline qua channel",
        summary=(
            "Ba stage generator → square → printer, mỗi bước là một goroutine "
            "nối với nhau bằng channel có buffer."
        ),
        template="demos/channel_pipeline.html",
        concept="channels",
        related_lesson="pipeline-va-fan-out",
    ),
    Demo(
        slug="slice-growth",
        title="Slice tăng trưởng",
        summary=(
            "Quan sát len/cap thay đổi khi append vượt capacity và mảng nền được cấp phát lại."
        ),
        template="demos/slice_growth.html",
        concept="slices",
        related_lesson="slice-va-mang",
    ),
    Demo(
        slug="gc-cycle",
        title="Chu kỳ garbage collector",
        summary=("Các pha của GC ba màu: mark setup, concurrent mark, mark termination và sweep."),
        template="demos/gc_cycle.html",
        concept="garbage collector",
        related_lesson="garbage-collector-hoat-dong",
    ),
    Demo(
        slug="build-speed",
        title="So sánh thời gian build",
        summary=(
            "Biểu đồ CSS thuần so sánh thời gian biên dịch lại một service "
            "trung bình giữa Go, Rust, C++ và Java."
        ),
        template="demos/build_speed.html",
        concept="tooling",
        related_lesson="toc-do-bien-dich",
    ),
    Demo(
        slug="interface-dispatch",
        title="Interface dispatch",
        summary=(
            "Cấu trúc bên trong một interface value: con trỏ itab và con trỏ "
            "dữ liệu, và cách gọi phương thức đi qua nó."
        ),
        template="demos/interface_dispatch.html",
        concept="interfaces",
        related_lesson="interface-co-ban",
    ),
    Demo(
        slug="http-request-lifecycle",
        title="Vòng đời một HTTP request",
        summary=(
            "Từ accept socket, goroutine per connection, middleware chain, "
            "handler, tới lúc ghi response."
        ),
        template="demos/http_request_lifecycle.html",
        concept="net/http",
        related_lesson="net-http-server-dau-tien",
    ),
    Demo(
        slug="mutex-contention",
        title="Tranh chấp mutex",
        summary=(
            "Bốn goroutine cùng giành một sync.Mutex: một chạy, ba xếp hàng, "
            "và điều gì xảy ra khi thay bằng sharding."
        ),
        template="demos/mutex_contention.html",
        concept="synchronisation",
        related_lesson="mutex-va-rwmutex",
    ),
)
