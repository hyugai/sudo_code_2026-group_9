# Đặc tả công thức và quy trình đo các metric đánh giá

Tài liệu này chi tiết hóa các metric trong `phase_1.md` để có thể triển khai thành script đánh giá chạy tự động. Các quy ước và công thức M1 bám theo Phụ lục A của đề; phần M2 bổ sung cách tổng hợp và các kiểm tra phụ để tránh diễn giải sai metric.

## 1. Quy ước chung

### 1.1. Đơn vị đánh giá

Ký hiệu:

- $N$: số kịch bản trong bộ test.
- $C_i$: tập các cuộc gọi của kịch bản $i$.
- $Q_i$: tập câu hỏi agent đặt ra trong các phiên được chấm của kịch bản $i$.
- $F_i$: tập fact được khai báo trong `must_carry_over` của kịch bản $i$.
- $K_i$: tập claim nguyên tử, có thể kiểm chứng, mà agent phát ra trong kịch bản $i$.
- $T_i$: tập tool call được đánh giá trong kịch bản $i$.
- $R_i$: tập tài liệu liên quan theo ground truth của truy vấn RAG $i$.
- $L$: tổng số cuộc gọi được đánh giá.
- $\mathbb{1}(x)$: bằng $1$ nếu điều kiện $x$ đúng, ngược lại bằng $0$.

Một **kịch bản** có thể gồm 2-3 cuộc gọi hoặc phiên chat của cùng một khách hàng. Mọi kỳ vọng dùng để chấm phải được khai báo trước khi chạy hệ thống, không được sửa ground truth sau khi đã xem kết quả.

### 1.2. Micro-average và macro-average

Mặc định dùng **micro-average** cho RQR, CCR, HR, WER, CER và Entity Accuracy vì các kịch bản có thể chứa số lượng câu hỏi, fact, claim hoặc token khác nhau:

$$
M_{micro}=\frac{\sum_i \text{số lỗi hoặc số phần tử đạt ở kịch bản }i}
{\sum_i \text{tổng số phần tử hợp lệ ở kịch bản }i}
$$

Ngoài ra nên báo cáo **macro-average** để phát hiện một vài kịch bản dài đang chi phối kết quả:

$$
M_{macro}=\frac{1}{|A|}\sum_{i\in A} M_i
$$

Trong đó $A$ chỉ gồm các kịch bản có metric áp dụng được và có mẫu số lớn hơn 0. Con số chính dùng trong bảng so sánh là micro-average, trừ khi metric quy định khác.

### 1.3. Quy tắc mẫu số bằng 0

- Không tự gán metric bằng 0% hoặc 100% khi mẫu số bằng 0.
- Ghi kết quả là `N/A` và loại phần tử đó khỏi macro-average.
- Luôn in kèm tử số/mẫu số, ví dụ `RQR = 12.5% (5/40)`, để kết quả có thể kiểm tra lại.
- Chỉ làm tròn khi hiển thị; phép tính nội bộ giữ nguyên độ chính xác.

### 1.4. Điều kiện so sánh baseline

Baseline không bộ nhớ và hệ thống có bộ nhớ phải chạy trên:

- cùng bộ test và cùng thứ tự kịch bản;
- cùng model, prompt nghiệp vụ không liên quan đến memory, tham số sinh và tool;
- cùng snapshot catalog, chính sách, tồn kho và khuyến mãi;
- cùng seed nếu nền tảng hỗ trợ.

Khác biệt chủ đích duy nhất là baseline không được nạp thông tin từ phiên trước. Nếu chạy lặp nhiều lần, hai hệ thống phải dùng cùng tập seed.

## 2. Metric M1 bắt buộc

### 2.1. Repeat-Question Rate (RQR)

### Biến và cách gán nhãn

Với mỗi câu hỏi $q\in Q_i$, đặt:

$$
r_{iq}=\begin{cases}
1, & \text{nếu câu hỏi mở yêu cầu lại một slot hợp lệ đã có trước cuộc gọi}\\
0, & \text{nếu không phải câu hỏi thừa}
\end{cases}
$$

Một slot chỉ được coi là đã biết nếu giá trị của nó còn hiệu lực tại thời điểm bắt đầu cuộc gọi. Không tính là hỏi thừa trong ba trường hợp:

- câu hỏi xác nhận, ví dụ “Chị vẫn lấy size L đúng không ạ?”;
- giá trị cũ đã hết TTL hoặc đã bị vô hiệu hóa;
- thông tin thực sự mới, chưa có trong các phiên trước.

### Công thức

RQR cho kịch bản $i$:

$$
RQR_i=\frac{\sum_{q\in Q_i}r_{iq}}{|Q_i|}\times100\%
$$

RQR toàn bộ bộ test:

$$
RQR_{micro}=\frac{\sum_{i=1}^{N}\sum_{q\in Q_i}r_{iq}}
{\sum_{i=1}^{N}|Q_i|}\times100\%
$$

Mức giảm tương đối so với baseline:

$$
\operatorname{RQRReduction}=\frac{RQR_{baseline}-RQR_{system}}
{RQR_{baseline}}\times100\%
$$

Nếu $RQR_{baseline}=0$, mức giảm tương đối là `N/A`; khi đó chỉ báo cáo chênh lệch điểm phần trăm.

### Dữ liệu cần log

- nội dung câu hỏi;
- slot mà câu hỏi nhắm tới;
- kiểu câu hỏi: `open`, `confirmation` hoặc `other`;
- giá trị slot trong memory tại đầu cuộc gọi;
- trạng thái hiệu lực/TTL của giá trị;
- nhãn `is_redundant` và lý do.

### 2.2. Context Carryover Rate (CCR)

Với mỗi fact $f\in F_i$, đặt:

$$
u_{if}=\begin{cases}
1, & \text{fact được sử dụng đúng và đúng lúc}\\
0, & \text{fact bị bỏ sót, dùng sai hoặc dùng không phù hợp}
\end{cases}
$$

Fact được tính là sử dụng đúng khi xuất hiện có ý nghĩa trong lời thoại, quyết định của agent hoặc tham số tool call. Mỗi fact chỉ được tính tối đa một lần; đọc vẹt fact trong câu chào nhưng không phục vụ lượt thoại không được tính.

CCR cho kịch bản $i$:

$$
CCR_i=\frac{\sum_{f\in F_i}u_{if}}{|F_i|}\times100\%
$$

CCR toàn bộ bộ test:

$$
CCR_{micro}=\frac{\sum_{i=1}^{N}\sum_{f\in F_i}u_{if}}
{\sum_{i=1}^{N}|F_i|}\times100\%
$$

### Dữ liệu cần log

- danh sách `must_carry_over` và giá trị kỳ vọng;
- vị trí fact đã được sử dụng: message ID, tool call ID hoặc decision ID;
- nhãn `correct_use`;
- lý do nếu bỏ sót, dùng sai giá trị, dùng fact hết hạn hoặc đặt sai ngữ cảnh.

### 2.3. Task Success Rate (TSR)

TSR phải là tỷ lệ kịch bản **đạt/không đạt**, không lấy trực tiếp điểm chất lượng hội thoại trung bình làm TSR. Mỗi kịch bản $i$ cần khai báo trước tập tiêu chí thành công $G_i$.

Với tiêu chí $g\in G_i$:

- `evaluation_mode = assertion`: kiểm tra bằng code, ví dụ tên tool, tham số, trạng thái đơn hoặc việc không gọi tool;
- `evaluation_mode = llm_judge`: dùng khi tiêu chí mang tính ngữ nghĩa, ví dụ agent có thừa nhận không đủ dữ liệu và đưa fallback an toàn hay không;
- `critical = true`: tiêu chí bắt buộc, trượt tiêu chí này thì cả kịch bản trượt;
- $w_{ig}>0$: trọng số tiêu chí;
- $p_{ig}\in\{0,1\}$: kết quả fail/pass cuối cùng của tiêu chí.

Điểm hoàn thành có trọng số của kịch bản:

$$
Score_i=\frac{\sum_{g\in G_i}w_{ig}p_{ig}}
{\sum_{g\in G_i}w_{ig}}
$$

Biến thành công nhị phân:

$$
s_i=\mathbb{1}\left(
Score_i\ge\tau_i
\land
\prod_{g\in G_i:\ critical(g)}p_{ig}=1
\right)
$$

Trong đó $\tau_i$ phải được khai báo trước. Khuyến nghị dùng $\tau_i=1.0$ khi mọi điều kiện đều bắt buộc; chỉ dùng ngưỡng thấp hơn khi kịch bản có các tiêu chí phụ không critical.

TSR toàn bộ bộ test:

$$
TSR=\frac{\sum_{i=1}^{N}s_i}{N}\times100\%
$$

### TSR bằng LLM-as-a-judge

LLM judge chỉ chấm các tiêu chí `llm_judge`; assertion luôn được ưu tiên khi có thể kiểm tra bằng code. Judge nhận:

1. mô tả mục tiêu và persona của kịch bản;
2. từng tiêu chí cần chấm, không đưa một yêu cầu chung kiểu “cho điểm 1-10”;
3. transcript đầy đủ và thứ tự các phiên;
4. tool trace gồm input, output và lỗi;
5. ground truth/snapshot tài liệu tại thời điểm chạy;
6. hướng dẫn không dùng kiến thức ngoài evidence được cung cấp.

Mỗi tiêu chí ngữ nghĩa phải thuộc một trong các nhóm dưới đây và có điều kiện pass/fail cụ thể theo kịch bản:

| Nhóm tiêu chí TSR | Pass | Fail | Critical mặc định |
|---|---|---|:---:|
| Hoàn thành mục tiêu | Outcome mà khách yêu cầu đã đạt hoặc được xử lý đúng theo `expected_outcome` | Chưa đạt outcome, xử lý nhầm mục tiêu hoặc tự tuyên bố hoàn thành | Có |
| Hành động bắt buộc | Có evidence trực tiếp cho hành động/trạng thái cần thiết | Thiếu hành động, sai đối tượng hoặc sai thời điểm | Có |
| Ràng buộc cấm | Không thực hiện hành vi bị cấm | Có bất kỳ hành vi cấm nào, ví dụ tạo đơn khi chưa được đồng ý | Có |
| Fallback khi thiếu dữ liệu | Thừa nhận giới hạn, không bịa và đưa next action an toàn | Đoán câu trả lời, bế tắc hoặc thực hiện hành động rủi ro | Có ở kịch bản khó |
| Chất lượng giao tiếp hỗ trợ mục tiêu | Phản hồi rõ, phù hợp và giúp tiến tới outcome | Dài dòng hoặc kém tự nhiên nhưng không làm sai outcome | Không |

Judge không được suy luận “có lẽ agent đã làm đúng” nếu không có evidence trong transcript hoặc trace. Khi so sánh baseline với hệ thống, nên ẩn tên biến thể khỏi judge để giảm thiên lệch vị trí hoặc kỳ vọng.

Judge trả về JSON có cấu trúc:

```json
{
  "scenario_id": "SC-07",
  "criteria": [
    {
      "criterion_id": "semantic-safe-fallback",
      "pass": true,
      "evidence_ids": ["msg-18", "tool-04"],
      "reason": "Agent nói rõ chưa có dữ liệu và không tạo đơn."
    }
  ],
  "invalid_input": false
}
```

`evidence_ids` bắt buộc để có thể audit. Trường `reason` chỉ cần giải thích ngắn, không yêu cầu chain-of-thought.

Để giảm độ ngẫu nhiên, chạy judge $R$ lần với $R$ lẻ, nhiệt độ 0 hoặc thấp. Kết quả cuối của tiêu chí là biểu quyết đa số:

$$
p_{ig}=\mathbb{1}\left(\sum_{r=1}^{R}p_{igr}>\frac{R}{2}\right)
$$

Nếu JSON sai schema, thiếu evidence hoặc judge báo `invalid_input`, lần chấm đó không được tự động coi là pass; cần retry có giới hạn rồi đưa vào hàng đợi kiểm tra.

### Dữ liệu cần log

- `success_criteria`, trọng số, `critical`, `evaluation_mode` và $\tau_i$;
- kết quả từng assertion;
- model judge, phiên bản prompt/rubric, temperature và seed;
- kết quả từng lần judge, kết quả majority vote và evidence;
- $Score_i$, $s_i$ và lý do trượt.

### 2.4. Hallucination Rate (HR)

### Đơn vị claim

Một câu có thể chứa nhiều claim. Ví dụ “Sản phẩm giá 4.890.000đ, được tặng bộ lọc và giao trong 2 ngày” gồm ba claim: giá, quà khuyến mãi và thời gian giao hàng.

Judge hoặc bộ tách claim phải tách phát ngôn thành các claim nguyên tử. Với mỗi claim $k\in K_i$, đặt:

$$
v_{ik}=\begin{cases}
1, & \text{claim thuộc phạm vi có thể kiểm chứng bằng nguồn được cung cấp}\\
0, & \text{câu hỏi, xã giao, ý kiến chủ quan hoặc evidence không đủ phạm vi}
\end{cases}
$$

Với claim kiểm chứng được:

$$
h_{ik}=\begin{cases}
1, & \text{claim mâu thuẫn ground truth, hoặc khẳng định điều không có trong nguồn đóng}\\
0, & \text{claim được ground truth hỗ trợ}
\end{cases}
$$

**Nguồn đóng** là nguồn được xác định là đầy đủ cho loại dữ kiện đang xét, ví dụ bảng giá hiện hành cho giá hoặc danh sách khuyến mãi đang hoạt động. Nếu evidence không đầy đủ và không thể kết luận đúng/sai, gán `NOT_VERIFIABLE`, tức $v_{ik}=0$, thay vì tự coi là hallucination.

HR toàn bộ bộ test:

$$
HR=\frac{\sum_{i=1}^{N}\sum_{k\in K_i}v_{ik}h_{ik}}
{\sum_{i=1}^{N}\sum_{k\in K_i}v_{ik}}\times100\%
$$

HR riêng cho giá và khuyến mãi:

$$
HR_{price\_promo}=\frac{
\sum_{i,k}\mathbb{1}(type_{ik}\in\{price,promotion\})v_{ik}h_{ik}}
{\sum_{i,k}\mathbb{1}(type_{ik}\in\{price,promotion\})v_{ik}}
\times100\%
$$

### HR bằng LLM-as-a-judge

Nên chấm theo hai bước để dễ audit:

1. **Claim extraction:** tách claim nguyên tử, giữ nguyên `message_id`, chủ thể, thuộc tính, giá trị và thời điểm.
2. **Claim verification:** đối chiếu từng claim chỉ với ground truth hoặc tool output có timestamp phù hợp.

Các nhãn judge được ánh xạ như sau:

| Nhãn judge | $v$ | $h$ | Diễn giải |
|---|---:|---:|---|
| `SUPPORTED` | 1 | 0 | Evidence hỗ trợ claim. |
| `CONTRADICTED` | 1 | 1 | Evidence cho giá trị khác hoặc phủ định claim. |
| `UNSUPPORTED_CLOSED_WORLD` | 1 | 1 | Nguồn đóng không chứa dữ kiện agent khẳng định. |
| `NOT_VERIFIABLE` | 0 | - | Nguồn không đủ phạm vi để kết luận. |
| `NON_FACTUAL` | 0 | - | Câu hỏi, xã giao hoặc ý kiến chủ quan. |

Judge trả về JSON có cấu trúc:

```json
{
  "claims": [
    {
      "claim_id": "msg-21-c2",
      "message_id": "msg-21",
      "type": "promotion",
      "claim_text": "Đơn này được tặng bộ lọc.",
      "verdict": "CONTRADICTED",
      "evidence_ids": ["promo-snapshot-2026-03-18"],
      "reason": "Khuyến mãi đã hết hạn ngày 2026-03-16."
    }
  ]
}
```

Giá, số lượng, ngày hết hạn, trạng thái tồn kho và mã SKU nên được kiểm tra lại bằng code sau khi judge đã tách claim. Kết quả exact match từ code được ưu tiên hơn kết luận của judge.

Nếu chạy judge $R$ lần, verdict cuối là nhãn có đa số phiếu. Trường hợp hòa hoặc không có đa số được đưa vào hàng đợi kiểm tra, không tự động gán là đúng.

### Dữ liệu cần log

- câu trả lời gốc và `message_id`;
- claim nguyên tử, loại claim và timestamp;
- snapshot ID/version của catalog, pricing, promotion, policy, inventory hoặc tool output;
- verdict, evidence và phương pháp chấm: `exact_rule` hoặc `llm_judge`;
- tử số/mẫu số HR chung và HR giá/khuyến mãi.

### 2.5. WER, CER và Entity Accuracy

Trước khi tính, áp dụng cùng một hàm chuẩn hóa cho ASR output và ground truth. Cần ghi rõ phiên bản hàm chuẩn hóa, ví dụ: Unicode NFC, chuyển thường, chuẩn hóa khoảng trắng, quy tắc dấu câu và quy tắc chuẩn hóa số. Không được chuẩn hóa theo cách làm mất lỗi nghiệp vụ cần đo.

### Word Error Rate

Với toàn bộ corpus gồm $n_{audio}$ file:

$$
WER=\frac{\sum_{a=1}^{n_{audio}}(S_a+D_a+I_a)}
{\sum_{a=1}^{n_{audio}}N_a}\times100\%
$$

Trong đó:

- $S_a$: số từ bị thay;
- $D_a$: số từ bị thiếu;
- $I_a$: số từ bị chèn thêm;
- $N_a$: số từ trong ground truth của audio $a$.

### Character Error Rate

$$
CER=\frac{\sum_{a=1}^{n_{audio}}(S^{char}_a+D^{char}_a+I^{char}_a)}
{\sum_{a=1}^{n_{audio}}N^{char}_a}\times100\%
$$

Nên công bố rõ CER có tính khoảng trắng hay không và giữ quy tắc này cố định giữa các lần chạy.

### Entity Accuracy

Với loại thực thể $e$, đặt $E_e$ là tập thực thể ground truth và `correct(x)=1` khi thực thể được trích xuất đúng hoàn toàn sau chuẩn hóa:

$$
EntityAccuracy_e=\frac{\sum_{x\in E_e}\mathbb{1}(correct(x))}
{|E_e|}\times100\%
$$

Bắt buộc báo cáo riêng ít nhất:

$$
MoneyAccuracy=EntityAccuracy_{money}
$$

$$
PhoneAccuracy=EntityAccuracy_{phone}
$$

Số tiền và số điện thoại dùng exact match sau ITN; không dùng so khớp gần đúng. Nếu hệ thống có thể sinh thêm thực thể không có trong ground truth, nên báo cáo thêm precision/recall thực thể để không bỏ qua false positive.

### 2.6. Số lượt thoại trung bình mỗi kịch bản

Đây là dòng bắt buộc trong bảng so sánh ở Phụ lục A.6 của đề. Chốt trước một **lượt thoại** là một message hoàn chỉnh của khách hoặc agent; tool call được log riêng và không tính là lượt thoại, trừ khi nhóm công bố một quy ước khác.

Gọi $n_i^{turn}$ là số lượt thoại từ đầu đến khi kịch bản $i$ kết thúc:

$$
AverageTurnsPerScenario=\frac{1}{N}\sum_{i=1}^{N}n_i^{turn}
$$

Nên báo cáo thêm median và p95 để một vài cuộc hội thoại bế tắc không bị che bởi số trung bình. Chỉ số thấp hơn chỉ có ý nghĩa khi TSR và các metric an toàn không giảm.

## 3. Metric M2 định lượng

### 3.1. Calls-to-Close (CtC)

Gọi $O$ là tập đơn hàng đã chốt trong cửa sổ đánh giá và $n_o$ là số cuộc gọi từ lần tiếp xúc đầu tiên đến lúc chốt đơn $o$:

$$
CallsToClose=\frac{\sum_{o\in O}n_o}{|O|}
$$

Chỉ số càng thấp càng tốt, nhưng chỉ số này chỉ tính trên các đơn đã chốt và có thể bị survivorship bias. Vì vậy phải báo cáo kèm:

$$
ConversionRate=\frac{\text{số lead chốt được đơn}}
{\text{tổng số lead đủ điều kiện}}\times100\%
$$

Quy định trước cửa sổ quan sát và cách xử lý đơn hủy/hoàn. Không so sánh CtC giữa hai hệ thống nếu conversion rate hoặc cửa sổ quan sát khác nhau đáng kể.

### 3.2. Tool-Call Accuracy (TCA)

Với mỗi tool call thực tế $t\in T_i$, đặt:

$$
c_t=\mathbb{1}(\text{name đúng}\land\text{args đúng}\land\text{state hợp lệ})
$$

Trong đó `args đúng` được kiểm tra theo schema và ground truth; `state hợp lệ` kiểm tra điều kiện nghiệp vụ, ví dụ chỉ gọi `order.create` khi đã có sự đồng ý của khách.

$$
ToolCallAccuracy=\frac{\sum_i\sum_{t\in T_i}c_t}
{\sum_i|T_i|}\times100\%
$$

TCA không phạt trường hợp agent bỏ sót một tool call bắt buộc vì mẫu số chỉ chứa tool đã gọi. Do đó nên báo cáo thêm:

$$
RequiredToolRecall=\frac{\text{số tool call bắt buộc đã gọi đúng}}
{\text{tổng số tool call bắt buộc theo ground truth}}\times100\%
$$

Và phân rã lỗi thành `wrong_tool`, `missing_arg`, `wrong_arg`, `invalid_state`, `duplicate_call`, `forbidden_call`, `missing_call`.

### 3.3. Recall@k của RAG

Với truy vấn $i$, gọi $TopK_i$ là tập tài liệu/đoạn được retrieval trả về trong $k$ vị trí đầu:

$$
Recall@k_i=\frac{|TopK_i\cap R_i|}{|R_i|}
$$

Toàn bộ tập truy vấn dùng macro-average:

$$
Recall@k=\frac{1}{|A|}\sum_{i\in A}Recall@k_i
$$

Trong đó $A=\{i:|R_i|>0\}$. Phải chốt trước đơn vị relevance là document hay chunk và cố định $k$. Với truy vấn chỉ có một đáp án liên quan, có thể báo cáo thêm:

$$
Hit@k=\frac{1}{|A|}\sum_{i\in A}\mathbb{1}(TopK_i\cap R_i\ne\varnothing)
$$

### 3.4. Độ trễ p50/p95

Với $m$ quan sát độ trễ hợp lệ $x_1,\ldots,x_m$, sắp xếp tăng dần thành $x_{(1)}\le\cdots\le x_{(m)}$. Dùng nearest-rank:

$$
p_q=x_{(\lceil q\cdot m\rceil)}
$$

Do đó:

$$
p50=x_{(\lceil0.50m\rceil)},\qquad
p95=x_{(\lceil0.95m\rceil)}
$$

Đo và báo cáo riêng:

- `call_brief_latency = brief_ready_at - call_start_at`;
- `TTFT = first_text_token_at - request_sent_at`;
- `TTFA = first_audio_frame_at - user_end_of_speech_at`;
- `total_turn_latency = response_complete_at - user_turn_complete_at`;
- thời gian từng tool và thời gian retry.

Không trộn chat, voice và xử lý audio offline vào cùng một phân phối. Timeout phải được báo cáo bằng `timeout_rate`; không được âm thầm loại timeout để p95 đẹp hơn.

Các ngưỡng hiệu năng trong đề:

- M1: Call Brief $\le5$ giây, chat TTFT p95 $\le3$ giây, Total Latency p95 $\le8$ giây;
- M2: Call Brief $\le3$ giây, voice TTFA p95 $\le2.5$ giây.

### 3.5. Chi phí ước tính mỗi cuộc gọi

Với cuộc gọi $l$:

$$
Cost_l=Cost^{LLM}_l+Cost^{ASR}_l+Cost^{TTS}_l+
Cost^{tool}_l+Cost^{retrieval}_l+Cost^{storage}_l
$$

Chi phí LLM:

$$
Cost^{LLM}_l=\sum_{r\in Requests(l)}
\left(
\frac{Tok^{in}_r}{10^6}P^{in}_{model(r)}+
\frac{Tok^{out}_r}{10^6}P^{out}_{model(r)}
\right)
$$

Chi phí trung bình:

$$
AverageCostPerCall=\frac{\sum_{l=1}^{L}Cost_l}{L}
$$

Nên báo cáo thêm p50/p95 cost. Bảng giá phải được lưu cùng timestamp/currency; với tool mock có chi phí bằng 0 vẫn cần ghi rõ giả định.

## 4. Metric rubric chấm bằng LLM-as-a-judge

Các metric MWQ, Handoff Brief Actionability, OHQ, VIQ, FRQ và PIBQ dùng rubric 0-3 đã định nghĩa trong `phase_1.md`.

Với metric $m$, gọi $A_m$ là tập mẫu mà metric áp dụng và $z_{im}\in\{0,1,2,3\}$ là trung vị điểm của các lần judge. Với thang thứ bậc 0-3, median ổn định hơn majority vote khi các lần chạy cho ba mức điểm khác nhau.

Điểm trung bình thang 0-3:

$$
MeanScore_m=\frac{\sum_{i\in A_m}z_{im}}{|A_m|}
$$

Điểm chuẩn hóa thang 0-100:

$$
NormalizedScore_m=\frac{\sum_{i\in A_m}z_{im}}
{3|A_m|}\times100
$$

Tỷ lệ đạt ngưỡng $\tau_m$:

$$
PassRate_m=\frac{\sum_{i\in A_m}\mathbb{1}(z_{im}\ge\tau_m)}
{|A_m|}\times100\%
$$

Khuyến nghị khai báo $\tau_m=2$ trước khi chạy, tức đáp ứng yêu cầu ở mức sử dụng được. Ngưỡng này là quy ước nội bộ, không phải ngưỡng bắt buộc của đề.

| Metric | Đơn vị chấm | Mẫu áp dụng | Kiểm tra phụ nên báo cáo |
|---|---|---|---|
| Memory Write Quality (MWQ) | Một lần ghi memory sau cuộc gọi | Mọi cuộc gọi có fact cần ghi/cập nhật/xóa | Tỷ lệ ghi sai khách, xung đột active, thiếu provenance/TTL |
| Handoff Brief Actionability | Một handoff brief | Ca chuyển AI-người, người-người hoặc chuyển ca | Tỷ lệ thiếu sản phẩm, blocker, cam kết hoặc next action |
| Objection Handling Quality (OHQ) | Một lần xử lý phản đối | Lượt có objection được gán nhãn | Điểm theo loại objection/persona |
| Vietnamese Interaction Quality (VIQ) | Một cuộc gọi/phiên | Mọi mẫu tiếng Việt | Điểm theo vùng miền, chat/voice và mức nhiễu |
| Failure Recovery Quality (FRQ) | Một sự cố được inject | Tool timeout, ASR rác, JSON lỗi, retrieval rỗng | Tỷ lệ fallback an toàn và tỷ lệ handoff thành công |
| Privacy & Identity Boundary Quality (PIBQ) | Một tình huống truy cập dữ liệu/nhận diện | Số lạ, số dùng chung, chưa xác minh danh tính | Tỷ lệ rò rỉ PII và tỷ lệ tiết lộ quá mức |

Với metric an toàn, điểm trung bình không được che khuất lỗi nghiêm trọng. Báo cáo thêm:

$$
CriticalFailureRate_m=\frac{\text{số mẫu có lỗi critical}}
{|A_m|}\times100\%
$$

Ví dụ lỗi critical: ghi memory nhầm khách, tạo đơn khi khách chưa đồng ý, tiết lộ PII của người khác hoặc tiếp tục cam kết chính sách sau khi tool báo lỗi.

### Cấu trúc output chung của judge rubric

```json
{
  "sample_id": "SC-07-call-2",
  "metric": "MWQ",
  "applicable": true,
  "score": 2,
  "evidence_ids": ["memory-write-03", "msg-27"],
  "violations": ["missing_provenance"],
  "critical_failure": false,
  "reason": "Fact đúng và hữu ích nhưng thiếu nguồn phiên."
}
```

Judge phải chọn một trong bốn mức rubric, trích evidence và gắn loại vi phạm; không được chấm chỉ dựa trên văn phong chung.

## 5. Đối chiếu LLM judge với người

Theo đề, cần chấm tay ít nhất 20 mẫu. Nên lấy mẫu phân tầng theo persona, loại lỗi, kịch bản dễ/khó và cả kết quả pass/fail; không chỉ lấy các ca thành công.

### 5.1. Tỷ lệ đồng thuận chính xác

Với $M$ nhãn được cả người và LLM chấm:

$$
ExactAgreement=\frac{1}{M}\sum_{j=1}^{M}
\mathbb{1}(y^{human}_j=y^{judge}_j)\times100\%
$$

Áp dụng trực tiếp cho TSR pass/fail, verdict HR và điểm rubric 0-3.

### 5.2. Cohen's kappa

Để loại ảnh hưởng của đồng thuận do ngẫu nhiên:

$$
\kappa=\frac{p_o-p_e}{1-p_e}
$$

Trong đó $p_o$ là tỷ lệ đồng thuận quan sát được và $p_e$ là tỷ lệ đồng thuận kỳ vọng từ phân phối nhãn biên. Với rubric 0-3 nên dùng weighted Cohen's kappa; với pass/fail dùng kappa không trọng số.

### 5.3. Precision/Recall/F1 cho phát hiện hallucination

Lấy nhãn người làm tham chiếu và coi hallucination là lớp dương:

$$
Precision_H=\frac{TP}{TP+FP}
$$

$$
Recall_H=\frac{TP}{TP+FN}
$$

$$
F1_H=\frac{2\cdot Precision_H\cdot Recall_H}
{Precision_H+Recall_H}
$$

Các chỉ số này phải tính ở cấp **claim**, không phải cấp lượt thoại. Ngoài verdict, cần kiểm tra riêng độ đầy đủ của bước claim extraction; nếu judge bỏ sót claim thì đó là false negative.

Ngưỡng kiểm soát nội bộ có thể đặt trước, ví dụ `ExactAgreement >= 80%` và `kappa >= 0.60`. Đây là gate vận hành do nhóm chọn, không phải ngưỡng chính thức của đề. Nếu không đạt, sửa rubric/prompt hoặc tăng tỷ lệ human review trước khi dùng judge cho toàn bộ bộ test.

## 6. Chênh lệch giữa baseline và hệ thống

Với metric càng cao càng tốt như CCR, TSR, Entity Accuracy, Tool-Call Accuracy và Recall@k:

$$
\Delta_{pp}=M_{system}-M_{baseline}
$$

$$
RelativeImprovement=\frac{M_{system}-M_{baseline}}
{M_{baseline}}\times100\%
$$

Với metric càng thấp càng tốt như RQR, HR, WER, CER, CtC, latency và cost:

$$
\Delta_{pp}=M_{baseline}-M_{system}
$$

$$
RelativeReduction=\frac{M_{baseline}-M_{system}}
{M_{baseline}}\times100\%
$$

Với metric có đơn vị phần trăm, $\Delta_{pp}$ được đọc là **điểm phần trăm**, không phải phần trăm tương đối. Nếu mẫu số baseline bằng 0, relative improvement/reduction là `N/A`.

Ngưỡng từ đề cần kiểm tra tự động:

- $RQR\ Reduction\ge40\%$;
- $TSR\ge70\%$;
- $HR_{price\_promo}\le5\%$.

## 7. Schema tối thiểu để áp dụng công thức

Mỗi kịch bản nên có cấu trúc tương đương:

```json
{
  "scenario_id": "SC-07",
  "persona": "khach_do_du_hoi_nguoi_nha",
  "calls": [
    {
      "call_id": "SC-07-C2",
      "must_not_ask": ["room_area_m2", "budget_vnd"],
      "must_carry_over": [
        {
          "fact_id": "product_advised",
          "expected_value": "SKU-AP-X",
          "valid_at": "2026-03-14T10:00:00+07:00"
        }
      ],
      "success_criteria": [
        {
          "criterion_id": "create-correct-order",
          "evaluation_mode": "assertion",
          "critical": true,
          "weight": 1,
          "expected": {
            "tool": "order.create",
            "args": {"sku": "SKU-AP-X", "price_vnd": 4890000}
          }
        },
        {
          "criterion_id": "natural-confirmation",
          "evaluation_mode": "llm_judge",
          "critical": false,
          "weight": 0.25,
          "rubric": "Xác nhận ý định hiện tại, không hỏi mở lại toàn bộ nhu cầu."
        }
      ],
      "success_threshold": 0.8,
      "ground_truth": {
        "snapshot_id": "catalog-policy-2026-03-14T10:00+07:00",
        "facts": {
          "price_vnd": 4890000,
          "promo_active": true,
          "in_stock": true,
          "delivery_days": 2
        },
        "closed_world_fields": [
          "price_vnd",
          "promo_active",
          "in_stock",
          "delivery_days"
        ]
      },
      "expected_tools": [
        {
          "tool": "order.create",
          "required": true,
          "args": {"sku": "SKU-AP-X", "price_vnd": 4890000}
        }
      ],
      "rag_relevant_ids": ["policy-return-03"]
    }
  ]
}
```

Trong ví dụ, criterion critical có trọng số 1 và criterion phụ có trọng số 0.25. Vì vậy `success_threshold = 0.8` cho phép kịch bản đạt khi criterion critical pass nhưng criterion phụ fail. Nếu criterion phụ chỉ dùng để phân tích và hoàn toàn không được tác động tới TSR, loại nó khỏi `success_criteria` của TSR.

## 8. Thứ tự tính trong script đánh giá

1. Kiểm tra schema của test set và bảo đảm mọi kỳ vọng đã được khai báo.
2. Chạy baseline và hệ thống trên cùng snapshot và seed.
3. Lưu transcript, memory snapshot, tool trace, retrieval trace, latency và token usage.
4. Chạy exact rules/assertions trước.
5. Chạy LLM judge cho tiêu chí ngữ nghĩa của TSR, claim extraction/verification của HR và rubric M2.
6. Kiểm tra schema output của judge, chạy exact override cho số, giá, ngày, SKU và trạng thái.
7. Tính metric từng kịch bản, sau đó tính micro/macro aggregate.
8. Tính chênh lệch baseline, ba ngưỡng bắt buộc và khoảng tin cậy nếu chạy lặp.
9. In cả tỷ lệ lẫn tử số/mẫu số; xuất file machine-readable để tái lập báo cáo.

## 9. Bảng kết quả đề xuất

| Metric | Baseline | Hệ thống | Chênh lệch | Tử số/Mẫu số | Ngưỡng | Đạt? |
|---|---:|---:|---:|---:|---:|:---:|
| RQR | ... | ... | giảm ...% | .../... | giảm tương đối $\ge40\%$ | ... |
| CCR | ... | ... | ... pp | .../... | tự đặt | ... |
| TSR | ... | ... | ... pp | .../... kịch bản | $\ge70\%$ | ... |
| HR tổng | ... | ... | ... pp | .../... claim | tự đặt | ... |
| HR giá & khuyến mãi | ... | ... | ... pp | .../... claim | $\le5\%$ | ... |
| WER | ... | ... | ... pp | .../... token | tự đặt | ... |
| CER | ... | ... | ... pp | .../... ký tự | tự đặt | ... |
| Money Accuracy | ... | ... | ... pp | .../... entity | tự đặt | ... |
| Phone Accuracy | ... | ... | ... pp | .../... entity | tự đặt | ... |
| Average Turns/Scenario | ... | ... | ... turn | ... kịch bản | tự đặt | ... |
| Calls-to-Close | ... | ... | ... call | ... đơn | tự đặt | ... |
| Tool-Call Accuracy | ... | ... | ... pp | .../... call | tự đặt | ... |
| Required Tool Recall | ... | ... | ... pp | .../... call | tự đặt | ... |
| Recall@k | ... | ... | ... pp | ... truy vấn | tự đặt | ... |
| Total latency p50/p95 | ... | ... | ... ms | ... lượt | theo M1/M2 | ... |
| Average Cost per Call | ... | ... | ... VND/USD | ... call | tự đặt | ... |

Đối với MWQ, Handoff Brief Actionability, OHQ, VIQ, FRQ và PIBQ, thêm các cột `MeanScore (0-3)`, `NormalizedScore`, `PassRate`, `CriticalFailureRate` và số mẫu áp dụng.
