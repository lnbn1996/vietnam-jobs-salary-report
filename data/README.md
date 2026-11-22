# Dữ liệu

## Nguồn (theo trang Kaggle)
| Mục | Thông tin |
|---|---|
| Tên | Vietnam Jobs Dataset |
| Tác giả | nguyen chi tinh (Kaggle: `nguyenchitinh`) |
| Trang | https://www.kaggle.com/datasets/nguyenchitinh/vietnam-jobs-dataset |
| Cập nhật lần cuối | 23/04/2025 (dữ liệu phản ánh thị trường ngày 22/04/2025) |
| Giấy phép ghi trên Kaggle | **MIT** |
| Nội dung | Tin tuyển dụng ở Việt Nam, 11 cột: chức danh, hình thức, cấp bậc, thành phố, kinh nghiệm, kỹ năng, ngành, lương (`salary`, `salary_min`, `salary_max`, `unit`) |

**Trích dẫn gợi ý:** nguyen chi tinh (2025). *Vietnam Jobs Dataset* [bộ dữ liệu]. Kaggle. https://www.kaggle.com/datasets/nguyenchitinh/vietnam-jobs-dataset

## Ghi chú về giấy phép MIT trên Kaggle
- Trang Kaggle ghi giấy phép **MIT** và trỏ tới https://www.mit.edu/~amini/LICENSE.md. Dự án này dùng dữ liệu theo đúng giấy phép mà trang Kaggle công bố và ghi rõ nguồn như trên.
- Văn bản ở link đó là giấy phép MIT chuẩn, chủ bản quyền ghi là "Mark Otto (2013)" và "Andrew Fong (2017)" (kiểm tra ngày 22/11/2026), không phải tên tác giả bộ dữ liệu. Vì vậy nên xem nhãn MIT là điều kiện sử dụng do người đăng chọn, không phải xác nhận quyền đối với dữ liệu gốc của bên thứ ba.
- Trang Kaggle không nêu nguồn thu thập ("Internal data collection, specific source not provided").
- Mô tả trên Kaggle ghi "85k job postings" ở phần tổng quan nhưng "215 rows" ở mục Size; tệp thực tế có 85.470 dòng.
- Mã nguồn của dự án này theo giấy phép MIT riêng (xem `LICENSE` ở thư mục gốc); giấy phép đó không thay đổi điều kiện của dữ liệu.

## Tệp trong thư mục này
- `sample_jobs.csv`: mẫu ngẫu nhiên 1.000 dòng của bộ dữ liệu (đã bỏ dòng trùng, `random_state=42`) để chạy thử mã mà không cần tải tệp lớn.
- `vietnam_jobs_2025.csv` (không đưa lên repo, nằm trong `.gitignore`): tệp đầy đủ 85.470 dòng; tải từ trang Kaggle ở trên (cần đăng nhập), đặt vào thư mục này với đúng tên. Mã tự dùng tệp đầy đủ nếu có, nếu không thì dùng tệp mẫu (khi đó số liệu chỉ mang tính minh họa).

## Quyền riêng tư
Tin tuyển dụng trong tệp không có tên người hay thông tin liên hệ; dữ liệu không chứa thông tin cá nhân.
