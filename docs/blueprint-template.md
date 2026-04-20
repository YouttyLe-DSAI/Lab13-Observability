# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [Team 04]
- [REPO_URL]: [https://github.com/YouttyLe-DSAI/Lab13-Observability]

- [MEMBERS]:
  - Member 1: Đậu Văn Nam | Role: Security & Core Log
  - Member 2: Nguyễn Trí Cao | Role: AI Tracing Lead
  - Member 3: Cao Diệu Ly | Role: SRE & Dashboard
  - Member 4: Lê Minh Tuấn | Role: QA & Demo Lead

---

## 2. Group Performance (Auto-Verified)
-[VALIDATE_LOGS_FINAL_SCORE]: 100/100

-[TOTAL_TRACES_COUNT]: 50+

-[PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: ![alt text]({DFF0164F-2FB8-4821-B4F8-65999C67998B}.png)
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: ![alt text](image-2.png)
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [screenshots/trace_waterfall.png]
- [TRACE_WATERFALL_EXPLANATION]: Trace waterfall ghi lại hành trình từ khi request đi qua Middleware (gắn Correlation ID) đến khi OpenAI thực hiện Generation. Thú vị nhất là Span tự động của Langfuse đã bắt được chính xác model `gpt-4o-mini` giúp chúng ta kiểm chứng được logic Tối ưu chi phí.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [screenshots/global_telemetry_dashboard.png]
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 1240ms |
| Error Rate | < 2% | 28d | 0.5% |
| Cost Budget | < $2.5/day | 1d | $0.05 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [![alt text]({16F93814-9571-477B-A473-7A1B5746478E}.png)]
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L1]

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: openai_tags_error
- [SYMPTOMS_OBSERVED]: Hệ thống bị sập (500) khi cố gắng gửi tags lên OpenAI qua SDK bản cũ.
- [ROOT_CAUSE_PROVED_BY]: Log ghi nhận lỗi `unexpected keyword argument 'langfuse_tags'`.
- [FIX_ACTION]: Sử dụng `langfuse_context.update_current_trace` để nạp dữ liệu thay vì sửa param trực tiếp của SDK.
- [PREVENTIVE_MEASURE]: Áp dụng unit test cho các tham số metadata trước khi deploy.

---

## 5. Individual Contributions & Evidence

### [Đậu Văn Nam]
- [TASKS_COMPLETED]: Viết Middleware xử lý x-request-id; Thiết lập Regex PII (Email, Phone, CCCD); Đảm bảo toàn bộ log có JSON schema chuẩn.
- [![alt text](image-3.png)], ![ ](image-4.png): [app/middleware.py], [app/pii.py]

### [Nguyễn Trí Cao]
- [TASKS_COMPLETED]: Tích hợp Langfuse Tracing; Gắn Contextvars (user_id, model) vào log; Phân tích Cost & Token của từng request qua Dynamic Routing.
- ![alt text](image-5.png): [app/agent.py], [app/metrics.py]
### [Cao Diệu Ly]
- [TASKS_COMPLETED]: Tạo 6 Chart Panel (Latency, Cost, Error...); Viết Alert Rules; Chạy load_test.py để lấy dữ liệu thực tế.
- ![alt text](image.png),![alt text](image-1.png) static/index.html, docs/alerts.md
### [Lê Minh Tuấn]
- [TASKS_COMPLETED]: Chạy validate_logs.py kiểm tra điểm; Phân tích sự cố (Incident Response); Hoàn thiện Report và dẫn dắt Demo.
- ![alt text]({89492C60-118A-4A90-BE85-8ACCF731759C}.png): docs/blueprint-template.md, scripts/trigger_alerts.py

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Dynamic Model Routing (GPT-4o vs Mini) thông minh dựa trên độ phức tạp của câu hỏi, giúp tiết kiệm chi phí tối đa.
- [BONUS_AUDIT_LOGS]: Hệ thống Audit Logs độc lập tại `data/audit.jsonl` chuyên biệt cho việc giám sát bảo mật và tuân thủ PII.
- [BONUS_CUSTOM_METRIC]: Heuristic Quality Score đánh giá chất lượng phản hồi hỗ trợ cho việc thiết lập SLOs chính xác hơn.
