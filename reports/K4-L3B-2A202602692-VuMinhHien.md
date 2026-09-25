# Individual contribution report

## Thông tin

- Họ và tên: Vũ Minh Hiển
- Mã học viên: 2A202602692
- Nhóm: Lạc Trôi
- Repository/branch: Hien

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Giao diện ứng dụng Streamlit | Xây dựng giao diện trợ lý pháp luật cho hộ kinh doanh bằng Streamlit; thiết lập page config, bố cục sidebar, khu vực giới thiệu và khung chat | `app.py` | Done |
| Hiển thị nguồn tham khảo | Xây dựng hàm `render_source()` để hiển thị tiêu đề, nguồn, score và URL của tài liệu tham khảo; tích hợp phần nguồn dưới mỗi câu trả lời | `app.py` | Done |
| Luồng hỏi đáp | Tích hợp ô nhập câu hỏi, lưu lịch sử hội thoại trong `st.session_state.messages` và gọi `generate_with_citation()` để sinh câu trả lời kèm nguồn | `app.py` | Done |
| Tham số truy xuất | Thêm thanh trượt `top_k` trong sidebar để người dùng điều chỉnh số lượng chunks được sử dụng khi tra cứu | `app.py` | Done |
| Trình bày giao diện | Thiết kế CSS cho màu nền, sidebar, tiêu đề, source card và phần giới thiệu của ứng dụng | `app.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng `st.session_state.messages` để lưu lịch sử hội thoại.
   **Lý do/evidence:** Ứng dụng cần hiển thị lại các câu hỏi và câu trả lời sau mỗi lần Streamlit chạy lại script; `st.session_state` cho phép duy trì danh sách message trong phiên làm việc.
   **Trade-off:** Cách này phù hợp cho lịch sử hội thoại trong một phiên sử dụng, nhưng chưa phải cơ chế lưu trữ lâu dài giữa các phiên hoặc giữa nhiều người dùng.

2. **Quyết định:** Hiển thị nguồn tham khảo ngay dưới mỗi câu trả lời thông qua `render_source()` và `st.expander()`.
   **Lý do/evidence:** `generate_with_citation()` trả về `answer`, `sources` và `retrieval_source`; giao diện sử dụng các trường này để người dùng có thể kiểm tra nguồn của câu trả lời.
   **Trade-off:** Giao diện có thêm thông tin kỹ thuật như score và URL, nhưng giúp tăng khả năng kiểm chứng câu trả lời.

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:** Nhập câu hỏi vào ô `Nhập câu hỏi...` trên giao diện Streamlit để kiểm tra luồng từ người dùng nhập câu hỏi → gọi `generate_with_citation(query, top_k=top_k)` → hiển thị câu trả lời → hiển thị nguồn tham khảo.
- **Kết quả trước/sau nếu có:** Ứng dụng có thể duy trì lịch sử các message trong phiên, hiển thị câu trả lời và mở rộng phần `Nguồn tham khảo` bên dưới câu trả lời khi có source.
- **Lỗi đã phát hiện và cách xử lý:** Trong phạm vi `app.py`, có xử lý trường hợp không có nguồn bằng điều kiện `if sources:` và trường hợp metadata không có URL bằng cách chỉ hiển thị link khi `url` tồn tại.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: `app.py` phụ thuộc vào module `src.task10_generation` và hàm `generate_with_citation()`, nên phần giao diện không tự xử lý việc truy xuất hoặc sinh câu trả lời nếu module backend không hoạt động.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: bổ sung trạng thái lỗi/thông báo thân thiện khi quá trình tra cứu hoặc sinh câu trả lời gặp exception, đồng thời bổ sung cơ chế kiểm soát lịch sử hội thoại rõ ràng hơn.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Vũ Minh Hiển