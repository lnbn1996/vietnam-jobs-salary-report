"""Làm sạch dữ liệu, thống kê và vẽ biểu đồ dùng chung cho báo cáo và dashboard.

Dữ liệu: Vietnam Jobs Dataset (Kaggle, nguyenchitinh, MIT), tin tuyển dụng ngày 22/04/2025.
Lương trong tệp tính theo triệu VND/tháng (USD đã quy đổi sẵn trong tệp).
"""
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FULL = os.path.join(ROOT, "data", "vietnam_jobs_2025.csv")
DATA_MAU = os.path.join(ROOT, "data", "sample_jobs.csv")
RESULTS = os.path.join(ROOT, "results")

MAX_LUONG = 200          # triệu VND/tháng; trên mức này coi là ngoại lai
TOP_THANH_PHO = 8
TOP_NGANH = 15
XANH, DO = "#2F6DB5", "#D9822B"
THU_TU_CAP = ["Thực tập/mới ra trường", "Nhân viên/chuyên viên", "Trưởng nhóm/giám sát",
              "Quản lý", "Giám đốc"]
THU_TU_KN = ["Không yêu cầu", "Dưới 1 năm", "1–2 năm", "2–3 năm", "3–5 năm", "Trên 5 năm"]


def duong_dan_du_lieu():
    """Ưu tiên tệp đầy đủ; nếu không có thì dùng tệp mẫu nhỏ (kèm cờ báo)."""
    if os.path.exists(DATA_FULL):
        return DATA_FULL, False
    return DATA_MAU, True


def nhom_cap_bac(s):
    s = str(s)
    if "giám đốc" in s:
        return "Giám đốc"
    if "thực tập" in s or "sinh viên" in s or "mới tốt nghiệp" in s:
        return "Thực tập/mới ra trường"
    if "trưởng" in s or "giám sát" in s:
        return "Trưởng nhóm/giám sát"
    if "quản lý" in s:
        return "Quản lý"
    return "Nhân viên/chuyên viên"


def nhom_hinh_thuc(s):
    s = str(s)
    if "thực tập" in s:
        return "Thực tập"
    if "bán thời gian" in s or "part-time" in s:
        return "Bán thời gian"
    if "toàn thời gian" in s or "full-time" in s or "chính thức" in s:
        return "Toàn thời gian"
    return "Khác"


def so_nam_kinh_nghiem(s):
    """'2 - 5 năm' -> 3,5; 'trên 1 năm' -> 1; 'dưới 1 năm' / 'lên đến 1 năm' -> 0,5; 'không yêu cầu' -> 0."""
    s = str(s)
    if "không yêu cầu" in s:
        return 0.0
    so = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[.,]\d+)?", s)]
    if not so:
        return np.nan
    if len(so) >= 2:
        return (so[0] + so[1]) / 2
    if "dưới" in s or "lên đến" in s:
        return so[0] / 2
    return so[0]


def nhom_kinh_nghiem(y):
    if pd.isna(y):
        return np.nan
    if y == 0:
        return "Không yêu cầu"
    if y < 1:
        return "Dưới 1 năm"
    if y < 2:
        return "1–2 năm"
    if y < 3:
        return "2–3 năm"
    if y <= 5:
        return "3–5 năm"
    return "Trên 5 năm"


def lam_sach(df_goc):
    """Trả về (df sạch, thống kê bước làm sạch). Các bước theo đúng thứ tự ghi trong báo cáo."""
    tk = {"n_goc": len(df_goc)}
    df = df_goc.drop_duplicates().copy()
    tk["n_trung"] = tk["n_goc"] - len(df)

    df["cap_bac"] = df["position_level"].map(nhom_cap_bac)
    df["hinh_thuc"] = df["job_type"].map(nhom_hinh_thuc)
    df["nam_kn"] = df["experience"].map(so_nam_kinh_nghiem)
    df["nhom_kn"] = df["nam_kn"].map(nhom_kinh_nghiem)
    df["so_ky_nang"] = df["skills"].fillna("").map(lambda s: len([x for x in s.split(",") if x.strip()]))

    def nganh_chinh(s):
        if pd.isna(s):
            return np.nan
        for x in str(s).split(","):
            if x.strip():
                return x.strip().title()
        return np.nan

    df["nganh"] = df["job_fields"].map(nganh_chinh)
    top_nganh = df["nganh"].value_counts().head(TOP_NGANH).index
    df["nganh"] = df["nganh"].where(df["nganh"].isin(top_nganh), "Khác").fillna("Không rõ")

    tp = df["city"].str.title()
    top_tp = tp.value_counts().head(TOP_THANH_PHO).index
    df["thanh_pho"] = tp.where(tp.isin(top_tp), "Tỉnh/thành khác")

    # Lương: chỉ coi là "khoảng lương" khi có đủ cận dưới và cận trên (>0, min <= max)
    khoang = (df["salary_min"] > 0) & (df["salary_max"] >= df["salary_min"])
    mot_can = ((df["salary_min"] > 0) ^ (df["salary_max"] > 0))
    df["luong"] = np.where(khoang, (df["salary_min"] + df["salary_max"]) / 2, np.nan)
    tk["n_khoang"] = int(khoang.sum())
    tk["n_mot_can"] = int(mot_can.sum())
    tk["n_min_lon_hon_max"] = int(((df["salary_min"] > 0) & (df["salary_max"] > 0)
                                   & (df["salary_max"] < df["salary_min"])).sum())
    tk["n_khong_luong"] = int(((df["salary_min"] == 0) & (df["salary_max"] == 0)).sum())
    qua_cao = df["luong"] > MAX_LUONG
    tk["n_qua_cao"] = int(qua_cao.sum())
    df.loc[qua_cao, "luong"] = np.nan
    tk["n_sau"] = len(df)
    tk["n_co_luong"] = int(df["luong"].notna().sum())
    return df, tk


def doc_du_lieu(duong_dan=None):
    if duong_dan is None:
        duong_dan, _ = duong_dan_du_lieu()
    return lam_sach(pd.read_csv(duong_dan))


# ---------------------------------------------------------------- thống kê và biểu đồ
def vn(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def thong_ke(df):
    """Các bảng/số liệu chính, tính từ df đã làm sạch (có thể là bản đã lọc)."""
    d = df[df["luong"].notna()]
    tk = {"n_tin": len(df), "n_co_luong": len(d)}
    if len(d):
        tk["luong_tv"] = d["luong"].median()
        tk["luong_tb"] = d["luong"].mean()

    def nhom(cot, thu_tu=None, toi_thieu=30):
        g = d.groupby(cot).agg(n=("luong", "size"), tv=("luong", "median"),
                               q1=("luong", lambda s: s.quantile(.25)),
                               q3=("luong", lambda s: s.quantile(.75)))
        g = g[g["n"] >= toi_thieu] if len(g) else g
        if thu_tu is not None:
            g = g.reindex([x for x in thu_tu if x in g.index])
        return g

    tk["cap_bac"] = nhom("cap_bac", THU_TU_CAP)
    tk["thanh_pho"] = nhom("thanh_pho").sort_values("tv", ascending=False)
    tk["kinh_nghiem"] = nhom("nhom_kn", THU_TU_KN)
    tk["nganh"] = nhom("nganh").sort_values("tv", ascending=False)
    tk["so_tin_tp"] = df["thanh_pho"].value_counts()
    return tk


CHE_DO_TOI = False   # dashboard đặt True khi giao diện tối; báo cáo PDF luôn dùng False


def dat_che_do_toi(bat):
    global CHE_DO_TOI
    truoc, CHE_DO_TOI = CHE_DO_TOI, bool(bat)
    return truoc


def _khung():
    plt.rcParams.update({"font.family": "Arial", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    if CHE_DO_TOI:   # nền trong suốt + chữ sáng để hợp giao diện tối
        mau = "#E6E6E6"
        plt.rcParams.update({"figure.facecolor": "none", "axes.facecolor": "none",
                             "savefig.facecolor": "none", "text.color": mau,
                             "axes.labelcolor": mau, "xtick.color": mau, "ytick.color": mau,
                             "axes.edgecolor": mau, "legend.labelcolor": mau})
    else:
        plt.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "white",
                             "savefig.facecolor": "white", "text.color": "black",
                             "axes.labelcolor": "black", "xtick.color": "black",
                             "ytick.color": "black", "axes.edgecolor": "black",
                             "legend.labelcolor": "black"})


def ve_cot(g, nhan_x, tieu_de_y="Lương trung vị (triệu VND/tháng)", xoay=20, ngang=False, size=(6.2, 3.1)):
    """Biểu đồ cột lương trung vị, có số mẫu n dưới mỗi nhãn; ngang=True cho nhãn dài."""
    _khung()
    nhan = [f"{i}\n(n={vn(r['n'], 0)})" for i, r in g.iterrows()]
    if ngang:
        fig, ax = plt.subplots(figsize=(size[0], max(size[1], 0.55 * len(g) + 0.9)))
        ax.barh(nhan[::-1], g["tv"].values[::-1], color=XANH)
        for i, v in enumerate(g["tv"].values[::-1]):
            ax.text(v + 0.3, i, vn(v), va="center", fontsize=9)
        ax.set_xlabel(tieu_de_y)
        ax.margins(x=0.1)
    else:
        fig, ax = plt.subplots(figsize=size)
        ax.bar(nhan, g["tv"].values, color=XANH)
        for i, v in enumerate(g["tv"].values):
            ax.text(i, v + 0.2, vn(v), ha="center", fontsize=9)
        ax.set_ylabel(tieu_de_y)
        ax.set_xlabel(nhan_x)
        plt.setp(ax.get_xticklabels(), rotation=xoay, ha="right", fontsize=8)
    fig.tight_layout()
    return fig


def luu_hinh(fig, ten, thu_muc=RESULTS):
    os.makedirs(thu_muc, exist_ok=True)
    p = os.path.join(thu_muc, ten)
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p
