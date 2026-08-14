# 5. Trạng thái dự án

## Nền tảng đã có

Repository hiện có các lớp behavior, gait, open field, progression, digital
twin, AI analysis, research campaign, experiment workspace, statistical
engine, integration hardening và verification/benchmark.

## Epic 11

Epic 11 bổ sung:

- plugin registry manifest-based với lifecycle rõ ràng;
- hook và capability contract;
- plugin context không lộ Workspace nội bộ;
- dependency checking và loader;
- ba plugin examples cho analysis, statistics và export;
- bộ tài liệu kỹ thuật tiếng Việt.

## Phần chưa nên suy diễn

Plugin platform không làm thay đổi simulation, controller, evidence JSON,
manuscript hoặc kết luận khoa học. Các plugin mới phải được kiểm thử như
software extension trước khi được dùng trong workflow nghiên cứu.
