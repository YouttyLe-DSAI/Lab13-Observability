# Incident Response Runbook (L1)

Tiêu chuẩn xử lý sự cố cho hệ thống AI Observability Lab.

## 1. Alert: High Latency (P95 > 5s)
- **Tình trạng**: Hệ thống phản hồi chậm, gây ảnh hưởng đến trải nghiệm người dùng.
- **Nguyên nhân tiềm năng**:
    - RAG (Retrieval) đang quét quá nhiều tài liệu.
    - OpenAI API đang gặp sự cố về độ trễ.
- **Quy trình xử lý**:
    1. Kiểm tra Dashboard SRE để xác định thời điểm bắt đầu chậm.
    2. Kiểm tra log `data/logs.jsonl` tìm các request có `latency_ms > 5000`.
    3. Thử bật **Turbo Mode** để giảm tải và rút ngắn câu trả lời.

## 2. Alert: High Error Rate (> 10%)
- **Tình trạng**: Nhiều request Chat thất bại liên tục.
- **Nguyên nhân tiềm năng**:
    - Hết hạn ngạch OpenAI API.
    - Sai cấu hình API Key.
- **Quy trình xử lý**:
    1. Kiểm tra mã lỗi trong phần **System Errors** trên Dashboard.
    2. Nếu là `api_outage`, hãy liên hệ ngay với người quản trị API.
    3. Kiểm tra biến môi trường `.env`.

## 3. Alert: Quality Degradation (Score < 3.0)
- **Tình trạng**: AI trả lời lan man hoặc bị ảo giác (Hallucination).
- **Quy trình xử lý**:
    1. Truy cập Langfuse (nếu có) để xem Waterfall Trace.
    2. Điều chỉnh System Prompt để tăng tính chính xác.
