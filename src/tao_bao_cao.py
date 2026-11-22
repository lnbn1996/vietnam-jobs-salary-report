"""Sinh báo cáo PDF tự động (giới thiệu, mô tả dữ liệu, kết quả, biểu đồ, kết luận và đề xuất).

Chạy:  python src/tao_bao_cao.py            # báo cáo toàn bộ -> results/bao_cao.pdf
Hàm build_pdf() cũng được dashboard gọi để xuất báo cáo cho phần dữ liệu đã lọc.
Mọi số liệu trong báo cáo đều tính từ dữ liệu khi chạy; câu chữ là mẫu cố định.
"""
import json
import os
import sys
import tempfile

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Table, TableStyle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

FONT_DIR = os.environ.get("FONT_DIR", r"C:\Windows\Fonts")
vn = C.vn


def nap_font():
    for ten, tep in [("Arial", "arial.ttf"), ("Arial-B", "arialbd.ttf"), ("Arial-I", "ariali.ttf")]:
        if ten not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(ten, os.path.join(FONT_DIR, tep)))
    pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-B", italic="Arial-I",
                                  boldItalic="Arial-B")


def _bang(hang, rong):
    cell = ParagraphStyle("cell", fontName="Arial", fontSize=9.5, leading=12)
    t = Table([[Paragraph(str(c), cell) for c in r] for r in hang], colWidths=rong, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE8F5")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F9FC")]),
    ]))
    return t


def build_pdf(df, lam_sach, mo_hinh, duong_ra, mo_ta_loc=None):
    """df: dữ liệu đã làm sạch (có thể đã lọc). lam_sach, mo_hinh: dict từ phan_tich.py."""
    truoc = C.dat_che_do_toi(False)   # báo cáo PDF luôn dùng nền sáng, kể cả khi gọi từ dashboard tối
    try:
        _build_pdf(df, lam_sach, mo_hinh, duong_ra, mo_ta_loc)
    finally:
        C.dat_che_do_toi(truoc)


def _build_pdf(df, lam_sach, mo_hinh, duong_ra, mo_ta_loc):
    nap_font()
    tk = C.thong_ke(df)
    tmp = tempfile.mkdtemp()
    hinh = {
        "cap_bac": C.luu_hinh(C.ve_cot(tk["cap_bac"], "Cấp bậc", ngang=True), "a.png", tmp),
        "thanh_pho": C.luu_hinh(C.ve_cot(tk["thanh_pho"], "Thành phố", xoay=25), "b.png", tmp),
        "kinh_nghiem": C.luu_hinh(C.ve_cot(tk["kinh_nghiem"], "Kinh nghiệm yêu cầu", xoay=15), "c.png", tmp),
    }
    td = ParagraphStyle("td", fontName="Arial-B", fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=4)
    ph = ParagraphStyle("ph", fontName="Arial-I", fontSize=10.5, leading=14, alignment=TA_CENTER,
                        textColor=colors.HexColor("#555555"), spaceAfter=10)
    h = ParagraphStyle("h", fontName="Arial-B", fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=5,
                       textColor=colors.HexColor(C.XANH))
    p = ParagraphStyle("p", fontName="Arial", fontSize=10.5, leading=14.5, alignment=TA_JUSTIFY, spaceAfter=4)
    cap = ParagraphStyle("cap", parent=p, fontName="Arial-I", fontSize=9.5, alignment=TA_CENTER, spaceAfter=6)

    n0 = lambda x: vn(x, 0)
    S = [Paragraph("Báo cáo tự động: mức lương trong tin tuyển dụng ở Việt Nam", td),
         Paragraph("Sinh tự động bằng Python (pandas, scikit-learn, matplotlib, reportlab)", ph)]

    S += [Paragraph("1. Giới thiệu đề tài", h), Paragraph(
        "Mức lương là thông tin được người tìm việc quan tâm nhất nhưng thường khác nhau nhiều giữa "
        "cấp bậc, thành phố và ngành. Báo cáo dùng tin tuyển dụng công khai để trả lời hai câu hỏi: "
        "(1) lương được đăng khác nhau thế nào theo cấp bậc, thành phố, kinh nghiệm; "
        "(2) có thể dự đoán lương đăng tuyển từ các thông tin đó ở mức độ nào.", p)]
    if mo_ta_loc:
        S.append(Paragraph(f"<b>Phạm vi báo cáo:</b> {mo_ta_loc}", p))

    S += [Paragraph("2. Mô tả dữ liệu", h), Paragraph(
        f"Dữ liệu là Vietnam Jobs Dataset (tác giả nguyen chi tinh, Kaggle, cập nhật 23/04/2025; "
        f"https://www.kaggle.com/datasets/nguyenchitinh/vietnam-jobs-dataset; giấy phép ghi trên Kaggle: MIT), "
        f"gồm {n0(lam_sach['n_goc'])} tin ngày 22/04/2025 với 11 cột: chức danh, hình thức, cấp bậc, "
        f"thành phố, kinh nghiệm, kỹ năng, ngành và lương. Trang Kaggle không nêu nguồn thu thập. "
        f"Làm sạch: bỏ {n0(lam_sach['n_trung'])} dòng trùng hệt (không có mã tin nên coi là đăng lặp), "
        f"còn {n0(lam_sach['n_sau'])} tin. Chỉ tin có <i>khoảng lương</i> đầy đủ cận dưới và cận trên "
        f"được dùng để phân tích lương ({n0(lam_sach['n_khoang'])} tin; lương = trung điểm khoảng, đơn vị "
        f"triệu VND/tháng); {n0(lam_sach['n_mot_can'])} tin chỉ có một cận (ví dụ \"từ 12 triệu\") và "
        f"{lam_sach['n_qua_cao']} tin trên {C.MAX_LUONG} triệu bị loại. Phần dữ liệu trong báo cáo này có "
        f"{n0(tk['n_tin'])} tin, trong đó {n0(tk['n_co_luong'])} tin có khoảng lương.", p)]

    S.append(Paragraph("3. Kết quả phân tích", h))
    if tk["n_co_luong"] == 0:
        S.append(Paragraph("Không có tin nào có khoảng lương trong phạm vi đã chọn.", p))
        _dung(S, duong_ra)
        return
    hang = [["Cấp bậc", "Số tin", "Lương trung vị", "Q1–Q3"]]
    for k, r in tk["cap_bac"].iterrows():
        hang.append([k, n0(r["n"]), vn(r["tv"]), f"{vn(r['q1'])}–{vn(r['q3'])}"])
    S.append(KeepTogether([_bang(hang, [6 * cm, 2.6 * cm, 3.6 * cm, 3.6 * cm]),
          Paragraph("Bảng 1. Lương theo cấp bậc (triệu VND/tháng; chỉ nhóm có từ 30 tin).", cap)]))
    hang = [["Thành phố", "Số tin có lương", "Lương trung vị", "Q1–Q3"]]
    for k, r in tk["thanh_pho"].iterrows():
        hang.append([k, n0(r["n"]), vn(r["tv"]), f"{vn(r['q1'])}–{vn(r['q3'])}"])
    S.append(KeepTogether([_bang(hang, [6 * cm, 3.2 * cm, 3.2 * cm, 3.4 * cm]),
          Paragraph("Bảng 2. Lương theo thành phố (triệu VND/tháng).", cap)]))

    kq = mo_hinh["ket_qua"]
    hang = [["Mô hình", "R² (thang log)", "Sai số tuyệt đối TB (triệu VND)"]]
    for ten, r in kq.items():
        hang.append([ten, vn(r["r2_log"], 3), vn(r["mae_trieu"], 2)])
    S.append(KeepTogether([_bang(hang, [6.4 * cm, 3.6 * cm, 5.6 * cm]),
          Paragraph(f"Bảng 3. Dự đoán lương trên tập kiểm tra ({n0(mo_hinh['n_test'])} tin, chia ngẫu nhiên "
                    f"80/20; mô hình huấn luyện trên toàn bộ dữ liệu, không phụ thuộc bộ lọc).", cap)]))

    S.append(Paragraph("4. Biểu đồ minh họa", h))
    for k, c in [("cap_bac", "Hình 1. Lương trung vị theo cấp bậc."),
                 ("thanh_pho", "Hình 2. Lương trung vị theo thành phố."),
                 ("kinh_nghiem", "Hình 3. Lương trung vị theo kinh nghiệm yêu cầu.")]:
        S += [Image(hinh[k], width=13.5 * cm, height=6.75 * cm), Paragraph(c, cap)]
    qt = os.path.join(C.RESULTS, "bd_quan_trong.png")
    if os.path.exists(qt):
        S += [Image(qt, width=13.5 * cm, height=6.1 * cm),
              Paragraph("Hình 4. Mức quan trọng của từng biến trong mô hình rừng ngẫu nhiên "
                        "(hoán vị trên tập kiểm tra).", cap)]

    # Kết luận: số liệu lấy từ dữ liệu
    cb, kn, tp = tk["cap_bac"], tk["kinh_nghiem"], tk["thanh_pho"]
    y = [f"• Lương trung vị chung là {vn(tk['luong_tv'])} triệu VND/tháng (trung bình {vn(tk['luong_tb'])})."]
    if len(cb) >= 2:
        y.append(f"• Cấp bậc khác nhau rõ: {cb['tv'].idxmax()} có trung vị {vn(cb['tv'].max())} triệu, "
                 f"{cb['tv'].idxmin()} {vn(cb['tv'].min())} triệu.")
    if len(tp) >= 2:
        y.append(f"• Trong các thành phố có đủ tin, {tp['tv'].idxmax()} cao nhất ({vn(tp['tv'].max())} triệu), "
                 f"{tp['tv'].idxmin()} thấp nhất ({vn(tp['tv'].min())} triệu)"
                 + ("; chênh lệch giữa các thành phố nhỏ." if tp['tv'].max() - tp['tv'].min() <= 2 else "."))
    if len(kn) >= 2:
        y.append(f"• Theo kinh nghiệm, nhóm \"{kn.index[0]}\" trung vị {vn(kn['tv'].iloc[0])} triệu, "
                 f"nhóm \"{kn.index[-1]}\" {vn(kn['tv'].iloc[-1])} triệu.")
    top = list(mo_hinh["quan_trong"])[:2]
    from phan_tich import NHAN_BIEN
    r = kq[mo_hinh["tot_nhat"]]
    y.append(f"• {mo_hinh['tot_nhat']} giải thích được khoảng {vn(r['r2_log']*100, 0)}% biến thiên của log lương "
             f"(sai số tuyệt đối trung bình {vn(r['mae_trieu'])} triệu so với {vn(kq[list(kq)[0]]['mae_trieu'])} "
             f"triệu của đường cơ sở); hai biến quan trọng nhất là {NHAN_BIEN[top[0]].lower()} và "
             f"{NHAN_BIEN[top[1]].lower()}.")
    S += [Paragraph("5. Kết luận và đề xuất", h), Paragraph("<br/>".join(y), p), Paragraph(
        "<b>Hạn chế:</b> lương là mức người đăng tin công bố chứ không phải lương thực nhận; tin \"thỏa thuận\" "
        "và tin chỉ có một cận lương không được dùng; nguồn thu thập không rõ nên mẫu có thể lệch "
        "(thiên về một số trang và ngành).<br/>"
        "<b>Đề xuất:</b> dùng kết quả như mốc tham khảo theo cấp bậc và ngành, không dùng để định lương "
        "cho từng vị trí; muốn dự đoán tốt hơn cần thêm biến về doanh nghiệp (quy mô, ngành chi tiết) "
        "và dữ liệu có mã tin để tránh trùng lặp.", p)]
    _dung(S, duong_ra)


def _dung(S, duong_ra):
    doc = SimpleDocTemplate(duong_ra, pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                            topMargin=2 * cm, bottomMargin=1.8 * cm,
                            title="Báo cáo tự động: mức lương trong tin tuyển dụng ở Việt Nam")
    doc.build(S)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    kq_json = os.path.join(C.RESULTS, "ket_qua.json")
    if not os.path.exists(kq_json):
        sys.exit("Chưa có results/ket_qua.json; chạy trước: python src/phan_tich.py")
    with open(kq_json, encoding="utf-8") as f:
        kq = json.load(f)
    df, lam_sach = C.doc_du_lieu()
    out = os.path.join(C.RESULTS, "bao_cao.pdf")
    build_pdf(df, lam_sach, kq["mo_hinh"], out)
    print("Đã tạo:", out)


if __name__ == "__main__":
    main()
