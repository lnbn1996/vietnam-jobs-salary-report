# Mức lương trong tin tuyển dụng ở Việt Nam (mini-project: Python sinh báo cáo + dashboard)

Mini-project cho môn Năng lực số nâng cao (CT999), yêu cầu 6 (mini-project nhóm): đọc dữ liệu thực tế, làm sạch, phân tích, tự động sinh báo cáo PDF và dựng dashboard tương tác.

## Mục tiêu
1. Mô tả mức lương đăng tuyển theo cấp bậc, thành phố, kinh nghiệm.
2. Dự đoán lương từ các thông tin trên bằng mô hình hồi quy đơn giản, và nói rõ độ tin cậy.
3. Tự động hóa: một lệnh sinh báo cáo PDF; dashboard cho phép chọn biến, xem biểu đồ, tải dữ liệu đã lọc và báo cáo.

## Dữ liệu
**Vietnam Jobs Dataset**, tác giả nguyen chi tinh, đăng trên Kaggle (cập nhật 23/04/2025): https://www.kaggle.com/datasets/nguyenchitinh/vietnam-jobs-dataset. **Giấy phép ghi trên Kaggle: MIT.** Gồm 85.470 tin tuyển dụng ngày 22/04/2025. Trang Kaggle không nêu nguồn thu thập, nên repo chỉ chứa mẫu 1.000 dòng; xem [data/README.md](data/README.md) để biết trích dẫn, ghi chú về giấy phép và cách tải tệp đầy đủ.

## Phương pháp
- **Làm sạch:** bỏ 40.531 dòng trùng hệt (không có mã tin); phân nhóm cấp bậc, hình thức, thành phố, ngành; đổi kinh nghiệm dạng chữ sang số năm; lương = trung điểm khoảng lương, chỉ dùng tin có đủ cận dưới và cận trên (42.280 tin sau khi bỏ 17 tin trên 200 triệu).
- **Mô hình:** dự đoán log(lương) từ cấp bậc, hình thức, thành phố, ngành, số năm kinh nghiệm, số kỹ năng; chia ngẫu nhiên 80/20; so sánh đường cơ sở (luôn đoán trung vị), hồi quy Ridge và rừng ngẫu nhiên; mức quan trọng của biến tính bằng hoán vị trên tập kiểm tra.

## Kết quả chính
| Mô hình | R² (thang log) | Sai số tuyệt đối TB |
|---|---|---|
| Cơ sở (trung vị) | −0,019 | 5,73 triệu |
| Hồi quy Ridge | 0,341 | 4,68 triệu |
| Rừng ngẫu nhiên | 0,397 | 4,43 triệu |

- Lương trung vị chung 13,5 triệu VND/tháng; tăng rõ theo cấp bậc (nhân viên 13,0 triệu, quản lý 25,0 triệu) và theo kinh nghiệm (không yêu cầu 12,0 triệu, trên 5 năm 25,0 triệu); khác biệt giữa các thành phố nhỏ.
- Số năm kinh nghiệm và cấp bậc là hai biến quan trọng nhất. Mô hình chỉ giải thích khoảng 40% biến thiên, nên chỉ dùng làm mốc tham khảo.
- Hạn chế: lương là mức đăng tuyển, không phải lương thực nhận; tin "thỏa thuận" và tin chỉ có một cận lương không được dùng; nguồn dữ liệu không rõ nên mẫu có thể lệch.

Báo cáo đầy đủ: [results/bao_cao.pdf](results/bao_cao.pdf).

## Cách chạy
```bash
pip install -r requirements.txt
python src/phan_tich.py          # làm sạch, huấn luyện, ghi results/ket_qua.json và biểu đồ
python src/tao_bao_cao.py        # sinh results/bao_cao.pdf
python -m streamlit run src/dashboard.py   # mở dashboard tương tác (dùng "python -m" để khỏi phụ thuộc PATH)
```
Nếu chưa có tệp dữ liệu đầy đủ, mã tự dùng tệp mẫu 1.000 dòng; khi đó số liệu và mô hình khác với báo cáo kèm sẵn trong `results/` (được tạo từ tệp đầy đủ), và các lệnh trên sẽ ghi đè `results/`. Dashboard hiện cảnh báo khi dùng tệp mẫu.

Báo cáo PDF dùng phông Arial (mặc định `C:\Windows\Fonts`); trên hệ điều hành khác đặt biến môi trường `FONT_DIR` tới thư mục chứa `arial.ttf`, `arialbd.ttf`, `ariali.ttf`.

## Cấu trúc
```
data/       README.md (nguồn, giấy phép), sample_jobs.csv (mẫu 1.000 dòng)
src/        common.py (làm sạch, thống kê, biểu đồ), phan_tich.py (mô hình),
            tao_bao_cao.py (PDF), dashboard.py (Streamlit)
results/    bao_cao.pdf, ket_qua.json, bd_*.png
```

## Giấy phép
Mã nguồn theo giấy phép **MIT** (xem [LICENSE](LICENSE)). Dữ liệu dùng theo giấy phép ghi trên trang Kaggle của bộ dữ liệu (MIT); xem [data/README.md](data/README.md) để biết nguồn và ghi chú.

## Công cụ AI
Mã nguồn và báo cáo mẫu được soạn với sự hỗ trợ của Claude (Anthropic); các yêu cầu đã dùng ghi ở [prompts/](prompts/P1_yeu_cau_6.txt); kết quả và nhận định đã được chạy lại và kiểm tra trên dữ liệu.
