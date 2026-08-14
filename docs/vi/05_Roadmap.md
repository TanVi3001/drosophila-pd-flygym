# 6. Roadmap

Roadmap này chỉ ghi các hướng mở rộng phù hợp với kiến trúc hiện tại; không
tự tạo thêm kết luận khoa học.

1. Hoàn thiện contract test và ví dụ plugin trong Epic 11.
2. Duy trì release manifest và health scan cùng mỗi thay đổi lớn.
3. Bổ sung host adapters để expose các service read-only cần thiết cho plugin.
4. Đánh giá dependency graph và lifecycle trong môi trường browser/CI.
5. Bổ sung plugin documentation khi API capability mở rộng.
6. Chỉ sau khi review và test mới xem xét các extension cho workflow cụ thể.

Mọi thay đổi phải giữ backward compatibility, chạy compileall/pytest/diff
check và cập nhật tài liệu tương ứng.
