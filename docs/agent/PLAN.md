| Khối | Vai trò trong Telesale Call Brief |
|---|---|
| **Perceive** | Chuyển giọng nói thành văn bản, nhận diện ý định và thông tin như nhu cầu, ngân sách, thời điểm mua |
| **Resolve Identity** | Đối chiếu số điện thoại, mã khách hàng hoặc thông tin trong hội thoại với CRM |
| **Retrieve** | Lấy hồ sơ khách hàng, lịch sử cuộc gọi, sản phẩm, chương trình bán hàng và kịch bản tư vấn |
| **Plan** | Quyết định nên hỏi thêm, tư vấn sản phẩm, xử lý phản đối, đặt lịch hay kết thúc cuộc gọi |
| **Guardrail** | Kiểm tra thông tin nhạy cảm, quyền truy cập, quy định tư vấn và nội dung không được cam kết |
| **Act** | Tạo câu trả lời cho telesales hoặc thực hiện hành động như cập nhật CRM, tạo lịch hẹn |
| **Observe** | Nhận kết quả từ CRM/API và phản ứng tiếp theo của khách hàng |
| **Persist** | Lưu tóm tắt, nhu cầu, objections, mức độ tiềm năng, lịch hẹn và next action |


# Future Work
```text
src/telesale_agent/
├── core/                       # 1. LỚP LÕI (Không phụ thuộc vào bất kỳ thư viện bên ngoài nào)
│   ├── models.py               # Domain models, State, Data Classes
│   ├── interfaces.py           # Các Protocol chuẩn (Ports)
│   ├── pipeline.py             # Agent Harness / Vòng lặp chính
│   ├── builder.py              # Builder Pattern để lắp ráp hệ thống
│   └── errors.py               # Các lỗi nghiệp vụ
│
├── adapters/                   # 2. LỚP KẾT NỐI (Thực thi các Interface ở Core)
│   ├── llm/                    # Kết nối AI
│   │   ├── openai_planner.py   # Planner dùng GPT-4
│   │   └── claude_planner.py   # Planner dùng Claude
│   │
│   ├── vector_db/              # RAG & Knowledge Base
│   │   ├── pinecone_retriever.py 
│   │   └── qdrant_retriever.py
│   │
│   ├── database/               # Lưu trữ dữ liệu lâu dài (Persister)
│   │   ├── redis_memory.py     # Lưu Session / State đang chat
│   │   └── postgres_logger.py  # Lưu lịch sử chat vĩnh viễn
│   │
│   ├── crm/                    # Kết nối hệ thống nội bộ doanh nghiệp
│   │   ├── salesforce_api.py   # Lấy thông tin khách hàng (IdentityResolver)
│   │   └── internal_erp.py     # Lấy thông tin tồn kho / đơn hàng
│   │
│   ├── telephony/              # Xử lý Voice / Âm thanh
│   │   ├── twilio_actor.py     # Phát âm thanh qua cuộc gọi
│   │   └── deepgram_perceiver.py # Speech-to-Text
│   │
│   ├── rules/                  # Các rule cứng của doanh nghiệp
│   │   └── business_guardrail.py
│   │
│   └── mock/                   # Dữ liệu giả lập để Dev/Test offline
│
├── entrypoints/                # 3. LỚP ĐẦU VÀO (Cách thế giới bên ngoài gọi vào Core)
│   ├── api/
│   │   ├── fastapi_app.py      # REST API cho Web/App chat
│   │   └── webhooks.py         # Nhận webhook từ Zalo/Facebook/Twilio
│   ├── cli/
│   │   └── console_chat.py     # Chat qua Terminal (giống demo.py)
│   └── workers/
│       └── celery_tasks.py     # Chạy ngầm các task nặng (sinh Call Brief gửi Email)
│
├── prompts/                    # 4. QUẢN LÝ PROMPT (Độc lập với code LLM)
│   ├── system_prompts/         # Các file .txt hoặc .jinja2 định hình nhân vật
│   └── templates/              # Prompt cho từng ngữ cảnh (giá, chính sách)
│
└── config/                     # 5. CẤU HÌNH HỆ THỐNG
    ├── settings.py             # Đọc biến môi trường (Pydantic Settings)
    ├── dev.yaml                # Cấu hình dùng Mock/Local DB
    └── prod.yaml               # Cấu hình dùng API xịn/Cloud DB
```