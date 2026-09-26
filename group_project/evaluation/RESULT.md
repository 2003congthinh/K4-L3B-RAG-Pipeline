# RAG evaluation results

## Run information

| Field                              | Value |
| ----------------------------------- | ----- |
| Evaluation date                    | 2026-09-26T03:39:00.415425+00:00 |
| Framework and version              | ragas 0.4.3 |
| Evaluator model                    | gemini / gemini-3.5-flash-lite |
| Generator model                    | gemini / gemini-3.5-flash-lite |
| Embedding model                    | sentence_transformers / BAAI/bge-m3 |
| Corpus version/commit              | ba50684 |
| Golden dataset size                | 20 (18 answerable, 2 out-of-domain) |
| `top_k`                            | 5 |
| Fallback threshold and calibration | SCORE_THRESHOLD = 0.3 (xem src/task9_retrieval_pipeline.py). Ngưỡng này **không được calibrate đúng cho việc phát hiện out-of-domain**: 2 câu out-of-domain trong golden set (gd-19 — lãi suất vay ngân hàng, gd-20 — luật doanh nghiệp Singapore) có best dense score thực đo lần lượt là 0.6387 và 0.6267 — cao hơn threshold gấp đôi, nên PageIndex fallback không bao giờ kích hoạt cho các câu này. Việc hệ thống có vẻ "từ chối" 2 câu này (câu trả lời chứa "không có thông tin cụ thể...") thực chất đến hoàn toàn từ tầng generation (LLM tự nhận thiếu context theo SYSTEM_PROMPT), không phải từ cơ chế fallback retrieval. Ngưỡng 0.3 hiện tại chỉ có tác dụng với case dense-score cực thấp, gần như không lọc được câu ngoài domain trong corpus tiếng Việt pháp lý này (embedding văn bản pháp lý cùng ngôn ngữ luôn có cosine similarity nền khá cao dù lệch chủ đề). |

## Configurations

- **Config A — dense-only:** `retrieve(query, top_k=5, use_reranking=False)` — chỉ dùng `semantic_search()`, bỏ qua BM25 và RRF.
- **Config B — hybrid + RRF:** `retrieve(query, top_k=5, use_reranking=True)` — dense + BM25 gộp bằng RRF (mặc định của hệ thống).

Hai config dùng cùng golden dataset, cùng generator (gemini/gemini-3.5-flash-lite), cùng `SYSTEM_PROMPT`, cùng `top_k` và cùng `SCORE_THRESHOLD`; chỉ khác retrieval strategy.

## Overall scores

(Trung bình trên 18 case có `answerable=true`; 2 case out-of-domain được chấm riêng ở mục Safe refusal bên dưới.)

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      | 0.926 | 0.965 | +0.039 |
| Answer relevance  | 0.910 | 0.925 | +0.016 |
| Context recall    | 0.833 | 0.781 | -0.052 |
| Context precision | 0.883 | 0.893 | +0.010 |
| **Average**       | 0.888 | 0.891 | +0.003 |

## Safe refusal (out-of-domain cases)

| Config | Refusal accuracy trên 2 case out-of-domain |
| ------ | -------------------------------------------------------------------------: |
| A      | 0.000 |
| B      | 0.000 |

## A/B comparison

- **Cấu hình tốt hơn:** Không có cấu hình nào vượt trội rõ rệt trên cả 4 metric — trung bình tổng gần như hoà (+0.003, nằm trong nhiễu đo lường). Config B (hybrid+RRF) tốt hơn ở 3/4 metric generation-side (faithfulness +0.039, answer relevance +0.016, context precision +0.010) — quan trọng với một trợ lý pháp luật vì faithfulness liên quan trực tiếp đến rủi ro bịa nội dung pháp lý. Nhưng Config B đánh đổi bằng context recall giảm rõ nhất trong 4 metric (-0.052). Kết luận: **chọn Config B làm baseline**, nhưng phải xử lý regression context_recall trước khi coi là bản final (xem Recommendations #1).
- **Evidence:** Trong 18 case, RRF gây recall giảm ở đúng 2 case (gd-05: 1.0→0.5, gd-16: 1.0→0.5) và giúp tăng ở 1 case (gd-07: 0.5→1.0), còn lại không đổi. Ở gd-05, RRF (BM25) đẩy `news/article_02.md::chunk-55` và `news/article_01.md::chunk-19` ra khỏi top-5 (có mặt ở Config A) để nhường chỗ cho `legal/so_tay_thue.md::chunk-19` và `legal/phap_luat_ve_ho_kinh_doanh_vn.md::chunk-258` — chunk lexical-match hơn nhưng thiếu thông tin ground truth cần. Ngược lại ở gd-07 (câu hỏi có yếu tố "quy định cũ... quy định mới hơn"), RRF kéo thêm được `news/article_04.md::chunk-45` mà dense-only bỏ lỡ hoàn toàn, giúp recall đạt 1.0.
- **Trade-off về latency/cost:** Số đo thực tế **ngược với giả định ban đầu** — Config B nhanh hơn Config A ở cả mean (22.03s vs 29.80s) lẫn median (18.59s vs 22.96s). Nguyên nhân: latency tổng bị chi phối bởi độ trễ gọi LLM generation (network/API), không phải bởi chi phí tính BM25+RRF (vốn chạy trên CPU, rẻ hơn nhiều bậc so với 1 lần gọi LLM). Config A có 1 outlier nặng ở gd-01 (109.2s) kéo mean lên cao — nhiều khả năng là biến động phía API provider tại thời điểm chạy, không phải đặc trưng hệ thống của dense-only. Kết luận: chi phí BM25+RRF trong pipeline này không đáng kể so với chi phí gọi LLM, latency không phải yếu tố quyết định khi chọn giữa 2 config.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Hộ kinh doanh được sử dụng tối đa bao nhiêu lao động theo qu | B | 1.000 | 0.849 | 0.000 | n/a | retrieval | Context top-5 (`news/article_03.md::chunk-29`, `article_02.md::chunk-45`, `phap_luat...chunk-117/633/545`) chứa đúng thông tin hiện hành ("từ 04/01/2021 không còn giới hạn lao động") NHƯNG các con số lịch sử bị trích dẫn rời rạc, mâu thuẫn giữa nguồn (9 lao động ở 1 đoạn, 10 lao động ở đoạn khác) và không đoạn nào nêu rõ số hiệu nghị định cũ đi kèm con số cụ thể. Nếu ground truth yêu cầu câu trả lời trích đúng văn bản/con số lịch sử, retrieval không đưa được đoạn ghép đủ 2 yếu tố (số lao động + số hiệu nghị định) vào top-5 dù các mảnh thông tin tồn tại rải rác trong corpus — cần đối chiếu `ground_truth` trong `golden_qa.json` để xác nhận chính xác câu nào bị thiếu. |
|   2 | Mã số thuế của hộ kinh doanh được xác định như thế nào? | B | 1.000 | 1.000 | 0.000 | n/a | retrieval | Top-5 (`dia_vi_phap_ly::chunk-230`, `so_tay_thue::chunk-176/3`, `phap_luat...chunk-448`) đều mô tả đúng nội dung cốt lõi (mã số thuế = mã số hộ kinh doanh, do Luật Quản lý thuế 2019 quy định), answer sinh ra khớp nội dung. Recall=0 nhiều khả năng do ground truth trích dẫn cụ thể hơn (vd số điều/khoản của Thông tư hướng dẫn, hoặc định dạng "13 chữ số") mà không đoạn context nào nêu đúng chi tiết đó — cần đối chiếu `ground_truth` để xác nhận câu/chi tiết bị thiếu, đây không phải lỗi "answer sai nội dung" mà là lỗi khớp chi tiết ở mức câu của metric recall. |
|   3 | Theo Nghị định 01/2021/NĐ-CP, hộ kinh doanh được định nghĩa  | B | 1.000 | n/a | 0.500 | n/a | data | Trong 5 context trả về, vị trí 2 và 3 (`legal/phap_luat_ve_ho_kinh_doanh_vn.md::chunk-204` và `::chunk-205`) chứa **văn bản gần như trùng lặp tuyệt đối** ("sử dụng từ Nghị định số 43/2010/NĐ-CP... Theo khoản 1 Điều 79..."). Đây là hệ quả của overlap chunking quá lớn ở task4 (2 chunk liền kề chia sẻ phần lớn nội dung), khiến 1/5 vị trí evidence bị lãng phí cho nội dung trùng thay vì đưa vào 1 đoạn khác biệt (vd đoạn làm rõ khái niệm "hộ gia đình" cũng có trong corpus) — làm giảm recall dù faithfulness vẫn cao vì phần trả lời trùng khớp context đã có. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------- | ---------------- | ------------- |
|        1 | Giảm chunk overlap và/hoặc thêm bước dedupe near-duplicate chunk trước khi index (task4) | gd-01: 2/5 context ở Config B là văn bản trùng gần tuyệt đối (`chunk-204` và `chunk-205`), lãng phí 1 vị trí evidence | Tăng context_recall cho các case có chunk liền kề overlap cao; khả năng ảnh hưởng nhiều hơn 1 case vì đây là vấn đề cấu hình chunking chung, không riêng gd-01 | Chạy lại `python group_project/evaluation/run_evaluation.py` sau khi sửa và so sánh `eval_raw_results.json` |
|        2 | Thêm query decomposition/rewriting cho câu hỏi dạng "trước đây vs hiện tại" hoặc câu cần trích dẫn số liệu/điều khoản cụ thể, hoặc tăng `top_k` khi phát hiện câu hỏi nhiều-phần | gd-04 và gd-14: context_recall = 0.000 ở CẢ 2 CONFIG dù nội dung cốt lõi có mặt trong top-5 — retrieval nhất quán bỏ lỡ chi tiết trích dẫn cụ thể mà ground truth cần | Cải thiện context_recall riêng cho nhóm câu hỏi lịch sử/nhiều-phần, hiện đang là nhóm điểm thấp nhất trong golden set | Chạy lại eval, theo dõi riêng recall của gd-04, gd-14 sau khi đổi query strategy |
|        3 | Hiệu chỉnh lại SCORE_THRESHOLD (nâng ngưỡng hoặc thay bằng cơ chế phát hiện out-of-domain riêng, không dựa vào cosine score) và sửa logic gắn flag `refused` trong script eval để nhận diện refusal theo ngữ nghĩa thay vì so khớp chuỗi cố định | gd-19/gd-20: dense score thật (0.60–0.64) cao hơn threshold 0.3 gấp đôi nên fallback không kích hoạt; đồng thời cả 2 câu model đã trả lời né tránh đúng bằng văn tự nhiên nhưng `refused=False` trong log → refusal_accuracy đo được 0.000 dù hành vi model có vẻ chấp nhận được | Có safety-net thật ở tầng retrieval thay vì phụ thuộc hoàn toàn vào LLM tự kiềm chế; đo refusal_accuracy chính xác hơn, không bị đánh giá thấp giả tạo | Chạy lại eval sau khi chỉnh threshold + sửa detection logic, kiểm tra refusal_accuracy đổi từ 0.000 sang giá trị phản ánh đúng hành vi thật |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | ------------------: | ---------- |
| (chưa chạy) | - | - | - | [DRAFT — điền nếu nhóm làm thêm HyDE/query expansion/reranker nâng cao theo mục Bonus của GRADING_RUBRIC.md] |
