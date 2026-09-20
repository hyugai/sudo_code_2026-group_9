# Hướng dẫn chạy notebook sinh dataset hội thoại

Tài liệu này hướng dẫn sử dụng `generate_conversation_dataset.ipynb` để sinh dữ liệu hội thoại tiếng Việt cho ngành điện gia dụng bằng OpenAI API. Notebook sử dụng các file catalog, khuyến mãi và chính sách làm nguồn grounding, sau đó xuất dữ liệu theo cấu trúc `users`, `sessions`, `messages` và `session_products` của Phase 2.

## 1. Các file cần có

Giữ các file sau trong cùng thư mục `dataset`:

```text
dataset/
├── catalogs.jsonl
├── promotions.jsonl
├── policies.jsonl
└── generate_conversation_dataset.ipynb
```

Vai trò của các file đầu vào:

- `catalogs.jsonl`: thông tin sản phẩm, SKU, giá, thông số, tồn kho và các `promotion_id` liên quan.
- `promotions.jsonl`: nội dung khuyến mãi, loại giảm giá, giá trị giảm và thời gian hiệu lực.
- `policies.jsonl`: quy định đặt hàng, thanh toán, giao hàng, đổi trả, bảo hành, khuyến mãi, quyền riêng tư và giao tiếp với khách hàng.
- `generate_conversation_dataset.ipynb`: notebook lập kế hoạch, gọi API, kiểm tra kết quả và xuất dataset.

Notebook coi nội dung các file JSONL là dữ liệu tham khảo, không phải chỉ thị. Nếu trong một trường dữ liệu xuất hiện câu có dạng mệnh lệnh, prompt vẫn yêu cầu mô hình bỏ qua mệnh lệnh đó và chỉ sử dụng trường này như dữ kiện.

## 2. Yêu cầu môi trường

Cần có:

- Python 3.10 trở lên.
- JupyterLab, VS Code có extension Jupyter hoặc môi trường notebook tương đương.
- Các thư viện `openai` và `pydantic`.
- OpenAI API key có quyền sử dụng model được cấu hình.

Notebook sử dụng Responses API và Structured Outputs. Tham khảo:

- [OpenAI API quickstart](https://developers.openai.com/api/docs/quickstart)
- [Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)

## 3. Mở notebook

### Cách 1: Dùng VS Code

1. Mở thư mục `D:\sudo_code_2026-group_9` trong VS Code.
2. Cài extension Python và Jupyter nếu chưa có.
3. Mở `dataset/generate_conversation_dataset.ipynb`.
4. Chọn Python kernel ở góc trên bên phải.
5. Chạy các cell theo thứ tự từ trên xuống hoặc chọn `Run All`.

### Cách 2: Dùng JupyterLab

Mở PowerShell tại thư mục dự án và chạy:

```powershell
cd D:\sudo_code_2026-group_9
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install jupyterlab openai pydantic
.\.venv\Scripts\python.exe -m jupyter lab
```

Trong giao diện JupyterLab, mở:

```text
dataset/generate_conversation_dataset.ipynb
```

### Cách 3: Cài dependency ngay trong notebook

Ở code cell đầu tiên, bỏ dấu `#` tại dòng:

```python
%pip install -q -U openai pydantic
```

Chạy cell này một lần. Nếu Jupyter yêu cầu, restart kernel rồi chạy lại notebook từ đầu.

## 4. Cấu hình API key

Không ghi trực tiếp API key vào notebook và không commit API key vào Git.

### Cách khuyến nghị: nhập ẩn khi notebook yêu cầu

Khi `RUN_GENERATION=True`, nếu chưa có biến môi trường, notebook sẽ hiện:

```text
Nhập OPENAI_API_KEY (được ẩn):
```

Dán API key vào ô nhập. Giá trị sẽ không hiển thị và không được ghi vào file output.

### Cách dùng biến môi trường trong PowerShell

Trước khi mở Jupyter hoặc VS Code từ terminal, chạy:

```powershell
$env:OPENAI_API_KEY = "API_KEY_CUA_BAN"
```

Biến này chỉ có hiệu lực trong phiên PowerShell hiện tại. Sau đó mở Jupyter từ cùng terminal:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

## 5. Chạy dry-run trước

Trong cell `CONFIG`, giữ:

```python
"RUN_GENERATION": False,
```

Chọn `Run All`. Ở chế độ này notebook sẽ:

1. Tìm thư mục chứa ba file JSONL nguồn.
2. Đọc và kiểm tra từng dòng JSONL.
3. Kiểm tra SKU và `promotion_id` có bị trùng hoặc tham chiếu thiếu hay không.
4. Chọn các nhóm kịch bản theo seed.
5. Lập kế hoạch khách đa phiên và đa kênh.
6. Chọn SKU cho từng kịch bản.
7. In số customer journey và số session dự kiến.
8. Không gọi API và không tạo thư mục output.

Ví dụ output của bước lập kế hoạch:

```text
Selected groups:
- [thong_thuong] hoi_va_chot_mua
- [trung_binh] doi_tra_hoac_khieu_nai
- [kho] hoi_ngoai_tai_lieu
Total journeys: 6
Multi-session voice: 2
Multi-channel: 1
Planned sessions: 12
DRY RUN: chưa gọi API và chưa tạo file output.
```

Chỉ chuyển sang chạy thật sau khi các số lượng này đúng với nhu cầu.

## 6. Các tham số cấu hình

Các tham số quan trọng nằm trong dictionary `CONFIG`.

### Số nhóm và số customer journey

```python
"NUM_SCENARIO_GROUPS": 3,
"SCRIPTS_PER_GROUP": 2,
```

- `NUM_SCENARIO_GROUPS`: số nhóm kịch bản được chọn từ `SCENARIO_POOL`.
- `SCRIPTS_PER_GROUP`: số customer journey được sinh trong mỗi nhóm.

Tổng số customer journey và số API request dự kiến:

```text
NUM_SCENARIO_GROUPS × SCRIPTS_PER_GROUP
```

Ví dụ:

```python
"NUM_SCENARIO_GROUPS": 5,
"SCRIPTS_PER_GROUP": 10,
```

Kết quả là 50 customer journey và khoảng 50 API request, vì mỗi journey được sinh bằng một request.

### Số khách đa phiên

```python
"NUM_MULTI_SESSION_CONVERSATIONS": 2,
"MULTI_SESSION_VOICE_RANGE": (2, 3),
```

- `NUM_MULTI_SESSION_CONVERSATIONS`: số khách có ít nhất hai phiên voice.
- `MULTI_SESSION_VOICE_RANGE`: số phiên voice tối thiểu và tối đa của các khách này.

Với `(2, 3)`, mỗi khách đa phiên sẽ có ngẫu nhiên hai hoặc ba cuộc gọi.

### Số khách đa kênh

```python
"NUM_MULTI_CHANNEL_CONVERSATIONS": 1,
"MULTI_CHANNEL_CHAT_RANGE": (1, 2),
```

- `NUM_MULTI_CHANNEL_CONVERSATIONS`: số khách có cả voice và messaging.
- `MULTI_CHANNEL_CHAT_RANGE`: số phiên chat được thêm cho mỗi khách đa kênh.

Các platform messaging có thể là:

- `zalo`
- `facebook_messenger`
- `website_chat`

### Cho phép chồng lấp đa phiên và đa kênh

```python
"OVERLAP_MULTI_SESSION_AND_CHANNEL": True,
```

Khi bằng `True`, một khách có thể đồng thời:

- Có từ hai phiên voice trở lên.
- Có thêm một hoặc nhiều phiên messaging.

Khi bằng `False`, notebook cố gắng chọn hai tập khách riêng biệt. Nếu tổng số khách không đủ để tách hai tập, notebook sẽ báo lỗi cấu hình.

### Model

```python
"MODEL": "gpt-5.6-luna",
```

Có thể thay bằng model khác hỗ trợ Responses API và Structured Outputs nếu project API của bạn không có quyền dùng model mặc định.

### Số message trong mỗi session

```python
"MIN_MESSAGES_PER_SESSION": 8,
"MAX_MESSAGES_PER_SESSION": 14,
```

Mỗi session phải có số lượt thoại nằm trong khoảng trên. Message bắt đầu bằng `customer`, sau đó `customer` và `agent` luân phiên.

### Retry và yêu cầu đúng số lượng

```python
"MAX_RETRIES": 3,
"REQUIRE_EXACT_COUNTS": True,
```

- `MAX_RETRIES`: số lần thử tối đa cho một journey khi API hoặc validation gặp lỗi.
- `REQUIRE_EXACT_COUNTS=True`: nếu còn journey thất bại sau retry, notebook dừng trước bước xuất các file JSONL cuối cùng. Cơ chế này tránh tạo dataset thiếu số lượng mà người dùng không biết.

### Seed

```python
"SEED": 2026,
```

Seed giúp việc chọn nhóm kịch bản, sản phẩm và phân bổ khách đa phiên/đa kênh có tính tái lập. Nội dung do model sinh vẫn có thể khác giữa các lần gọi API.

## 7. Ví dụ cấu hình

### Cấu hình thử nghiệm nhỏ

```python
"NUM_SCENARIO_GROUPS": 3,
"SCRIPTS_PER_GROUP": 2,
"NUM_MULTI_SESSION_CONVERSATIONS": 2,
"NUM_MULTI_CHANNEL_CONVERSATIONS": 1,
```

Kết quả có 6 customer journey.

### Cấu hình 50 customer journey

```python
"NUM_SCENARIO_GROUPS": 5,
"SCRIPTS_PER_GROUP": 10,
"NUM_MULTI_SESSION_CONVERSATIONS": 15,
"NUM_MULTI_CHANNEL_CONVERSATIONS": 8,
```

Kết quả có:

- 50 customer journey.
- 15 khách có nhiều phiên voice.
- 8 khách có cả voice và messaging.

### Cấu hình 120 customer journey

```python
"NUM_SCENARIO_GROUPS": 10,
"SCRIPTS_PER_GROUP": 12,
"NUM_MULTI_SESSION_CONVERSATIONS": 30,
"NUM_MULTI_CHANNEL_CONVERSATIONS": 10,
```

Kết quả có 120 customer journey. Đây không nhất thiết là đúng 120 transcript/session, vì mỗi khách đa phiên hoặc đa kênh tạo thêm session.

### Phân biệt journey và session

- Một `journey` tương ứng một khách hàng và một script tổng thể.
- Một `session` tương ứng một cuộc gọi hoặc một đoạn chat.
- Một journey thông thường có một session voice.
- Journey đa phiên có từ hai đến ba session voice.
- Journey đa kênh có thêm từ một đến hai session messaging.

Do đó:

```text
Tổng sessions >= Tổng journeys
```

Nếu yêu cầu cuộc thi tính số lượng theo transcript hoặc cuộc gọi thay vì số khách hàng, hãy kiểm tra dòng `Planned sessions` trong dry-run trước khi chạy thật.

## 8. Chạy sinh dữ liệu thật

Sau khi kiểm tra dry-run, đổi:

```python
"RUN_GENERATION": True,
```

Sau đó chọn `Restart Kernel and Run All` hoặc chạy lại toàn bộ cell từ đầu.

Quá trình chạy sẽ hiển thị:

```text
[1/50] hoi_va_chot_mua
[2/50] hoi_va_chot_mua
[3/50] so_sanh_gia
...
```

Mỗi journey thành công được ghi ngay vào checkpoint. Nếu validation thất bại, notebook sẽ thử lại và in thời gian chờ:

```text
Retry 1/3 sau 2s: ...
```

Không tắt kernel khi API đang chạy, trừ khi bạn muốn dừng quá trình sinh.

## 9. Thư mục đầu ra

Mỗi lần chạy thật tạo một thư mục timestamp riêng:

```text
dataset/
└── generated_conversations/
    └── run_YYYYMMDDTHHMMSSZ/
        ├── raw_journeys.jsonl
        ├── failed_journeys.jsonl
        ├── users.jsonl
        ├── sessions.jsonl
        ├── messages.jsonl
        ├── session_products.jsonl
        ├── conversation_scripts.jsonl
        └── manifest.json
```

`failed_journeys.jsonl` chỉ xuất hiện nếu có lỗi. Các file chuẩn hóa cuối cùng chỉ được tạo sau khi quá trình sinh hoàn thành và thỏa điều kiện số lượng.

JSONL là định dạng trong đó mỗi dòng là một JSON object hoàn chỉnh. Không nên format toàn bộ JSONL thành một JSON array nếu pipeline tiếp theo cần đọc theo dòng.

## 10. Giải thích từng file đầu ra

### 10.1 `conversation_scripts.jsonl`

Đây là file dễ đọc và đánh giá thủ công nhất. Mỗi dòng chứa toàn bộ customer journey:

```json
{
  "script_id": "SCRIPT_000001",
  "scenario_group_id": "hoi_va_chot_mua",
  "difficulty": "thong_thuong",
  "is_multi_session": true,
  "is_multi_channel": false,
  "user": {},
  "sessions": [],
  "source_policy_ids": [],
  "source_promotion_ids": [],
  "openai_response_id": "resp_..."
}
```

Các trường quan trọng:

- `script_id`: ID của script tổng thể.
- `scenario_group_id`: nhóm kịch bản được áp dụng.
- `difficulty`: `thong_thuong`, `trung_binh` hoặc `kho`.
- `is_multi_session`: khách có ít nhất hai phiên voice hay không.
- `is_multi_channel`: khách có cả voice và messaging hay không.
- `user`: thông tin khách hàng giả lập.
- `sessions`: toàn bộ các phiên và message đã được lồng vào script.
- `source_policy_ids`: các policy được đưa vào grounding.
- `source_promotion_ids`: các promotion được đưa vào grounding.
- `openai_response_id`: ID response của OpenAI, phục vụ audit và debug.

Nên dùng file này để:

- Đọc và chấm chất lượng hội thoại.
- Làm input cho pipeline đánh giá.
- Kiểm tra tính nhất quán đa phiên và đa kênh.
- Xuất dữ liệu cho người không cần làm việc với schema quan hệ.

### 10.2 `users.jsonl`

Mỗi dòng là một khách hàng:

```json
{
  "user_id": "USR_000001",
  "name": "Nguyễn Minh An (giả lập)",
  "phone": "09xx000001",
  "region": "Nam",
  "persona": "khách cân nhắc kỹ",
  "profile": {
    "needs": [],
    "preferences": [],
    "budget_note": "",
    "verified_facts": []
  }
}
```

- `user_id`: khóa chính của khách hàng.
- `name`: tên giả lập, bắt buộc có hậu tố `(giả lập)`.
- `phone`: số điện thoại masked được tạo cục bộ, không phải dữ liệu thật.
- `region`: Bắc, Trung hoặc Nam.
- `persona`: nhóm hành vi chính của khách.
- `profile`: nhu cầu, sở thích, ghi chú ngân sách và dữ kiện đã xác minh.

### 10.3 `sessions.jsonl`

Mỗi dòng là một lần tương tác hoàn chỉnh:

```json
{
  "session_id": "SES_000001_01",
  "user_id": "USR_000001",
  "channel": "voice",
  "platform": "phone",
  "timestamp": "2026-09-20T09:00:00+07:00",
  "summary": "Khách hỏi về sản phẩm và cần xác nhận với gia đình.",
  "outcome": "callback_scheduled"
}
```

- `session_id`: khóa chính của session.
- `user_id`: khóa ngoại đến `users.user_id`.
- `channel`: `voice` hoặc `messaging`.
- `platform`: `phone`, `zalo`, `facebook_messenger` hoặc `website_chat`.
- `timestamp`: thời điểm bắt đầu session.
- `summary`: tóm tắt session dùng như episodic memory.
- `outcome`: kết quả của session.

Các giá trị `outcome`:

- `ongoing`: chưa kết thúc.
- `callback_scheduled`: đã hẹn liên hệ lại.
- `closed_won`: khách chốt mua.
- `rejected`: khách từ chối.
- `resolved`: vấn đề đã được giải quyết.
- `escalated`: cần chuyển bộ phận hoặc nhân sự có thẩm quyền.

Nhiều session có cùng `user_id` thể hiện customer journey đa phiên hoặc đa kênh.

### 10.4 `messages.jsonl`

Mỗi dòng là một lượt thoại:

```json
{
  "message_id": "MSG_000001_01_001",
  "session_id": "SES_000001_01",
  "sender": "customer",
  "type": "voice",
  "text": "Mình muốn hỏi về mẫu nồi cơm này.",
  "sequence_no": 1
}
```

- `message_id`: ID duy nhất của message.
- `session_id`: khóa ngoại đến `sessions.session_id`.
- `sender`: `customer` hoặc `agent`.
- `type`: `voice` cho cuộc gọi, `text` cho nhắn tin.
- `text`: nội dung transcript.
- `sequence_no`: thứ tự message trong session.

Dùng `session_id` và `sequence_no` để tái dựng đúng thứ tự hội thoại.

### 10.5 `session_products.jsonl`

File liên kết session với sản phẩm được thảo luận:

```json
{
  "session_id": "SES_000001_01",
  "product_id": "delites-ncg1805"
}
```

Trong dataset này:

```text
session_products.product_id = catalogs.sku
```

Một session có thể có nhiều dòng trong file này nếu khách so sánh hoặc thảo luận nhiều sản phẩm.

### 10.6 `manifest.json`

File metadata của toàn bộ lần chạy, gồm:

- `run_id`: tên thư mục run.
- `created_at`: thời gian tạo.
- `model`: model đã sử dụng.
- `config`: toàn bộ cấu hình.
- `selected_scenario_groups`: các nhóm kịch bản được chọn.
- `counts`: số record của từng file.
- `failed_journeys`: số journey thất bại.
- `catalog_product_id_mapping`: mô tả ánh xạ `product_id` và `sku`.
- `source_sha256`: SHA-256 của catalog, promotion và policy nguồn.

Dùng `manifest.json` để:

- Xác định dataset được sinh từ cấu hình nào.
- Kiểm tra phiên bản file nguồn.
- So sánh hai lần chạy.
- Lưu bằng chứng tái lập và audit.

### 10.7 `raw_journeys.jsonl`

Đây là checkpoint được ghi ngay sau từng API request thành công. Mỗi dòng chứa:

- `plan`: kế hoạch của customer journey.
- `draft`: Structured Output gốc đã qua Pydantic.
- `source_policy_ids`: policy đã dùng.
- `source_promotion_ids`: promotion đã dùng.
- `openai_response_id`: ID response từ OpenAI.

File này hữu ích khi:

- Notebook bị dừng giữa chừng.
- Cần kiểm tra output trước khi chuẩn hóa.
- Cần truy vết response gây ra lỗi nội dung.
- Cần xây chức năng resume trong tương lai.

`raw_journeys.jsonl` là file audit/checkpoint, không phải lựa chọn tốt nhất để nạp trực tiếp vào database.

### 10.8 `failed_journeys.jsonl`

File chỉ xuất hiện khi một journey vẫn thất bại sau retry:

```json
{
  "plan": {},
  "error": "Loại lỗi và thông báo lỗi"
}
```

Kiểm tra file này để biết:

- Kịch bản nào thất bại.
- SKU và blueprint session liên quan.
- Lỗi API, lỗi Structured Output hoặc lỗi validation.

Khi `REQUIRE_EXACT_COUNTS=True`, notebook không xuất bộ file chuẩn hóa cuối cùng nếu file này có journey thất bại.

## 11. Kiểm tra QA cuối notebook

Sau khi xuất file, notebook kiểm tra:

- Số user bằng số customer journey thành công.
- `user_id`, `session_id` và `message_id` không trùng.
- Mọi session tham chiếu đến user tồn tại.
- Mọi message tham chiếu đến session tồn tại.
- Mọi `product_id` tồn tại trong catalog.
- `sequence_no` liên tục từ 1 trong từng session.
- Voice session chỉ chứa message `type=voice`.
- Messaging session chỉ chứa message `type=text`.
- Số khách đa phiên voice đúng với kế hoạch thành công.
- Số khách đa kênh đúng với kế hoạch thành công.
- Phân bố số script theo nhóm kịch bản.

Ví dụ báo cáo QA:

```json
{
  "users": 6,
  "sessions": 12,
  "messages": 96,
  "session_products": 12,
  "multi_session_voice": 2,
  "multi_channel": 1,
  "scenario_distribution": {
    "hoi_va_chot_mua": 2,
    "doi_tra_hoac_khieu_nai": 2,
    "hoi_ngoai_tai_lieu": 2
  }
}
```

Chỉ nên đưa dataset sang bước tiếp theo khi cell QA chạy xong mà không có assertion error.

## 12. Kiểm tra nhanh file bằng PowerShell

Liệt kê các lần chạy:

```powershell
Get-ChildItem D:\sudo_code_2026-group_9\dataset\generated_conversations
```

Liệt kê file của một run:

```powershell
Get-ChildItem D:\sudo_code_2026-group_9\dataset\generated_conversations\run_YYYYMMDDTHHMMSSZ
```

Đếm số dòng trong từng file JSONL:

```powershell
(Get-Content .\users.jsonl).Count
(Get-Content .\sessions.jsonl).Count
(Get-Content .\messages.jsonl).Count
(Get-Content .\session_products.jsonl).Count
(Get-Content .\conversation_scripts.jsonl).Count
```

Đọc một record:

```powershell
Get-Content .\conversation_scripts.jsonl -TotalCount 1
```

## 13. Cách chọn file cho từng mục đích

| Mục đích | File nên dùng |
|---|---|
| Đọc và chấm hội thoại thủ công | `conversation_scripts.jsonl` |
| Nạp bảng khách hàng | `users.jsonl` |
| Nạp bảng tương tác | `sessions.jsonl` |
| Nạp transcript từng lượt | `messages.jsonl` |
| Liên kết session và catalog | `session_products.jsonl` |
| Audit cấu hình và nguồn | `manifest.json` |
| Debug output gốc của API | `raw_journeys.jsonl` |
| Điều tra journey lỗi | `failed_journeys.jsonl` |

## 14. Lỗi thường gặp

### `ModuleNotFoundError: No module named 'openai'`

Chạy:

```python
%pip install -q -U openai pydantic
```

Sau đó restart kernel.

### Không tìm thấy file JSONL

Đảm bảo ba file sau nằm trong `dataset`:

```text
catalogs.jsonl
promotions.jsonl
policies.jsonl
```

Nên mở notebook từ thư mục dự án hoặc trực tiếp từ thư mục `dataset`.

### Không thấy thư mục output

Kiểm tra:

```python
"RUN_GENERATION": True
```

Khi bằng `False`, notebook chỉ dry-run và không tạo file.

### `model_not_found` hoặc không có quyền truy cập model

Kiểm tra model trong `CONFIG` và quyền của API project. Có thể đổi `MODEL` sang một model khác mà project của bạn được phép sử dụng, với điều kiện model đó hỗ trợ Responses API và Structured Outputs.

### `insufficient_quota`

Kiểm tra usage, billing và giới hạn chi tiêu của OpenAI API project. ChatGPT subscription và OpenAI API billing là các cơ chế riêng.

### Rate limit

Notebook tự retry với thời gian chờ tăng dần. Nếu lỗi vẫn lặp lại:

- Giảm `SCRIPTS_PER_GROUP`.
- Chạy từng batch nhỏ.
- Đợi rate-limit window được làm mới.
- Kiểm tra giới hạn của API project.

### Có `failed_journeys.jsonl` và notebook dừng

Đây là hành vi dự kiến khi:

```python
"REQUIRE_EXACT_COUNTS": True
```

Các bước xử lý:

1. Mở `failed_journeys.jsonl`.
2. Xem trường `error`.
3. Kiểm tra API key, model, rate limit và cấu hình.
4. Chạy lại với cùng `SEED` để giữ kế hoạch phân bổ ổn định.

### Validation báo sai số session hoặc message

Model đã trả kết quả không đúng blueprint sau tất cả retry. Có thể:

- Tăng `MAX_RETRIES`.
- Giảm số session chat hoặc voice trên mỗi journey.
- Giảm độ phức tạp của kịch bản.
- Dùng model mạnh hơn có hỗ trợ Structured Outputs.

## 15. Chi phí và an toàn dữ liệu

- Mỗi customer journey tương ứng khoảng một API request, chưa tính retry.
- Số request cơ sở bằng `NUM_SCENARIO_GROUPS × SCRIPTS_PER_GROUP`.
- Chi phí phụ thuộc model, số token grounding, số session và độ dài hội thoại.
- Nên chạy thử 2 đến 6 journey trước khi sinh hàng trăm mẫu.
- Không đưa API key vào notebook, Git hoặc file output.
- Tên và số điện thoại đầu ra là dữ liệu giả lập hoặc masked.
- Catalog, promotion và policy được gửi đến API làm context cho từng request; không dùng file chứa thông tin bí mật nếu chính sách dự án không cho phép.

## 16. Quy trình khuyến nghị

1. Mở notebook và cài dependency.
2. Giữ `RUN_GENERATION=False`.
3. Chỉnh số nhóm, số script mỗi nhóm, số khách đa phiên và đa kênh.
4. Chạy toàn bộ notebook để xem dry-run.
5. Kiểm tra `Total journeys` và `Planned sessions`.
6. Đổi `RUN_GENERATION=True`.
7. Chạy lại từ đầu và nhập API key khi được hỏi.
8. Chờ notebook hoàn tất.
9. Kiểm tra báo cáo QA.
10. Mở `manifest.json` và `conversation_scripts.jsonl` để kiểm tra thủ công.
11. Chỉ nạp `users`, `sessions`, `messages` và `session_products` vào database sau khi QA đạt.
