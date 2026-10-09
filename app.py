import math
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# 1. ページ設定（最優先で読み込み）
st.set_page_config(page_title="雨水排水設計支援ツール", layout="wide")

# 2. CSSの埋め込み（見た目の定義）
st.markdown("""
    <style>
    /* 入力項目ラベル */
    div[data-testid="stWidgetLabel"] p,
    .stSelectbox label p,
    .stNumberInput label p,
    .stSlider label p {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #0f172a !important;
        line-height: 1.4 !important;
        margin-bottom: 8px !important;
    }

    /* Press Enter to apply を非表示にする */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
    
    /* 入力ボックス最大幅 */
    div[data-testid="stNumberInput"],
    div[data-testid="stSelectbox"],
    div[data-testid="stSlider"] {
        width: 100% !important;
        max-width: 435px !important;
    }
    
    /* 入力コンテナ高さ */
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stSelectbox"] > div,
    div[data-baseweb="input"],
    div[data-baseweb="select"],
    div[data-baseweb="base-input"] {
        height: 56px !important;
        min-height: 56px !important;
        border-radius: 8px !important;
    }
    
    /* 入力テキスト */
    input {
        font-size: 24px !important;
        font-weight: normal !important;
        color: #0f172a !important;
        height: 54px !important;
        line-height: 54px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    
    /* +/- ボタン */
    div[data-testid="stNumberInput"] button {
        height: 54px !important;
        min-height: 54px !important;
        width: 45px !important;
    }
    div[data-testid="stNumberInput"] button svg {
        transform: scale(1.3) !important;
    }
    
    /* セレクトボックス内枠・テキスト */
    .stSelectbox div[data-baseweb="select"] {
        font-size: 24px !important;
        font-weight: normal !important;
        height: 56px !important;
        min-height: 56px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        height: 54px !important;
        min-height: 54px !important;
        display: flex !important;
        align-items: center !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    .stSelectbox div[data-baseweb="select"] svg {
        transform: scale(1.3) !important;
    }
    
    /* スライダー要素 */
    div[data-testid="stSlider"] > label div p,
    div[data-testid="stSlider"] label p {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #0f172a !important;
        line-height: 1.4 !important;
    }
    div[data-testid="stSlider"] div[data-testid="stWidgetLabel"] + div div p,
    div[data-testid="stSlider"] [role="slider"] div {
        font-size: 22px !important;
        font-weight: bold !important;
    }
    
    /* 見出し装飾 */
    h5 {
        font-size: 30px !important;
        font-weight: 800 !important;
        color: #0ea5e9 !important;
        margin-top: 10px !important;
        margin-bottom: 15px !important;
        border-left: 6px solid #0ea5e9;
        padding-left: 12px !important;
        border-bottom: none !important;
    }
    
    h3 {
        font-size: 32px !important;
        font-weight: bold !important;
        margin-top: 0px !important;
        margin-bottom: 5px !important;
    }

    /* タブスタイル */
    div[data-testid="stTabBar"] button,
    div[data-testid="stTabBar"] button div,
    div[data-testid="stTabBar"] button p,
    [data-baseweb="tab"] *,
    .stTabs [role="tab"] p,
    .stTabs [role="tab"] {
        font-size: 24px !important;
        font-weight: bold !important;
        line-height: 1.6 !important;
    }
    div[data-testid="stTabBar"] {
        gap: 24px !important;
        height: auto !important;
    }

    /* 判定結果カードラベル・数値 */
    div[data-testid="stMetric"] label[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] {
        font-size: 22px !important;
        font-weight: bold !important;
        color: #334155 !important;
        line-height: 1.4 !important;
        margin-bottom: 6px !important;
    }
    div[data-testid="stMetricValue"] div,
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: normal !important;
        color: #0f172a !important;
    }

    /* チェックボックス */
    div[data-testid="stCheckbox"] label p {
        font-weight: normal !important;
    }

    /* 横並びコンテナ枠制限 */
    .compact-row-container {
        max-width: 435px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. タイトル表示
st.title("🌧️ 雨水排水設計支援ツール")

# 4. セッション状態の初期化
if "upstream_Q" not in st.session_state:
    st.session_state["upstream_Q"] = 0.0

# 5. コールバック関数（単位自動換算など）
def convert_area_a():
    new_unit = st.session_state.area_unit_a
    if new_unit == "ha":
        st.session_state.area_val_a = st.session_state.get("area_val_a", 1000.0) / 10000.0
    else:
        st.session_state.area_val_a = st.session_state.get("area_val_a", 0.1000) * 10000.0

def convert_slope_a():
    old_unit = st.session_state.get("prev_s_type_a", "‰")
    new_unit = st.session_state.s_type_a
    cur_val = st.session_state.get("s_val_a", 5.0)

    if old_unit == "‰":
        S = cur_val / 1000.0
    elif old_unit == "%":
        S = cur_val / 100.0
    else:
        S = 1.0 / cur_val if cur_val > 0 else 0.0

    if new_unit == "‰":
        st.session_state.s_val_a = S * 1000.0
    elif new_unit == "%":
        st.session_state.s_val_a = S * 100.0
    else:
        st.session_state.s_val_a = float(round(1.0 / S)) if S > 0 else 200.0

    st.session_state.prev_s_type_a = new_unit

# ----------------------------------------------------
# 共通水理計算関数
# ----------------------------------------------------
def calculate_manning(
    shape_type, slope_val, slope_type, roughness_n, ratio,
    w_mm=None, h_mm=None, w_bottom_mm=None, r_bottom_mm=None,
    d_mm=None, b1_mm=None, b2_mm=None
):
    if "‰" in slope_type or "パーミル" in slope_type:
        S = slope_val / 1000.0
    elif "%" in slope_type or "パーセント" in slope_type:
        S = slope_val / 100.0
    else:
        S = 1.0 / slope_val if slope_val > 0 else 0.0

    A_max, P_max, h_design_mm = 0.0, 0.0, 0.0

    if shape_type == "U形":
        B1, H = w_mm / 1000.0, h_mm / 1000.0
        h_design = H * ratio
        h_design_mm = h_design * 1000.0
        
        B2 = (w_bottom_mm / 1000.0) if w_bottom_mm is not None else B1
        R = (r_bottom_mm / 1000.0) if r_bottom_mm is not None else 0.0
        
        slope_len = math.sqrt(((B1 - B2) / 2.0)**2 + H**2)
        bh = B2 + (B1 - B2) * (h_design / H)
        
        if R > 0.0:
            if h_design >= R:
                A_max = ((B2 + bh) * h_design / 2.0) - (2.0 - math.pi / 2.0) * (R ** 2)
                P_max = B2 + 2.0 * h_design * (slope_len / H) - 2.0 * R * ((slope_len / H) + 1.0) + math.pi * R
            else:
                A_max = ((B2 + bh) * h_design / 2.0) * (h_design / R)
                P_max = B2 + 2.0 * h_design
        else:
            A_max = (B2 + bh) * h_design / 2.0
            P_max = B2 + 2.0 * h_design * (slope_len / H)

    elif shape_type == "円形":
        D = d_mm / 1000.0
        r = D / 2.0
        h_design = D * ratio
        h_design_mm = h_design * 1000.0
        
        cos_val = max(-1.0, min(1.0, (r - h_design) / r))
        theta = 2.0 * math.acos(cos_val)
        
        if h_design <= r:
            A_max = (r ** 2) * (theta - math.sin(theta)) / 2.0
        else:
            A_max = (math.pi * (r ** 2)) - ((r ** 2) * ((2.0 * math.pi - theta) - math.sin(2.0 * math.pi - theta)) / 2.0)
            
        P_max = r * theta

    elif shape_type == "台形":
        B1, B2, H = b1_mm / 1000.0, b2_mm / 1000.0, h_mm / 1000.0
        h_design = H * ratio
        h_design_mm = h_design * 1000.0
        
        bh = B2 + (B1 - B2) * (h_design / H)
        slope_len = math.sqrt(((B1 - B2) / 2.0)**2 + H**2)
        
        A_max = (B2 + bh) * h_design / 2.0
        P_max = B2 + 2.0 * h_design * (slope_len / H)

    R_max = A_max / P_max if P_max > 0.0 else 0.0

    if P_max > 0.0 and S > 0.0:
        V_max = (1.0 / roughness_n) * (R_max ** (2.0 / 3.0)) * (S ** (1.0 / 2.0))
        Q_max = A_max * V_max
    else:
        V_max, Q_max = 0.0, 0.0

    return Q_max, V_max, h_design_mm, A_max, P_max, R_max


# ----------------------------------------------------
# 共通水理計算関数
# ----------------------------------------------------
def calculate_manning(
    shape_type, slope_val, slope_type, roughness_n, ratio,
    w_mm=None, h_mm=None, w_bottom_mm=None, r_bottom_mm=None,
    d_mm=None, b1_mm=None, b2_mm=None
):
    if "‰" in slope_type or "パーミル" in slope_type:
        S = slope_val / 1000.0
    elif "%" in slope_type or "パーセント" in slope_type:
        S = slope_val / 100.0
    else:
        S = 1.0 / slope_val if slope_val > 0 else 0.0

    A_max, P_max, h_design_mm = 0.0, 0.0, 0.0

    if shape_type == "U形":
        B1, H = w_mm / 1000.0, h_mm / 1000.0
        h_design = H * ratio
        h_design_mm = h_design * 1000.0
        
        B2 = (w_bottom_mm / 1000.0) if w_bottom_mm is not None else B1
        R = (r_bottom_mm / 1000.0) if r_bottom_mm is not None else 0.0
        
        slope_len = math.sqrt(((B1 - B2) / 2.0)**2 + H**2)
        bh = B2 + (B1 - B2) * (h_design / H)
        
        dx = (B1 - B2) / 2.0
        alpha = math.atan2(H, dx) if dx > 0 else (math.pi / 2.0)
        
        A_base = (B2 + bh) * h_design / 2.0
        P_base = B2 + 2.0 * h_design * (slope_len / H)

        if R > 0.0:
            tan_half = math.tan(alpha / 2.0)
            d_pt = R / tan_half if tan_half > 0 else 0.0
            y_pt = d_pt * math.sin(alpha)

            if h_design >= y_pt:
                A_loss = 2.0 * (R * d_pt - (alpha * (R ** 2) / 2.0))
                A_max = max(0.0, A_base - A_loss)
                
                P_loss = 2.0 * (d_pt + R) - (alpha * R * 2.0)
                P_max = max(0.0, P_base - P_loss)
            else:
                ratio_h = h_design / y_pt if y_pt > 0 else 0.0
                A_loss = 2.0 * (R * d_pt - (alpha * (R ** 2) / 2.0)) * (ratio_h ** 2)
                A_max = max(0.0, A_base - A_loss)
                P_max = B2 + 2.0 * h_design
        else:
            A_max = A_base
            P_max = P_base

    elif shape_type == "円形":
        D = d_mm / 1000.0
        r = D / 2.0
        h_design = D * ratio
        h_design_mm = h_design * 1000.0
        
        cos_val = max(-1.0, min(1.0, (r - h_design) / r))
        theta = 2.0 * math.acos(cos_val)
        
        if h_design <= r:
            A_max = (r ** 2) * (theta - math.sin(theta)) / 2.0
        else:
            A_max = (math.pi * (r ** 2)) - ((r ** 2) * ((2.0 * math.pi - theta) - math.sin(2.0 * math.pi - theta)) / 2.0)
            
        P_max = r * theta

    elif shape_type == "台形":
        B1, B2, H = b1_mm / 1000.0, b2_mm / 1000.0, h_mm / 1000.0
        h_design = H * ratio
        h_design_mm = h_design * 1000.0
        
        bh = B2 + (B1 - B2) * (h_design / H)
        slope_len = math.sqrt(((B1 - B2) / 2.0)**2 + H**2)
        
        A_max = (B2 + bh) * h_design / 2.0
        P_max = B2 + 2.0 * h_design * (slope_len / H)

    R_max = A_max / P_max if P_max > 0.0 else 0.0

    if P_max > 0.0 and S > 0.0:
        V_max = (1.0 / roughness_n) * (R_max ** (2.0 / 3.0)) * (S ** (1.0 / 2.0))
        Q_max = A_max * V_max
    else:
        V_max, Q_max = 0.0, 0.0

    return Q_max, V_max, h_design_mm, A_max, P_max, R_max


# ----------------------------------------------------
# 断面描画関数
# ----------------------------------------------------
def draw_section(shape_type, h_design_mm, w_mm=None, h_mm=None, w_bottom_mm=None, d_mm=None, b1_mm=None, b2_mm=None, r_bottom_mm=None):
    plt.close('all')

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.15, 1.25)

    water_color = "#38bdf8"
    water_line_color = "#0369a1"
    wall_color = "#475569"
    dim_color = "#334155"

    def add_dim_line(p1, p2, text, is_horizontal=True, text_pos='above'):
        ax.annotate('', xy=p1, xytext=p2, arrowprops=dict(arrowstyle='<->', lw=1.2, color=dim_color))
        mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2

        if is_horizontal:
            text_x = mid_x
            text_y = mid_y - 0.05 if text_pos == 'below' else mid_y + 0.05
            va_align = 'top' if text_pos == 'below' else 'bottom'
            ha_align = 'center'
        else:
            text_x = mid_x + (-0.06 if mid_x < 0 else 0.06)
            text_y = mid_y
            va_align = 'center'
            ha_align = 'right' if mid_x < 0 else 'left'

        ax.text(text_x, text_y, text, ha=ha_align, va=va_align, fontsize=12, color=dim_color, fontweight='bold')

    def add_water_symbol(x, y, size=0.04):
        ax.plot([x - size * 1.5, x + size * 1.5], [y, y], color=water_line_color, lw=1.8, zorder=5)
        tri_x = [x - size, x + size, x, x - size]
        tri_y = [y + size * 1.5, y + size * 1.5, y, y + size * 1.5]
        ax.plot(tri_x, tri_y, color=water_line_color, lw=1.8, zorder=5)

    if shape_type == "U形":
        B1 = float(w_mm) if w_mm else 100.0
        B2 = float(w_bottom_mm) if (w_bottom_mm is not None and w_bottom_mm > 0) else B1
        H = float(h_mm) if h_mm else 100.0
        R = float(r_bottom_mm) if r_bottom_mm is not None else 0.0
        h_w = min(h_design_mm, H)

        max_dim = max(B1, H)
        scale = 1.05 / max_dim if max_dim > 0 else 1.0

        b1_s, b2_s, h_s, hw_s = B1 * scale, B2 * scale, H * scale, h_w * scale

        dx = (b1_s - b2_s) / 2.0
        alpha = math.atan2(h_s, dx) if dx > 0 else (math.pi / 2.0)

        r_s = R * scale
        tan_half = math.tan((math.pi - alpha) / 2.0)
        d_in = r_s * tan_half

        if d_in > b2_s / 2.0 and b2_s > 0:
            d_in = b2_s / 2.0
            r_s = d_in / tan_half if tan_half > 0 else 0.0

        if r_s > 0:
            xc_r = (b2_s / 2.0) - d_in
            yc_r = r_s

            p_wall_r = (xc_r + r_s * math.sin(alpha), yc_r - r_s * math.cos(alpha))

            angles_r = np.linspace(-math.pi / 2.0, alpha - math.pi / 2.0, 15)
            arc_x_r = xc_r + r_s * np.cos(angles_r)
            arc_y_r = yc_r + r_s * np.sin(angles_r)

            arc_x_l = -arc_x_r[::-1]
            arc_y_l = arc_y_r[::-1]

            x_wall = np.concatenate([[-b1_s / 2.0, -p_wall_r[0]], arc_x_l, arc_x_r, [p_wall_r[0], b1_s / 2.0]])
            y_wall = np.concatenate([[h_s, p_wall_r[1]], arc_y_l, arc_y_r, [p_wall_r[1], h_s]])
        else:
            x_wall = np.array([-b1_s / 2.0, -b2_s / 2.0, b2_s / 2.0, b1_s / 2.0])
            y_wall = np.array([h_s, 0.0, 0.0, h_s])

        if hw_s > 0:
            bw_s = b2_s + (b1_s - b2_s) * (hw_s / h_s) if h_s > 0 else b2_s

            if r_s > 0:
                y_pt_wall = yc_r - r_s * math.cos(alpha)

                if hw_s <= r_s:
                    cos_v = max(-1.0, min(1.0, (r_s - hw_s) / r_s))
                    theta = math.acos(cos_v)
                    t_r = np.linspace(-math.pi / 2.0, -math.pi / 2.0 + theta, 15)
                    
                    x_w_r = xc_r + r_s * np.cos(t_r)
                    y_w_r = yc_r + r_s * np.sin(t_r)
                    x_w_l = -x_w_r[::-1]
                    y_w_l = y_w_r[::-1]

                    x_water = np.concatenate([[-x_w_r[-1]], x_w_l, x_w_r, [x_w_r[-1]]])
                    y_water = np.concatenate([[hw_s], y_w_l, y_w_r, [hw_s]])
                    xw_surface = x_w_r[-1]

                elif hw_s < y_pt_wall:
                    sin_v = max(-1.0, min(1.0, (hw_s - r_s) / r_s))
                    phi = math.asin(sin_v)
                    
                    t_r = np.linspace(-math.pi / 2.0, phi, 15)
                    x_w_r = xc_r + r_s * np.cos(t_r)
                    y_w_r = yc_r + r_s * np.sin(t_r)
                    x_w_l = -x_w_r[::-1]
                    y_w_l = y_w_r[::-1]

                    x_water = np.concatenate([[-x_w_r[-1]], x_w_l, x_w_r, [x_w_r[-1]]])
                    y_water = np.concatenate([[hw_s], y_w_l, y_w_r, [hw_s]])
                    xw_surface = x_w_r[-1]

                else:
                    x_water = np.concatenate([[-bw_s / 2.0], arc_x_l, arc_x_r, [bw_s / 2.0]])
                    y_water = np.concatenate([[hw_s], arc_y_l, arc_y_r, [hw_s]])
                    xw_surface = bw_s / 2.0
            else:
                x_water = np.array([-bw_s / 2.0, -b2_s / 2.0, b2_s / 2.0, bw_s / 2.0])
                y_water = np.array([hw_s, 0.0, 0.0, hw_s])
                xw_surface = bw_s / 2.0

            ax.fill(x_water, y_water, color=water_color, alpha=0.6, zorder=2)
            ax.plot([-xw_surface, xw_surface], [hw_s, hw_s], color=water_line_color, lw=1.8, zorder=4)
            add_water_symbol(0, hw_s)

        ax.plot(x_wall, y_wall, color=wall_color, lw=3, zorder=3)

        dim_off_y, dim_off_x = 0.12, 0.12
        label_b1 = f"B1={B1:.0f}" if B1 != B2 else f"B={B1:.0f}"
        add_dim_line((-b1_s / 2.0, h_s + dim_off_y), (b1_s / 2.0, h_s + dim_off_y), label_b1, is_horizontal=True)

        if B1 != B2:
            add_dim_line((-b2_s / 2.0, -dim_off_y), (b2_s / 2.0, -dim_off_y), f"B2={B2:.0f}", is_horizontal=True, text_pos='below')

        add_dim_line((b1_s / 2.0 + dim_off_x, 0), (b1_s / 2.0 + dim_off_x, h_s), f"H={H:.0f}", is_horizontal=False)

        if hw_s > 0:
            add_dim_line((-b1_s / 2.0 - dim_off_x, 0), (-b1_s / 2.0 - dim_off_x, hw_s), f"h={h_w:.0f}", is_horizontal=False)

        if R > 0 and r_s > 0:
            xc_l = -((b2_s / 2.0) - d_in)
            yc_l = r_s

            arc_x_l = xc_l - r_s * math.cos(math.pi / 4.0)
            arc_y_l = yc_l - r_s * math.sin(math.pi / 4.0)

            text_x = arc_x_l + 0.05 + r_s * 0.3
            text_y = arc_y_l + 0.08 + r_s * 0.3

            ax.annotate(
                f"R={R:.0f}",
                xy=(arc_x_l, arc_y_l),
                xytext=(text_x, text_y),
                arrowprops=dict(arrowstyle='->', lw=1.0, color=dim_color),
                fontsize=11, color=dim_color, fontweight='bold', ha='left', va='bottom'
            )

    elif shape_type == "円形":
        D = d_mm if d_mm else 100
        h_w = min(h_design_mm, D)

        r_s = 0.52
        hw_s = (h_w / D) * (2 * r_s)

        if hw_s > 0:
            cos_v = max(-1.0, min(1.0, (r_s - hw_s) / r_s))
            theta = math.acos(cos_v)
            
            angle_start, angle_end = 1.5 * math.pi - theta, 1.5 * math.pi + theta
            t = np.linspace(angle_start, angle_end, 50)
            x_arc = r_s * np.cos(t)
            y_arc = r_s + r_s * np.sin(t)
            
            ax.fill(x_arc, y_arc, color=water_color, alpha=0.6, zorder=2)

            x_w = r_s * math.sin(theta)
            ax.plot([-x_w, x_w], [hw_s, hw_s], color=water_line_color, lw=1.8, zorder=4)
            add_water_symbol(0, hw_s)

        circle = patches.Circle((0, r_s), r_s, edgecolor=wall_color, facecolor='none', lw=3, zorder=3)
        ax.add_patch(circle)

        dim_off = 0.12
        add_dim_line((-r_s, 2*r_s + dim_off), (r_s, 2*r_s + dim_off), f"D={D:.0f}", is_horizontal=True)
        if hw_s > 0:
            add_dim_line((-r_s - dim_off, 0), (-r_s - dim_off, hw_s), f"h={h_w:.0f}", is_horizontal=False)

    elif shape_type == "台形":
        B1, B2, H = b1_mm if b1_mm else 100, b2_mm if b2_mm else 50, h_mm if h_mm else 100
        h_w = min(h_design_mm, H)

        scale = 1.05 / max(B1, H)
        b1_s, b2_s, h_s, hw_s = B1 * scale, B2 * scale, H * scale, h_w * scale

        bw_s = b2_s + (b1_s - b2_s) * (hw_s / h_s) if h_s > 0 else b2_s
        x_water = [-bw_s/2, -b2_s/2, b2_s/2, bw_s/2]
        y_water = [hw_s, 0, 0, hw_s]
        ax.fill(x_water, y_water, color=water_color, alpha=0.6, zorder=2)
        ax.plot([-bw_s/2, bw_s/2], [hw_s, hw_s], color=water_line_color, lw=1.8, zorder=4)

        if hw_s > 0:
            add_water_symbol(0, hw_s)

        x_wall = [-b1_s/2, -b2_s/2, b2_s/2, b1_s/2]
        y_wall = [h_s, 0, 0, h_s]
        ax.plot(x_wall, y_wall, color=wall_color, lw=3, zorder=3)

        dim_off_y, dim_off_x = 0.12, 0.12
        add_dim_line((-b1_s/2, h_s + dim_off_y), (b1_s/2, h_s + dim_off_y), f"B1={B1:.0f}", is_horizontal=True)
        add_dim_line((-b2_s/2, -dim_off_y), (b2_s/2, -dim_off_y), f"B2={B2:.0f}", is_horizontal=True, text_pos='below')
        add_dim_line((b1_s/2 + dim_off_x, 0), (b1_s/2 + dim_off_x, h_s), f"H={H:.0f}", is_horizontal=False)
        if hw_s > 0:
            add_dim_line((-b1_s / 2.0 - dim_off_x, 0), (-b1_s / 2.0 - dim_off_x, hw_s), f"h={h_w:.0f}", is_horizontal=False)

    plt.tight_layout()
    return fig
# ----------------------------------------------------
# メイン画面：タブ切り替え
# ----------------------------------------------------
tabA, = st.tabs(["📋 流れる？あふれる？"])

# ====================================================
# 【タブA】機能A：流れる？あふれる？
# ====================================================
with tabA:
    col_left_a, col_space_a, col_right_a = st.columns([1.0, 0.1, 1.4], gap="large")
    
    # --- 左側：条件入力領域 ---
    with col_left_a:
        st.subheader("⚙️ 条件入力")
        col_sub_left, col_sub_right = st.columns(2, gap="medium")
        
        with col_sub_left:
            channel_type = st.selectbox("水路の形状", options=["U形", "円形", "台形"], key="channel_type_a")
            
        with col_sub_right:
            material_options = {
                "U形": {"コンクリート(二次製品)": 0.013, "土側溝": 0.025, "石積み側溝": 0.025},
                "円形": {"塩ビ管": 0.010, "コルゲート管": 0.025},
                "台形": {"コンクリート(現場打ち)": 0.015, "土側溝": 0.025, "石積み側溝": 0.025}
            }
            available_materials = list(material_options[channel_type].keys())
            
            def update_n_a():
                st.session_state.n_input_a = material_options[channel_type][st.session_state.material_a]

            selected_material = st.selectbox("水路の種類", options=available_materials, key="material_a", on_change=update_n_a)
            default_n = material_options[channel_type][selected_material]
            
        if channel_type == "U形":
            col_dim_l, col_dim_r = st.columns(2, gap="medium")
            with col_dim_l:
                w_a = st.number_input("水路幅 B (mm)", min_value=50, max_value=5000, value=300, step=50, key="w_a")
            with col_dim_r:
                h_a = st.number_input("水路深 H (mm)", min_value=50, max_value=5000, value=300, step=50, key="h_a")
            
            show_detail = st.checkbox("詳細設定（下幅・底面Rを指定する）", value=False, key="show_detail_a")
            if show_detail:
                col_opt_l, col_opt_r = st.columns(2, gap="medium")
                with col_opt_l:
                    w_bottom_a = st.number_input("下幅 B2 (mm) ", min_value=50, max_value=5000, value=260, step=10, key="w_bottom_a")
                with col_opt_r:
                    r_bottom_a = st.number_input("底面角 R (mm) ", min_value=0, max_value=500, value=50, step=5, key="r_bottom_a")
            else:
                w_bottom_a, r_bottom_a = None, None
                
        elif channel_type == "円形":
            col_dim_l, col_dim_r = st.columns(2, gap="medium")
            with col_dim_l:
                d_a = st.number_input("管径 D (mm)", min_value=50, max_value=5000, value=300, step=50, key="d_a")
                w_a, h_a = d_a, d_a
            with col_dim_r:
                st.empty()

        elif channel_type == "台形":
            col_dim_l, col_dim_r = st.columns(2, gap="medium")
            with col_dim_l:
                b1_a = st.number_input("上幅 B1 (mm)", min_value=50, max_value=5000, value=400, step=50, key="b1_a")
            with col_dim_r:
                b2_a = st.number_input("下幅 B2 (mm)", min_value=50, max_value=5000, value=300, step=50, key="b2_a")
            
            col_dim2_l, col_dim2_r = st.columns(2, gap="medium")
            with col_dim2_l:
                h_a = st.number_input("水路深 H (mm)", min_value=50, max_value=5000, value=300, step=50, key="h_a")
            with col_dim2_r:
                st.empty()

        st.write("---") 

        col_mid_left, col_mid_right = st.columns(2, gap="medium")
        with col_mid_left:
            st.markdown('<div data-testid="stWidgetLabel"><p>流域面積 A</p></div>', unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="compact-row-container">', unsafe_allow_html=True)
                col_a_val, col_a_unit = st.columns([7, 3])
                
                with col_a_unit:
                    area_unit_a = st.selectbox(
                        "単位", ["㎡", "ha"], 
                        label_visibility="collapsed", 
                        key="area_unit_a",
                        on_change=convert_area_a
                    )
                    
                with col_a_val:
                    if "area_val_a" not in st.session_state:
                        st.session_state.area_val_a = 1000.0 if area_unit_a == "㎡" else 0.1000

                    if area_unit_a == "㎡":
                        area_m2_a = st.number_input(
                            "流域面積 A (㎡)", min_value=0.0, step=10.0, 
                            label_visibility="collapsed", key="area_val_a"
                        )
                        area_ha_a = area_m2_a / 10000.0
                    else:
                        area_ha_a = st.number_input(
                            "流域面積 A (ha)", min_value=0.0, step=0.0010, format="%.4f", 
                            label_visibility="collapsed", key="area_val_a"
                        )
                        area_m2_a = area_ha_a * 10000.0
                        
                st.markdown('</div>', unsafe_allow_html=True)

            I_a = st.number_input("降雨強度 I (mm/h)", min_value=0.0, max_value=300.0, value=119.0, step=1.0, key="I_a")

        with col_mid_right:
            st.markdown('<div data-testid="stWidgetLabel"><p>勾配</p></div>', unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="compact-row-container">', unsafe_allow_html=True)
                col_s_val, col_s_unit = st.columns([7, 3])
                
                with col_s_unit:
                    s_type_a = st.selectbox(
                        "単位", ["‰", "%", "1/N"], 
                        label_visibility="collapsed", 
                        key="s_type_a",
                        on_change=convert_slope_a                    )
                    
                with col_s_val:
                    if "s_val_a" not in st.session_state:
                        st.session_state.s_val_a = 5.0
                    if "prev_s_type_a" not in st.session_state:
                        st.session_state.prev_s_type_a = s_type_a

                    if s_type_a == "‰":
                        s_val_a = st.number_input(
                            "勾配値 (‰)", min_value=0.0, max_value=100.0, step=0.5, format="%.2f", 
                            label_visibility="collapsed", key="s_val_a"
                        )
                    elif s_type_a == "%":
                        s_val_a = st.number_input(
                            "勾配値 (%)", min_value=0.0, max_value=10.0, step=0.1, format="%.2f", 
                            label_visibility="collapsed", key="s_val_a"
                        )
                    else:
                        s_val_a = st.number_input(
                            "Nの値 (1/N)", min_value=1, max_value=10000, step=10, 
                            label_visibility="collapsed", key="s_val_a"
                        )
                        
                st.markdown('</div>', unsafe_allow_html=True)

            if "n_input_a" not in st.session_state:
                st.session_state.n_input_a = default_n

            n_a = st.number_input("粗度係数 n", min_value=0.001, max_value=0.100, value=st.session_state.n_input_a, step=0.001, format="%.3f", key="n_input_a")

        col_sub_bottom_left, col_sub_bottom_right = st.columns(2, gap="medium")
        with col_sub_bottom_left:
            C_MAP = {
                1.00: "水面・調整池",
                0.95: "屋根・コンクリート舗装",
                0.90: "アスファルト舗装",
                0.80: "ブロック敷",
                0.70: "砂利敷",
                0.50: "農地・裸地",
                0.30: "山林・緑地",
                0.10: "水田"
            }
            c_val = st.session_state.get("C_a", 0.9)
            c_rounded = round(c_val, 2)
            guide_text = C_MAP.get(c_rounded, "")

            col_label, col_guide = st.columns([1, 1])
            with col_label:
                st.markdown('<div data-testid="stWidgetLabel"><p>流出係数 C</p></div>', unsafe_allow_html=True)
            with col_guide:
                st.markdown(f"<div style='text-align: right; font-size: 16px; font-weight: bold; color: #777777; padding-top: 4px;'>{guide_text}</div>", unsafe_allow_html=True)

            C_a = st.slider("流出係数 C", min_value=0.0, max_value=1.0, value=0.9, step=0.05, key="C_a", label_visibility="collapsed")

        with col_sub_bottom_right:
            ratio_a = st.slider("水深比 (%)", min_value=10, max_value=100, value=80, step=5, key="ratio_a") / 100.0

    # --- 計算実行 ---
    if channel_type == "U形":
        Q_max_a, V_max_a, h_design_a_mm, A_design_a, P_design_a, R_design_a = calculate_manning(
            shape_type="U形", slope_val=s_val_a, slope_type=s_type_a, roughness_n=n_a, ratio=ratio_a,
            w_mm=w_a, h_mm=h_a, w_bottom_mm=w_bottom_a, r_bottom_mm=r_bottom_a
        )
    elif channel_type == "円形":
        Q_max_a, V_max_a, h_design_a_mm, A_design_a, P_design_a, R_design_a = calculate_manning(
            shape_type="円形", slope_val=s_val_a, slope_type=s_type_a, roughness_n=n_a, ratio=ratio_a,
            d_mm=d_a
        )
    elif channel_type == "台形":
        Q_max_a, V_max_a, h_design_a_mm, A_design_a, P_design_a, R_design_a = calculate_manning(
            shape_type="台形", slope_val=s_val_a, slope_type=s_type_a, roughness_n=n_a, ratio=ratio_a,
            b1_mm=b1_a, b2_mm=b2_a, h_mm=h_a
        )

    Q_in_a = (1.0 / 360.0) * C_a * I_a * area_ha_a

    # --- 右側：結果表示 & 断面描画 ---
    with col_right_a:
        st.subheader("📊 判定結果")
        
        g = 9.80665
        h_m = h_design_a_mm / 1000.0
        Fr = V_max_a / ((g * h_m) ** 0.5) if h_m > 0.0 else 0.0

        with st.container(border=True):
            use_modified_v_a = st.session_state.get("use_modified_v_a", False)

            if use_modified_v_a and Fr > 1.0:
                V_design = V_max_a / Fr
                Q_design = Q_max_a / Fr
                flow_status = f"{Fr:.2f}&emsp;射流"
                v_value_str = f"{V_design:.2f} m/s (修正流速)"
            else:
                V_design, Q_design = V_max_a, Q_max_a
                v_value_str = f"{V_design:.2f} m/s"
                if Fr > 1.0:
                    flow_status = f"{Fr:.2f}&emsp;射流"
                elif Fr > 0.0:
                    flow_status = f"{Fr:.2f}&emsp;常流"
                else:
                    flow_status = "0.00&emsp;静止"

            stored_Q = st.session_state.get("upstream_Q", 0.0)
            add_upstream = st.session_state.get("add_upstream_a", False) if stored_Q > 0.0 else False
            Q_total_in = Q_in_a + stored_Q if add_upstream else Q_in_a

            margin_ratio = (Q_design / Q_total_in * 100) if Q_total_in > 0 else 0

            if margin_ratio >= 120.0:
                st.success("## ⭕ 流れます")
            elif 100.0 <= margin_ratio < 120.0:
                st.warning("## ⚠️ ぎりぎりです")
            else:
                st.error("## ❌ あふれます")

            col_res_left, col_res_right = st.columns([1.2, 1.0])
            
            with col_res_left:
                st.markdown("""
                    <style>
                    [data-testid="stColumn"] > div [data-testid="stMetric"] {
                        padding-left: 20px !important;
                    }
                    </style>
                """, unsafe_allow_html=True)

                r1_c1, r1_c2, r1_c3 = st.columns(3)
                with r1_c1:
                    st.metric(label="安全率", value=f"{margin_ratio / 100.0:.1f}")
                with r1_c2:
                    st.metric(label="流入雨水量 Q ", value=f"{Q_total_in:.4f} m³/s")
                with r1_c3:
                    st.metric(label="設計流量 Q_max", value=f"{Q_design:.4f} m³/s")

                r2_c1, r2_c2 = st.columns([1.0, 2.0])
                with r2_c1:
                    st.metric(label="フルード数 Fr", value=flow_status)
                with r2_c2:
                    st.metric(label="設計流速 V_max", value=v_value_str)

                r3_c1, r3_c2, r3_c3 = st.columns(3)
                with r3_c1:
                    st.metric(label="断面積 A", value=f"{A_design_a:.4f} ㎡")
                with r3_c2:
                    st.metric(label="潤辺 P", value=f"{P_design_a:.4f} m")
                with r3_c3:
                    st.metric(label="径深 R", value=f"{R_design_a:.4f} m")

            with col_res_right:
                if channel_type == "U形":
                    fig_a = draw_section("U形", h_design_a_mm, w_mm=w_a, h_mm=h_a, w_bottom_mm=w_bottom_a, r_bottom_mm=r_bottom_a)
                elif channel_type == "円形":
                    fig_a = draw_section("円形", h_design_a_mm, d_mm=d_a)
                elif channel_type == "台形":
                    fig_a = draw_section("台形", h_design_a_mm, b1_mm=b1_a, b2_mm=b2_a, h_mm=h_a)
                st.pyplot(fig_a, use_container_width=False)
                plt.close(fig_a)

        with st.container(key="checkbox_zone"):
            st.markdown("""
                <style>
                div[data-testid="checkbox_zone"] div[data-testid="stHorizontalBlock"] {
                    margin-top: -15px !important;
                    margin-bottom: -10px !important;
                    align-items: center !important;
                }
                div[data-testid="checkbox_zone"] div[data-testid="stCheckbox"] {
                    padding: 0px !important;
                    margin: 0px !important;
                }
                div[data-testid="checkbox_zone"] div[data-testid="stCheckbox"] label {
                    min-height: auto !important;
                    padding: 0px !important;
                }
                </style>
            """, unsafe_allow_html=True)

            col_opt1_chk, col_opt1_txt, col_opt2_chk, col_opt2_txt = st.columns([0.1, 4.9, 0.1, 4.9])
            
            with col_opt1_chk:
                use_modified_v_a = st.checkbox("", value=False, key="use_modified_v_a", label_visibility="collapsed")
            with col_opt1_txt:
                st.markdown(
                    '<div style="font-size: 22px; font-weight: normal; color: #334155; line-height: 1.3; margin-left: 12px;">'
                    '射流（Fr > 1.0）のときに<br>修正流速（V/Fr）を適用する'
                    '</div>',
                    unsafe_allow_html=True
                )

            with col_opt2_chk:
                add_upstream_a = st.checkbox(
                    "",
                    value=(stored_Q > 0.0),
                    disabled=(stored_Q == 0.0),
                    key="add_upstream_a",
                    label_visibility="collapsed"
                )
            with col_opt2_txt:
                txt_color = "#94a3b8" if stored_Q == 0.0 else "#334155"
                st.markdown(
                    f'<div style="font-size: 22px; font-weight: normal; color: {txt_color}; line-height: 1.3; margin-left: 12px;">'
                    f'上流からの流入量（{stored_Q:.4f} m³/s）を<br>今回の流入雨水量に加算する'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.write("---")
        current_stored_Q = st.session_state["upstream_Q"]

        st.markdown("""
            <style>
            .stored-q-text {
                font-size: 20px !important;
                font-weight: normal !important;
                color: #0f172a !important;
                margin-bottom: 12px !important;
            }
            .stored-q-code {
                font-size: 24px !important;
                font-weight: bold !important;
                background-color: #f1f5f9 !important;
                padding: 2px 8px !important;
                border-radius: 6px !important;
                color: #0284c7 !important;
            }
            div[data-testid="stButton"] button {
                font-size: 20px !important;
                font-weight: normal !important;
                height: 52px !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                padding-top: 0px !important;
                padding-bottom: 0px !important;
            }
            div[data-testid="stButton"] button p,
            div[data-testid="stButton"] button div {
                font-size: 20px !important;
                font-weight: normal !important;
                line-height: 1.0 !important;
                margin: 0px !important;
                padding: 0px !important;
                display: flex !important;
                align-items: center !important;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown(
            f'<div class="stored-q-text">'
            f'💾 上流からの流入雨水量: <span class="stored-q-code">{current_stored_Q:.4f} m³/s</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📥 現在の流入雨水量を記憶する"):
                st.session_state["upstream_Q"] = Q_in_a
                st.rerun()
                
        with col_btn2:
            if st.button("🗑️ 記憶をリセット"):
                st.session_state["upstream_Q"] = 0.0
                st.rerun()

# ====================================================
# 【タブB】機能B：限界集水面積の逆算
# ====================================================
if False:
    with tabB:
        col_left_b, col_space_b, col_right_b = st.columns([1.0, 0.1, 1.4], gap="large")

        # --- 左側：条件入力領域 ---
        with col_left_b:
            st.subheader("⚙️ 条件入力")
            col_sub_left_b, col_sub_right_b = st.columns(2, gap="medium")
            
            with col_sub_left_b:
                channel_type_b = st.selectbox("水路の形状", options=["U形", "円形", "台形"], key="channel_type_b")
                
            with col_sub_right_b:
                material_options_b = {
                    "U形": {"コンクリート(二次製品)": 0.013, "土側溝": 0.025, "石積み側溝": 0.025},
                    "円形": {"塩ビ管": 0.010, "コルゲート管": 0.025},
                    "台形": {"コンクリート(現場打ち)": 0.015, "土側溝": 0.025, "石積み側溝": 0.025}
                }
                available_materials_b = list(material_options_b[channel_type_b].keys())
                
                def update_n_b():
                    st.session_state.n_input_b = material_options_b[channel_type_b][st.session_state.material_b]

                selected_material_b = st.selectbox("水路の種類", options=available_materials_b, key="material_b", on_change=update_n_b)
                default_n_b = material_options_b[channel_type_b][selected_material_b]
                
            if channel_type_b == "U形":
                col_dim_lb, col_dim_rb = st.columns(2, gap="medium")
                with col_dim_lb:
                    w_b = st.number_input("水路幅 B (mm)", min_value=50, max_value=5000, value=300, step=50, key="w_b")
                with col_dim_rb:
                    h_b = st.number_input("水路深 H (mm)", min_value=50, max_value=5000, value=300, step=50, key="h_b")
                
                show_detail_b = st.checkbox("詳細設定（下幅・底面Rを指定する）", value=False, key="show_detail_b")
                if show_detail_b:
                    col_opt_lb, col_opt_rb = st.columns(2, gap="medium")
                    with col_opt_lb:
                        w_bottom_b = st.number_input("下幅 B2 (mm)", min_value=50, max_value=5000, value=290, step=10, key="w_bottom_b")
                    with col_opt_rb:
                        r_bottom_b = st.number_input("底面角 R (mm)", min_value=0, max_value=500, value=30, step=5, key="r_bottom_b")
                else:
                    w_bottom_b, r_bottom_b = None, None
                    
            elif channel_type_b == "円形":
                col_dim_lb, col_dim_rb = st.columns(2, gap="medium")
                with col_dim_lb:
                    d_b = st.number_input("管径 D (mm)", min_value=50, max_value=5000, value=300, step=50, key="d_b")
                    w_b, h_b = d_b, d_b
                with col_dim_rb:
                    st.empty()
                w_bottom_b, r_bottom_b = None, None

            elif channel_type_b == "台形":
                col_dim_lb, col_dim_rb = st.columns(2, gap="medium")
                with col_dim_lb:
                    b1_b = st.number_input("上幅 B1 (mm)", min_value=50, max_value=5000, value=400, step=50, key="b1_b")
                with col_dim_rb:
                    b2_b = st.number_input("下幅 B2 (mm)", min_value=50, max_value=5000, value=300, step=50, key="b2_b")
                
                col_dim2_lb, col_dim2_rb = st.columns(2, gap="medium")
                with col_dim2_lb:
                    h_b = st.number_input("水路深 H (mm)", min_value=50, max_value=5000, value=300, step=50, key="h_b")
                with col_dim2_rb:
                    st.empty()
                w_bottom_b, r_bottom_b = None, None

            st.write("---") 

            col_mid_left_b, col_mid_right_b = st.columns(2, gap="medium")
            with col_mid_left_b:
                I_b = st.number_input("降雨強度 I (mm/h)", min_value=1.0, max_value=300.0, value=50.0, step=1.0, key="I_b")

            with col_mid_right_b:
                st.markdown("<label style='font-size:22px; font-weight:bold;'>勾配</label>", unsafe_allow_html=True)
                with st.container():
                    st.markdown('<div class="compact-row-container">', unsafe_allow_html=True)
                    col_sb_val, col_sb_unit = st.columns([7, 3])
                    with col_sb_unit:
                        s_type_b = st.selectbox("単位", ["‰", "%", "1/N"], label_visibility="collapsed", key="s_type_b")
                    with col_sb_val:
                        if s_type_b == "‰":
                            s_val_b = st.number_input("勾配値 (‰)", min_value=0.0, max_value=100.0, value=5.0, step=0.5, format="%.2f", label_visibility="collapsed", key="s_val_b_per")
                        elif s_type_b == "%":
                            s_val_b = st.number_input("勾配値 (%)", min_value=0.0, max_value=10.0, value=0.5, step=0.1, format="%.2f", label_visibility="collapsed", key="s_val_b_pct")
                        else:
                            s_val_b = st.number_input("Nの値 (1/N)", min_value=1, max_value=10000, value=200, step=10, label_visibility="collapsed", key="s_val_b_n")
                    st.markdown('</div>', unsafe_allow_html=True)

                if "n_input_b" not in st.session_state:
                    st.session_state.n_input_b = default_n_b

                n_b = st.number_input("粗度係数 n", min_value=0.001, max_value=0.100, value=st.session_state.n_input_b, step=0.001, format="%.3f", key="n_input_b")

            col_sub_bottom_left_b, col_sub_bottom_right_b = st.columns(2, gap="medium")
            with col_sub_bottom_left_b:
                C_b = st.slider("流出係数 C", min_value=0.0, max_value=1.0, value=0.9, step=0.05, key="C_b")
            with col_sub_bottom_right_b:
                ratio_b = st.slider("設計水深比 (%)", min_value=10, max_value=100, value=80, step=5, key="ratio_b") / 100.0

        # --- 計算実行（b系統） ---
        if channel_type_b == "U形":
            Q_max_b, V_max_b, h_design_b_mm, A_design_b, P_design_b, R_design_b = calculate_manning(
                shape_type="U形", slope_val=s_val_b, slope_type=s_type_b, roughness_n=n_b, ratio=ratio_b,
                w_mm=w_b, h_mm=h_b, w_bottom_mm=w_bottom_b, r_bottom_mm=r_bottom_b
            )
        elif channel_type_b == "円形":
            Q_max_b, V_max_b, h_design_b_mm, A_design_b, P_design_b, R_design_b = calculate_manning(
                shape_type="円形", slope_val=s_val_b, slope_type=s_type_b, roughness_n=n_b, ratio=ratio_b,
                d_mm=d_b
            )
        elif channel_type_b == "台形":
            Q_max_b, V_max_b, h_design_b_mm, A_design_b, P_design_b, R_design_b = calculate_manning(
                shape_type="台形", slope_val=s_val_b, slope_type=s_type_b, roughness_n=n_b, ratio=ratio_b,
                b1_mm=b1_b, b2_mm=b2_b, h_mm=h_b
            )

        # 限界集水面積 A_limit の計算
        if C_b > 0 and I_b > 0:
            area_ha_limit_b = (360.0 * Q_max_b) / (C_b * I_b)
            area_m2_limit_b = area_ha_limit_b * 10000.0
        else:
            area_ha_limit_b, area_m2_limit_b = 0.0, 0.0

        # --- 右側：逆算結果表示 & 断面描画 ---
        with col_right_b:
            st.subheader("📊 逆算結果")
            
            with st.container(border=True):
                st.info("### 基準をクリアできる最大面積")
                
                col_b_res_left, col_b_res_right = st.columns([1.2, 1.0])

                with col_b_res_left:
                    st.metric(label="限界集水面積 (㎡)", value=f"{area_m2_limit_b:,.1f} ㎡")
                    st.metric(label="限界集水面積 (ha)", value=f"{area_ha_limit_b:.4f} ha")
                    
                    st.markdown("---")
                    st.markdown("**【このときの水路の基本能力】**")
                    col_res_b1, col_res_b2 = st.columns(2)
                    with col_res_b1:
                        st.metric(label="許容通水量 Q_max", value=f"{Q_max_b:.4f} m³/s")
                    with col_res_b2:
                        st.metric(label="許容流速 V_max", value=f"{V_max_b:.2f} m/s")
                        
                    st.caption(f"設計水深: {h_design_b_mm:.0f} mm (余裕高: {h_b - h_design_b_mm:.0f} mm)")
                    st.caption(f"※これ以上の面積になると、降雨強度 {I_b} mm/h の時にあふれます。")

                with col_b_res_right:
                    st.markdown("<h5 style='font-size:20px !important; margin-top:0px !important;'>📐 断面イメージ</h5>", unsafe_allow_html=True)
                    if channel_type_b == "U形":
                        fig_b = draw_section("U形", h_design_b_mm, w_mm=w_b, h_mm=h_b, w_bottom_mm=w_bottom_b)
                    elif channel_type_b == "円形":
                        fig_b = draw_section("円形", h_design_b_mm, d_mm=d_b)
                    elif channel_type_b == "台形":
                        fig_b = draw_section("台形", h_design_b_mm, b1_mm=b1_b, b2_mm=b2_b, h_mm=h_b)
                    st.pyplot(fig_b, use_container_width=False)
