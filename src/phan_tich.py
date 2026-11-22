"""Phân tích: làm sạch -> thống kê -> mô hình hồi quy dự đoán lương -> ket_qua.json + biểu đồ.

Chạy:  python src/phan_tich.py
Mô hình: dự đoán log(lương trung điểm) từ cấp bậc, hình thức, thành phố, ngành, số năm kinh nghiệm,
số kỹ năng. So sánh với đường cơ sở (luôn đoán trung vị), hồi quy tuyến tính (Ridge) và rừng ngẫu nhiên.
"""
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

warnings.filterwarnings("ignore")
CAT = ["cap_bac", "hinh_thuc", "thanh_pho", "nganh"]
NUM = ["nam_kn", "so_ky_nang"]
SEED = 42


def huan_luyen(df):
    d = df[df["luong"].notna()].copy()
    d["nam_kn"] = d["nam_kn"].fillna(d["nam_kn"].median())
    X, y = d[CAT + NUM], np.log(d["luong"])
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=SEED)

    def pipe(model):
        pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CAT)],
                                remainder="passthrough")
        return Pipeline([("pre", pre), ("m", model)])

    mo_hinh = {
        "Cơ sở (luôn đoán trung vị)": None,
        "Hồi quy tuyến tính (Ridge)": pipe(Ridge(alpha=1.0)),
        "Rừng ngẫu nhiên": pipe(RandomForestRegressor(n_estimators=150, min_samples_leaf=20,
                                                      n_jobs=-1, random_state=SEED)),
    }
    kq, tot_nhat = {}, None
    for ten, m in mo_hinh.items():
        if m is None:
            du_doan = np.full(len(yte), ytr.median())
        else:
            m.fit(Xtr, ytr)
            du_doan = m.predict(Xte)
        kq[ten] = {"r2_log": float(r2_score(yte, du_doan)),
                   "mae_trieu": float(mean_absolute_error(np.exp(yte), np.exp(du_doan)))}
        if m is not None and (tot_nhat is None or kq[ten]["r2_log"] > kq[tot_nhat[0]]["r2_log"]):
            tot_nhat = (ten, m)
    # Mức quan trọng theo hoán vị trên tập kiểm tra, tính trên từng biến gốc
    mau = Xte.sample(min(5000, len(Xte)), random_state=SEED)
    pi = permutation_importance(tot_nhat[1], mau, yte.loc[mau.index], n_repeats=5,
                                random_state=SEED, scoring="r2")
    quan_trong = dict(sorted(zip(CAT + NUM, pi.importances_mean.round(4).tolist()),
                             key=lambda kv: -kv[1]))
    return {"n_train": len(Xtr), "n_test": len(Xte), "ket_qua": kq, "tot_nhat": tot_nhat[0],
            "quan_trong": quan_trong}


NHAN_BIEN = {"cap_bac": "Cấp bậc", "hinh_thuc": "Hình thức", "thanh_pho": "Thành phố",
             "nganh": "Ngành", "nam_kn": "Số năm kinh nghiệm", "so_ky_nang": "Số kỹ năng"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    duong_dan, la_mau = C.duong_dan_du_lieu()
    df, lam_sach = C.doc_du_lieu(duong_dan)
    tk = C.thong_ke(df)
    print("Dữ liệu:", duong_dan, "(MẪU)" if la_mau else "", lam_sach)

    mo_hinh = huan_luyen(df)
    print(json.dumps(mo_hinh, ensure_ascii=False, indent=1))

    # Biểu đồ
    hinh = {}
    hinh["cap_bac"] = C.luu_hinh(C.ve_cot(tk["cap_bac"], "Cấp bậc", ngang=True), "bd_cap_bac.png")
    hinh["thanh_pho"] = C.luu_hinh(C.ve_cot(tk["thanh_pho"], "Thành phố", xoay=25), "bd_thanh_pho.png")
    hinh["kinh_nghiem"] = C.luu_hinh(C.ve_cot(tk["kinh_nghiem"], "Kinh nghiệm yêu cầu", xoay=15),
                                     "bd_kinh_nghiem.png")
    import matplotlib.pyplot as plt
    C._khung()
    fig, ax = plt.subplots(figsize=(6.2, 2.8))
    qt = mo_hinh["quan_trong"]
    ax.barh([NHAN_BIEN[k] for k in list(qt)[::-1]], list(qt.values())[::-1], color=C.XANH)
    ax.set_xlabel("Mức giảm R² khi xáo trộn biến (càng lớn càng quan trọng)")
    fig.tight_layout()
    hinh["quan_trong"] = C.luu_hinh(fig, "bd_quan_trong.png")

    # Lưu kết quả (bảng gọn để báo cáo/dashboard không phải tính lại mô hình)
    def bang(g):
        return {k: {c: float(v) for c, v in r.items()} for k, r in g.iterrows()}
    out = {"lam_sach": lam_sach, "la_mau": la_mau, "mo_hinh": mo_hinh,
           "luong_tv": float(tk["luong_tv"]), "luong_tb": float(tk["luong_tb"]),
           "cap_bac": bang(tk["cap_bac"]), "thanh_pho": bang(tk["thanh_pho"]),
           "kinh_nghiem": bang(tk["kinh_nghiem"]), "nganh": bang(tk["nganh"]),
           "so_tin_tp": {k: int(v) for k, v in tk["so_tin_tp"].items()}}
    os.makedirs(C.RESULTS, exist_ok=True)
    with open(os.path.join(C.RESULTS, "ket_qua.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("Đã ghi results/ket_qua.json và", len(hinh), "biểu đồ")


if __name__ == "__main__":
    main()
