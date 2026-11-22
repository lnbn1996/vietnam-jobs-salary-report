"""Dashboard tương tác (Streamlit): chọn biến, xem biểu đồ, tải dữ liệu đã lọc và báo cáo PDF.

Chạy:  streamlit run src/dashboard.py
"""
import json
import os
import sys
import tempfile

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import tao_bao_cao as B  # noqa: E402

BIEN = {"Cấp bậc": "cap_bac", "Thành phố": "thanh_pho", "Kinh nghiệm yêu cầu": "nhom_kn",
        "Ngành": "nganh", "Hình thức": "hinh_thuc"}
THU_TU = {"cap_bac": C.THU_TU_CAP, "nhom_kn": C.THU_TU_KN}

st.set_page_config(page_title="Lương trong tin tuyển dụng VN", layout="wide")


@st.cache_data(show_spinner="Đang đọc và làm sạch dữ liệu...")
def tai_du_lieu():
    duong_dan, la_mau = C.duong_dan_du_lieu()
    df, lam_sach = C.doc_du_lieu(duong_dan)
    return df, lam_sach, la_mau


@st.cache_data
def tai_mo_hinh():
    p = os.path.join(C.RESULTS, "ket_qua.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)["mo_hinh"]
    return None


try:   # theo giao diện hiện tại của Streamlit (sáng/tối)
    C.dat_che_do_toi(st.context.theme.type == "dark")
except Exception:
    C.dat_che_do_toi(False)

df, lam_sach, la_mau = tai_du_lieu()
mo_hinh = tai_mo_hinh()

st.title("Mức lương trong tin tuyển dụng ở Việt Nam")
st.caption("Nguồn: Vietnam Jobs Dataset (Kaggle, nguyenchitinh, MIT), tin ngày 22/04/2025; "
           "lương = trung điểm khoảng lương, triệu VND/tháng.")
if la_mau:
    st.warning("Đang dùng tệp mẫu nhỏ (data/sample_jobs.csv) vì chưa có tệp đầy đủ; số liệu chỉ để minh họa.")

# ------------------------------------------------------------- bộ lọc
sb = st.sidebar
sb.header("Bộ lọc")
tp = sb.multiselect("Thành phố", sorted(df["thanh_pho"].unique()))
cap = sb.multiselect("Cấp bậc", [x for x in C.THU_TU_CAP if x in set(df["cap_bac"])])
nganh = sb.multiselect("Ngành", sorted(df["nganh"].unique()))
ht = sb.multiselect("Hình thức", sorted(df["hinh_thuc"].unique()))
chi_co_luong = sb.checkbox("Chỉ tin có khoảng lương", value=True)
lmax = float(df["luong"].max()) if df["luong"].notna().any() else 100.0
luong = sb.slider("Khoảng lương (triệu VND/tháng)", 0.0, lmax, (0.0, lmax))

f = df
for cot, chon in [("thanh_pho", tp), ("cap_bac", cap), ("nganh", nganh), ("hinh_thuc", ht)]:
    if chon:
        f = f[f[cot].isin(chon)]
if chi_co_luong:
    f = f[f["luong"].between(*luong)]
elif luong != (0.0, lmax):
    f = f[f["luong"].isna() | f["luong"].between(*luong)]

mo_ta = ", ".join(f"{t}: {', '.join(c)}" for t, c in
                  [("Thành phố", tp), ("Cấp bậc", cap), ("Ngành", nganh), ("Hình thức", ht)] if c) or None

# ------------------------------------------------------------- chỉ số
d = f[f["luong"].notna()]
c1, c2, c3 = st.columns(3)
c1.metric("Số tin (sau lọc)", f"{len(f):,}".replace(",", "."))
c2.metric("Số tin có khoảng lương", f"{len(d):,}".replace(",", "."))
c3.metric("Lương trung vị (triệu VND/tháng)", C.vn(d["luong"].median()) if len(d) else "—")

if len(f) == 0:
    st.info("Không có tin nào khớp bộ lọc.")
    st.stop()

# ------------------------------------------------------------- biểu đồ
t1, t2, t3 = st.tabs(["So sánh theo nhóm", "Phân bố lương", "Dữ liệu và báo cáo"])
with t1:
    a, b = st.columns(2)
    ten_bien = a.selectbox("Nhóm theo biến", list(BIEN))
    chi_so = b.radio("Chỉ số", ["Lương trung vị", "Số tin"], horizontal=True)
    cot = BIEN[ten_bien]
    if chi_so == "Lương trung vị":
        tkf = C.thong_ke(f)
        g = {"cap_bac": tkf["cap_bac"], "thanh_pho": tkf["thanh_pho"], "nhom_kn": tkf["kinh_nghiem"],
             "nganh": tkf["nganh"]}.get(cot)
        if g is None:  # hình thức: tính trực tiếp
            g = d.groupby(cot).agg(n=("luong", "size"), tv=("luong", "median"))
            g = g[g["n"] >= 30]
        if len(g):
            st.pyplot(C.ve_cot(g, ten_bien, ngang=True, size=(8, 3.6)))
            st.caption("Chỉ hiển thị nhóm có từ 30 tin có khoảng lương; n là số tin của nhóm.")
        else:
            st.info("Không nhóm nào đủ 30 tin có khoảng lương.")
    else:
        dem = f[cot].value_counts()
        if cot in THU_TU:
            dem = dem.reindex([x for x in THU_TU[cot] if x in dem.index])
        C._khung()
        fig, ax = plt.subplots(figsize=(8, 3.6))
        ax.bar(dem.index.astype(str), dem.values, color=C.XANH)
        ax.set_ylabel("Số tin")
        plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=8)
        fig.tight_layout()
        st.pyplot(fig)

with t2:
    if len(d):
        C._khung()
        fig, ax = plt.subplots(figsize=(8, 3.4))
        ax.hist(d["luong"], bins=40, color=C.XANH)
        ax.axvline(d["luong"].median(), color=C.DO, ls="--", label="Trung vị")
        ax.set_xlabel("Lương (triệu VND/tháng)")
        ax.set_ylabel("Số tin")
        ax.legend(frameon=False)
        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.info("Không có tin nào có khoảng lương trong bộ lọc.")

with t3:
    cot_hien = ["job_title", "cap_bac", "hinh_thuc", "thanh_pho", "nganh", "experience", "salary", "luong"]
    hien = f[cot_hien].head(200).copy()
    hien["luong"] = hien["luong"].map(lambda x: "" if pd.isna(x) else C.vn(x))   # dấu phẩy thập phân
    st.dataframe(hien, width="stretch")
    st.caption("Hiển thị 200 dòng đầu của dữ liệu đã lọc.")
    st.download_button("Tải dữ liệu đã lọc (CSV)", f[cot_hien].to_csv(index=False).encode("utf-8-sig"),
                       "du_lieu_da_loc.csv", "text/csv")
    if mo_hinh is None:
        st.info("Chưa có results/ket_qua.json; chạy src/phan_tich.py để có mục mô hình trong báo cáo.")
    elif st.button("Tạo báo cáo PDF cho phần đã lọc"):
        with st.spinner("Đang sinh báo cáo..."):
            out = os.path.join(tempfile.mkdtemp(), "bao_cao.pdf")
            B.build_pdf(f, lam_sach, mo_hinh, out, mo_ta_loc=mo_ta)
            with open(out, "rb") as fh:
                st.session_state["pdf"] = fh.read()
    if "pdf" in st.session_state:
        st.download_button("Tải báo cáo PDF", st.session_state["pdf"], "bao_cao.pdf", "application/pdf")
