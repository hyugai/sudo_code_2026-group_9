# Tóm tắt Dataset Electronics

## 1. Mục đích

Bộ dữ liệu gồm hai phần chính: **base knowledge** dùng làm nguồn sự thật cho agent và **transcript examples** dùng để kiểm thử khả năng ghi nhớ đa phiên, duy trì ngữ cảnh, tuân thủ chính sách, gọi tool đúng và tránh hallucination.

## 2. Base Knowledge

- `knowledge_base_id`: `KB_ELECTRONICS_001`
- Domain: `electronics`
- Ngôn ngữ: `vi-VN`
- Số sản phẩm mẫu: **8**
- Đơn vị tiền tệ: `VND`

### Chính sách chung

- Đặt hàng: hỗ trợ cuộc gọi và trò chuyện; phải xác nhận lại sản phẩm, số lượng, giá cuối, địa chỉ và số điện thoại trước khi tạo đơn.
- Thanh toán: COD, chuyển khoản ngân hàng và thẻ nội địa; COD có giới hạn.
- Giao hàng: có thời gian giao tiêu chuẩn, phí tiêu chuẩn, ngưỡng miễn phí và phụ phí khu vực xa.
- Đổi trả: có thời hạn cho đổi do thay đổi nhu cầu và đổi do lỗi kỹ thuật.
- Bảo hành: tra cứu bằng mã đơn hoặc số sê-ri; một số lỗi sớm có thể đủ điều kiện đổi tương đương sau kiểm tra.
- Khuyến mãi: không tự cộng dồn, không áp dụng mã hết hạn, không tự tạo mức giảm.

### Danh mục sản phẩm mẫu

| ID | Sản phẩm | Nhóm | Giá niêm yết | Tồn kho | Có khuyến mãi |
|---|---|---|---:|---|---|
| `ELEC_001` | Auralite H5 Wireless Headphones | tai nghe không dây | 1,890,000 | còn hàng | Có |
| `ELEC_002` | KeyForge K87 Mechanical Keyboard | bàn phím cơ | 1,490,000 | còn hàng | Không |
| `ELEC_003` | Vector M2 Pro Wireless Mouse | chuột máy tính | 990,000 | sắp hết hàng | Có |
| `ELEC_004` | VoltGo P20 20,000mAh Power Bank | pin sạc dự phòng | 790,000 | còn hàng | Có |
| `ELEC_005` | NovaFit S3 Smartwatch | đồng hồ thông minh | 2,290,000 | còn hàng | Có |
| `ELEC_006` | NetCore AX3000 Wi-Fi 6 Router | bộ định tuyến Wi-Fi | 1,590,000 | còn hàng | Không |
| `ELEC_007` | FlashCore X1 Portable SSD 1TB | ổ SSD di động | 2,190,000 | còn hàng | Có |
| `ELEC_008` | ChargeMax GaN 65W USB-C Charger | bộ sạc USB-C | 690,000 | hết hàng | Không |

### Quy tắc grounding

- Sử dụng product_id làm khóa định danh chuẩn cho sản phẩm.
- Các câu trả lời về giá, tồn kho, khuyến mãi, bảo hành, giao hàng và đổi trả phải dựa trên cơ sở tri thức này.
- Không suy luận tình trạng còn hàng chỉ từ trạng thái sản phẩm; phải sử dụng stock.status và stock.quantity.
- Không áp dụng khuyến mãi đã hết hạn hoặc khuyến mãi có điều kiện khi điều kiện chưa được đáp ứng.
- Nếu thông tin được hỏi không có trong cơ sở tri thức, phải nói rõ rằng chưa có dữ liệu.
- Với khách hàng có nhiều phiên tương tác, sở thích mới nhất được khách hàng xác nhận rõ ràng sẽ thay thế sở thích cũ bị xung đột.

## 3. Transcript Dataset

- `dataset_id`: `TRANSCRIPT_ELECTRONICS_EXAMPLES_001`
- Số scenario mẫu: **10**
- Tổng số session trong các ví dụ: **21**
- Kênh sử dụng: `call` (16), `chat` (5)

### General Format

Mỗi scenario gồm:

- `scenario_id`: định danh scenario.
- `scenario`: nhóm kịch bản nghiệp vụ.
- `edge_case`: loại tình huống kiểm thử.
- `customer`: hồ sơ khách hàng và profile memory.
- `sessions`: chuỗi cuộc gọi/chat theo thời gian.
- `summary`: episodic memory của từng session.
- `facts_established`: các fact mới được xác lập.
- `facts_invalidated`: fact cũ bị thay thế hoặc không còn hiệu lực.
- `benchmark`: cấu hình kiểm thử tự động.

### Benchmark fields

- `must_carry_over`: thông tin bắt buộc phải nhớ sang session sau.
- `must_not_ask`: thông tin agent không được hỏi lại.
- `success_if.tool_called`: tool kỳ vọng nếu scenario cần hành động.
- `success_if.args_match`: tham số tool cần khớp.
- `response_requirements`: yêu cầu hành vi hoặc nội dung phản hồi.
- `ground_truth_facts`: sự thật dùng để kiểm tra hallucination và tính đúng.

## 4. Năm scenario bắt buộc

| Scenario key | Mô tả | Ví dụ bao phủ |
|---|---|---|
| `do_du_hoi_nguoi_nha` | Khách do dự cần hỏi người nhà | `SC-001`, `SC-004` |
| `so_gia` | Khách so giá | `SC-002`, `SC-005` |
| `doi_size_khieu_nai` | Khách đã mua gọi lại đổi size/biến thể hoặc khiếu nại | `SC-003`, `SC-008` |
| `hoi_nhieu_khong_mua` | Khách hỏi nhiều nhưng không mua | `SC-006`, `SC-007`, `SC-009` |
| `goi_lan_3_mat_kien_nhan` | Khách gọi lần 3 và đã mất kiên nhẫn | `SC-010` |

## 5. Edge Cases đang được kiểm thử

- `conflicting_facts`: 1 scenario
- `expired_promo`: 1 scenario
- `mind_change`: 1 scenario
- `normal`: 2 scenario
- `out_of_catalog`: 1 scenario
- `out_of_stock`: 1 scenario
- `post_purchase_complaint`: 1 scenario
- `price_compare`: 1 scenario
- `service_repetition`: 1 scenario

Các edge case nổi bật gồm:

- Khách đổi ý giữa các phiên.
- Fact mới xung đột với fact cũ và cần invalidation.
- Yêu cầu áp dụng khuyến mãi đã hết hạn.
- Hỏi thông tin không tồn tại trong knowledge base.
- Sản phẩm hết hàng nhưng khách vẫn yêu cầu giao ngay hoặc hỏi ngày nhập hàng.
- Khiếu nại sau mua / đổi biến thể.
- Liên hệ lần thứ ba và khách đã mất kiên nhẫn.

## 6. Mối liên kết giữa Base Knowledge và Transcript

Base knowledge là nguồn ground truth cho các thông tin như giá, tồn kho, biến thể, thông số kỹ thuật, khuyến mãi, bảo hành, giao hàng và đổi trả. Transcript sử dụng các fact này để tạo hội thoại và benchmark. Khi đánh giá agent, câu trả lời hoặc tool call phải nhất quán với base knowledge thay vì suy đoán thêm thông tin.

Luồng sử dụng đề xuất:

```text
Base Knowledge
      ↓
Retrieval / Grounding
      ↓
Customer Session
      ↓
Working + Episodic + Profile Memory
      ↓
Next Session
      ↓
Benchmark Evaluation
```

## 7. Mục tiêu đánh giá chính

- Agent nhớ đúng thông tin giữa nhiều session.
- Không hỏi lại các slot đã biết.
- Fact mới thay thế fact cũ khi khách đổi ý.
- Không áp dụng khuyến mãi sai điều kiện hoặc đã hết hạn.
- Không bịa thông tin khi knowledge base không có dữ liệu.
- Không tạo đơn cho sản phẩm hết hàng.
- Gọi đúng tool và truyền đúng tham số khi cần hành động.
- Phản hồi phù hợp với lịch sử tương tác, đặc biệt khi khách đã liên hệ nhiều lần.

## 8. Ghi chú

Toàn bộ sản phẩm, thương hiệu, giá, tồn kho, khuyến mãi và hội thoại trong hai file là dữ liệu giả lập phục vụ phát triển và kiểm thử hệ thống.