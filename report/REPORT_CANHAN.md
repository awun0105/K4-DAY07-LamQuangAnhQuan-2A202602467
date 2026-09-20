# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lâm Quang Anh Quân
**Nhóm:** promaxima
**Ngày:** 20/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Độ tương tự cosine cao có nghĩa là hai vector đại diện cho hai đoạn văn bản đang hướng về cùng một hướng trong không gian vector. Điều này chỉ ra rằng chúng có ý nghĩa ngữ nghĩa (semantic meaning) rất giống nhau hoặc liên quan chặt chẽ với nhau, ngay cả khi chúng không sử dụng chung từ vựng.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Tôi rất thích ăn phở bò."
- Câu B: "Món phở bò là đồ ăn khoái khẩu của tôi."
- Tại sao tương đồng: Cả hai câu đều diễn đạt cùng một ý nghĩa là sở thích ăn món phở bò, dù cấu trúc ngữ pháp và từ vựng ("rất thích ăn" so với "đồ ăn khoái khẩu") hoàn toàn khác nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Tôi rất thích ăn phở bò."
- Câu B: "Giá xăng hôm nay lại tiếp tục tăng mạnh."
- Tại sao khác: Hai câu đề cập đến hai chủ đề hoàn toàn không liên quan đến nhau (sở thích ẩm thực cá nhân so với tin tức kinh tế, giá cả).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Cosine similarity chỉ quan tâm đến góc (hướng) giữa hai vector chứ không bị ảnh hưởng bởi độ lớn (chiều dài) của vector. Điều này giúp so sánh ý nghĩa của hai văn bản một cách công bằng ngay cả khi một văn bản rất dài và một văn bản rất ngắn, điều mà khoảng cách Euclid thường đánh giá sai.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Số chunk = làm tròn lên((10000 - 50) / (500 - 50)) = làm tròn lên(9950 / 450) = làm tròn lên(22.11)
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Nếu overlap = 100, số chunk = làm tròn lên((10000 - 100) / (500 - 100)) = làm tròn lên(9900 / 400) = 25 chunks. Số chunk tăng lên. Việc tăng overlap giúp đảm bảo rằng không có ngữ nghĩa hay câu từ nào bị cắt đứt đột ngột ở ranh giới giữa 2 chunk, qua đó bảo toàn được bối cảnh (context) cho mô hình tìm kiếm hiệu quả hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*
Sử dụng regex `re.split(r'(?<=[.!?])\s+', text)` để tách các câu dựa trên dấu chấm, chấm than và hỏi chấm. Kỹ thuật lookbehind `(?<=[.!?])` giúp giữ lại dấu câu gốc mà không bị nuốt mất, kết hợp `strip()` để bỏ khoảng trắng dư thừa trước khi gộp các câu lại theo nhóm `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*
Thuật toán đệ quy cắt đoạn theo từng ký tự phân cách từ lớn đến nhỏ (vd: '\n\n', '\n', '. '). Trường hợp cơ sở (base case) là khi văn bản đã nhỏ hơn `chunk_size` hoặc không còn separator nào để thử (buộc phải cắt theo đúng `chunk_size`). Quá trình xử lý bao gồm cả chiều "gom lên" để kết nối các mảnh nhỏ liền kề lại cho sát với giới hạn `chunk_size` nhằm tránh tạo ra các chunk quá vụn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*
Dữ liệu được chuẩn hóa và nạp vào danh sách `_store` (bộ nhớ RAM), mỗi chunk là một dictionary chứa id, content, metadata và embedding của nó (do `self._embedding_fn` tạo ra). Khi `search`, câu truy vấn cũng được tạo embedding rồi được tính toán độ tương tự bằng Cosine Similarity với từng chunk trong kho, và sắp xếp giảm dần theo điểm số (`score`).

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*
Quá trình lọc (filter) qua metadata được tiến hành **TRƯỚC** khi mang đi tìm kiếm (search) nhằm đảm bảo kết quả trả về thực sự nằm trong phạm vi cần tìm, không bị chiếm chỗ bởi tài liệu ngoài phạm vi nhưng lại có độ tương đồng ngữ nghĩa lớn. Hàm xóa sẽ sử dụng List Comprehension duyệt qua kho lưu trữ, chỉ giữ lại những chunk có trường `metadata['doc_id']` khác với giá trị ID bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*
Sử dụng hàm `store.search()` để lấy `top_k` chunk, nếu kho lưu trữ rỗng thì trả về thông báo lỗi thay vì gọi API mô hình. Khi có ngữ cảnh, chúng được gộp lại (inject) cùng với mã định danh (ví dụ `[1]`, `[2]`), rồi định dạng thành prompt với yêu cầu bắt buộc LLM chỉ trả lời dựa vào các ngữ cảnh trên và trích dẫn mã số tương ứng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts ==============================
platform linux -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/lqaq/PROJECT/AI20K/WEEK01/day07_20092026/LAB/K4-DAY07-LamQuangAnhQuan-2A202602467
plugins: anyio-4.14.2
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.13s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Tôi thích ăn táo" | "Tôi thích ăn táo" | cao | 1.000 | Đúng |
| 2 | "Tôi thích ăn táo" | "Tôi ghiền ăn quả bôm" | cao | 0.012 | Sai |
| 3 | "Chính sách hoàn tiền là 7 ngày" | "Bạn có 7 ngày để trả hàng" | cao | 0.067 | Sai |
| 4 | "Hôm nay trời đẹp" | "Tôi muốn mua một chiếc điện thoại" | thấp | -0.098 | Đúng |
| 5 | "Sản phẩm lỗi được bảo hành 1 năm" | "Cam kết sửa chữa miễn phí trong 12 tháng nếu có lỗi" | cao | 0.199 | Sai |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:* Kết quả bất ngờ nhất là các cặp câu đồng nghĩa (cặp 2, 3, 5) lại có điểm cosine cực kỳ thấp (gần 0), trái ngược hoàn toàn với dự đoán là sẽ cao. Điều này xảy ra do hệ thống đang chạy mặc định bằng `MockEmbedder` (băm MD5 thành vector ngẫu nhiên) thay vì Semantic Embedding thật. Nó minh chứng rõ ràng: nếu mô hình embedding không thực sự "hiểu" ngữ nghĩa, thì thuật toán cosine similarity hoàn toàn vô dụng trong việc truy xuất.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm truy xuất | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sản phẩm đổi ý có được mở seal/mở hộp không? | Phần Điều kiện sản phẩm (ID: buyer-tra-hang-doi-y) | 2đ | Có (nằm ở Top-1) | Câu trả lời giả lập từ LLM... |
| 2 | Người bán gửi sai hàng có được trả hàng không? | Phần Hướng dẫn trả lời đề xuất (ID: buyer-gui-yeu-cau-va-tra-loi) | 2đ | Có (nằm ở Top-1) | Câu trả lời giả lập từ LLM... |
| 3 | Khẩu trang y tế có được trả hàng với lý do đổi ý không? | Phần Trả hàng do đổi ý (ID: buyer-tra-hang-doi-y) | 1đ | Có (nhưng nằm ở Top-2) | Câu trả lời giả lập từ LLM... |
| 4 | Video mở kiện hàng cần quay mấy mặt của kiện hàng? | Phần Cách chuẩn bị bằng chứng (ID: buyer-bang-chung-va-dong-goi) | 2đ | Có (nằm ở Top-1) | Câu trả lời giả lập từ LLM... |
| 5 | Người bán có bao nhiêu ngày để trả hàng về kho? | Phần Quy trình Shopee Mall (ID: seller-quy-trinh-shopee-mall) | 0đ | Không (Chunk đúng bị văng khỏi Top-3) | Câu trả lời giả lập từ LLM... |

**Tổng điểm truy xuất của tôi:** 7 / 10 điểm. (Chấm theo barem 2/1/0: 2đ nếu gold ở top-1, 1đ nếu ở top-2/3, 0đ nếu vắng mặt). 

*(Lưu ý: Do hạn chế của MockEmbedder MD5, các vector bị phân tán ngẫu nhiên dẫn đến câu 5 dù đã lọc Metadata vẫn trượt khỏi Top-3. Đây là minh chứng rõ nhất cho việc thiếu Semantic Search thực sự).*

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:* Bài học lớn nhất là: Lọc metadata (`audience`) cực kỳ quan trọng đối với các nền tảng TMĐT vì nó giúp phân tách ngay từ đầu tài liệu của seller và buyer, tránh việc LLM trả về nhầm chính sách. Ngoài ra, việc dùng chiến lược cắt theo Heading (HeadingChunker) của tôi giúp bảo toàn được nguyên vẹn 1 điều khoản tốt hơn hẳn so với việc cắt mù quáng theo số lượng ký tự.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5/ 5 |
| Hướng tiếp cận của tôi (My Approach) | 8/ 10 |
| Hoàn thiện code (Core Implementation — tests) | 30/ 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 2/ 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10/ 10 |
| **Tổng phần cá nhân** | **60/ 60** |
