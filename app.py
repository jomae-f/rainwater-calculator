# ====================================================
# ■ 第1章：初期設定・共通基盤
# ====================================================

# ----------------------------------------------------
# 1-1. インポート・ページ設定・CSS定義
# ----------------------------------------------------
import math
import platform
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


def render_figure_inline(fig, width_px, y_offset_px=0, tight_crop=False):
    """Render a Matplotlib figure as inline SVG, avoiding Streamlit's media URL.

    SVG is vector-based, so lines and text remain sharp when the image is scaled.
    The full figure canvas is retained so its intrinsic width/height do not change
    when the channel cross-section becomes taller or wider. This keeps the fixed
    result card from gaining a scrollbar and changing the status band's width.
    ``tight_crop`` is retained for call-site compatibility; section figures use a
    deliberately sized canvas instead of data-dependent cropping.
    """
    buffer = BytesIO()
    fig.savefig(buffer, format="svg", bbox_inches=None)
    svg_b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
    html = (
        f'<div style="display:block; width:{width_px}px; max-width:none; '
        f'margin-top:{y_offset_px}px; margin-right:0; margin-bottom:0; margin-left:0; '
        f'padding:0; line-height:0; overflow:visible;">'
        f'<img alt="図形" src="data:image/svg+xml;base64,{svg_b64}" '
        f'style="display:block; width:{width_px}px !important; '
        f'max-width:none !important; height:auto !important; '
        f'margin:0; padding:0; border:0;" />'
        f'</div>'
    )
    st.html(html)

# ページ基本設定
st.set_page_config(page_title="雨水排水設計ツール", layout="wide")

# スタイル定義（CSS）
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

    /* Tab A: 流域面積・勾配の独自見出しは、通常のウィジェットラベルと同じ間隔にする */
    div[data-testid="stWidgetLabel"].compact-field-heading p {
        margin-bottom: 0 !important;
    }
    .st-key-area_a_controls_row,
    .st-key-slope_a_controls_row {
        margin-top: -8px !important;
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

# アプリケーションタイトル
st.title("🌧️ 雨水排水設計ツール")


# ----------------------------------------------------
# 1-2. セッション状態の初期化
# ----------------------------------------------------
if "upstream_Q" not in st.session_state:
    st.session_state["upstream_Q"] = 0.0


# ----------------------------------------------------
# 1-3. コールバック関数（単位換算・勾配変換）
# ----------------------------------------------------
def convert_area_a():
    new_unit = st.session_state.area_unit_a
    if new_unit == "ha":
        st.session_state.area_val_a = st.session_state.get("area_val_a", 1000.0) / 10000.0
    else:
        st.session_state.area_val_a = st.session_state.get("area_val_a", 0.1000) * 10000.0

def convert_area_b():
    new_unit = st.session_state.basin_area_unit
    if new_unit == "ha":
        st.session_state.a_in_int = st.session_state.get("a_in_int", 3000.0) / 10000.0
        st.session_state.a_dir_int = st.session_state.get("a_dir_int", 0.0) / 10000.0
        st.session_state.a_in_ext = st.session_state.get("a_in_ext", 0.0) / 10000.0
    else:
        st.session_state.a_in_int = st.session_state.get("a_in_int", 0.3) * 10000.0
        st.session_state.a_dir_int = st.session_state.get("a_dir_int", 0.0) * 10000.0
        st.session_state.a_in_ext = st.session_state.get("a_in_ext", 0.0) * 10000.0

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


# タブAの水路形状・材質・粗度係数の対応表。
MATERIAL_OPTIONS_A = {
    "U形": {"コンクリート(二次製品)": 0.013, "土側溝": 0.025, "石積み側溝": 0.025},
    "円形": {"塩ビ管": 0.010, "コルゲート管": 0.025},
    "台形": {"コンクリート(現場打ち)": 0.015, "土側溝": 0.025, "石積み側溝": 0.025},
}


def handle_channel_type_change_a():
    """水路形状の変更時、材質を有効な選択肢に合わせ、粗度係数を連動させる。"""
    shape = st.session_state.get("channel_type_a", "U形")
    choices = MATERIAL_OPTIONS_A[shape]
    material = st.session_state.get("material_a")

    # 変更後の形状で選べない材質なら、その形状の先頭の材質に切り替える。
    if material not in choices:
        material = next(iter(choices))
        st.session_state["material_a"] = material

    # 選択中の材質に対応する標準粗度係数に更新する。
    st.session_state["n_input_a"] = choices[material]


def update_n_a():
    """材質を変更した場合、その材質の標準粗度係数に更新する。"""
    shape = st.session_state.get("channel_type_a", "U形")
    material = st.session_state.get("material_a")
    choices = MATERIAL_OPTIONS_A[shape]
    if material in choices:
        st.session_state["n_input_a"] = choices[material]


def validate_channel_dimensions(shape_type, *, w_mm=None, h_mm=None,
                                w_bottom_mm=None, r_bottom_mm=None,
                                b1_mm=None, b2_mm=None):
    """水路寸法の不整合・描画上の制約を警告文として返す。計算自体は止めない。"""
    warnings = []

    if shape_type == "U形" and w_mm is not None and h_mm is not None:
        if w_bottom_mm is not None and w_bottom_mm > w_mm:
            warnings.append(
                f"下幅 B2（{w_bottom_mm:g} mm）が水路幅 B（{w_mm:g} mm）を上回っています。"
                "一般的なU形断面を想定しているため、幅の入力値を確認してください。"
            )
        elif (w_bottom_mm is not None and r_bottom_mm is not None
              and r_bottom_mm > 0 and w_bottom_mm > 0):
            dx = (w_mm - w_bottom_mm) / 2.0
            alpha = math.atan2(h_mm, dx) if dx > 0 else (math.pi / 2.0)
            tan_half = math.tan((math.pi - alpha) / 2.0)
            max_r_for_drawing = (w_bottom_mm / 2.0) / tan_half if tan_half > 0 else float("inf")
            if r_bottom_mm > max_r_for_drawing:
                warnings.append(
                    f"底面R（{r_bottom_mm:g} mm）が、この幅・深さで図形に反映できる目安"
                    f"（約 {max_r_for_drawing:.0f} mm）を超えています。図ではRが制限される可能性があるため、"
                    "水路幅・下幅・水路深・Rを確認してください。"
                )

    elif shape_type == "台形" and b1_mm is not None and b2_mm is not None:
        if b2_mm > b1_mm:
            warnings.append(
                f"下幅 B2（{b2_mm:g} mm）が上幅 B1（{b1_mm:g} mm）を上回っています。"
                "逆向きの台形断面を意図している場合を除き、幅の入力値を確認してください。"
            )

    return warnings

# ====================================================
# ■ 第2章：計算ロジック
# ====================================================

# ----------------------------------------------------
# 2-1. 水路―水理計算関数
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
# 2-2. 調整池容量・構造―計算関数
# ----------------------------------------------------
def calculate_detention_basin(
    a_in_internal, a_dir_internal, a_in_external,
    f_pre, f_post,
    i_safe, i_50, i_100,
    area_unit="㎡",
    pro_mode=False,
    orifice_depth=0.0, weir_top_w=0.0,
    pipe_slope=0.0
):
    # 単位に応じてha（ヘクタール）に換算
    if area_unit == "㎡":
        a_in_int_ha = a_in_internal / 10000.0
        a_dir_int_ha = a_dir_internal / 10000.0
        a_in_ext_ha = a_in_external / 10000.0
    else:
        a_in_int_ha = a_in_internal
        a_dir_int_ha = a_dir_internal
        a_in_ext_ha = a_in_external

    # 1. 面積の定義
    a1 = a_in_int_ha  # 区域内流入面積
    a2 = a_in_ext_ha  # 区域外流入面積
    total_dev_area = a_in_int_ha + a_dir_int_ha  # 総開発面積（区域内流入 ＋ 区域内直接）

    # 2. 開発前許容量 (Q_pre) と 開発後直接流出量 (Q_dir) の算出
    a_all_ha = a_in_int_ha + a_dir_int_ha
    q_pre = (1.0 / 360.0) * f_pre * i_safe * a_all_ha
    q_dir = (1.0 / 360.0) * f_post * i_50 * a_dir_int_ha
    
    # 3. 調整池からの許容放流量 (Q_allow)
    q_allow = max(0.0, q_pre - q_dir)

    # 4. 許容放流量に対応した逆算降雨強度 (rc)
    if a1 > 0 and f_pre > 0:
        rc = (360.0 * q_allow) / (a1 * f_pre)
    else:
        rc = 0.0

    # 5. 補正係数 alpha の判定（2ha未満: 1, 2ha以上: 2）
    alpha = 2.0 if total_dev_area >= 2.0 else 1.0

    # 6. 必要調整容量の計算 (V1, V2, V)
    ri = i_50    # 流入側降雨強度 (1/50確率)
    t1 = 30.0    # 降雨継続時間 (分)

    # V1: 区域内流入面積に対応する容量
    term1 = (ri * f_post - (rc / 2.0) * f_pre)
    v1 = max(0.0, term1 * alpha * t1 * 60.0 * a1 * (1.0 / 360.0))

    # V2: 区域外流入面積に対応する容量（流出係数は現況 f_pre を使用）
    term2 = (ri * f_pre - (rc / 2.0) * f_pre)
    v2 = max(0.0, term2 * alpha * t1 * 60.0 * a2 * (1.0 / 360.0))

    # 総必要容量 V = V1 + V2
    v_req = v1 + v2

    # プロモード用の詳細検討（オプション）
    weir_depth_result = 0.0
    pipe_dia_result = 0.0
    orifice_area_result = 0.0

    if pro_mode:
        weir_depth_result = math.cbrt((q_allow ** 2) / (9.8 * (weir_top_w if weir_top_w > 0 else 1.0) ** 2)) if q_allow > 0 else 0.0
        pipe_dia_result = 300.0  # プレースホルダー (mm)
        orifice_area_result = orifice_depth * 0.1  # プレースホルダー (㎡)

    return v_req, v1, v2, q_pre, q_dir, q_allow, rc, weir_res if 'weir_res' in locals() else 0.0, pipe_dia_result, orifice_area_result


# ====================================================
# ■ 第3章：描画・ビジュアル関数
# ====================================================

# ----------------------------------------------------
# 3-1. 水路―断面描画関数
# ----------------------------------------------------
def draw_section(shape_type, h_design_mm, w_mm=None, h_mm=None, w_bottom_mm=None, d_mm=None, b1_mm=None, b2_mm=None, r_bottom_mm=None):
    # 1. 共通プロット設定・ヘルパー関数定義
    plt.close('all')

    # Fixed 500×318 SVG canvas: aspect ratio closely matches the fixed axes limits
    # (x span 2.2 / y span 1.4), so all section types occupy a stable layout box.
    fig, ax = plt.subplots(figsize=(5, 3.18))
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

    # 2. U形断面の計算と描画処理
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

    # 3. 円形断面の計算と描画処理
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

    # 4. 台形断面の計算と描画処理
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

    # 5. 共通レイアウト調整と図の返却
    plt.tight_layout()
    return fig

# ----------------------------------------------------
# 3-2. 調整池・流域―概略図描画関数
# ----------------------------------------------------
def draw_catchment_layout(v_req, a_in_internal, a_dir_internal, a_in_external, area_unit="㎡", pond_area_m2=None):
    # OSを判定して、それぞれの環境に最適なフォントを先頭にする
    os_name = platform.system()
    if os_name == "Windows":
        base_font = "Meiryo"
    elif os_name == "Darwin":  # Macの場合
        base_font = "Hiragino Sans"
    else:  # Linux（Streamlit Cloud）の場合
        base_font = "Noto Sans CJK JP"

    if base_font not in plt.rcParams['font.sans-serif']:
        plt.rcParams['font.sans-serif'].insert(0, base_font)

    # 1. 各エリアの有無とサイズ計算
    has_dir = a_dir_internal > 0
    has_ext = a_in_external > 0

    total_inner = a_in_internal + (a_dir_internal if has_dir else 0.0)
    
    if not has_dir or total_inner == 0:
        width_1 = 9.0
        width_dir = 0.0
    else:
        # まず従来どおり面積比から区域内流入の幅を算出する。
        r1 = a_in_internal / total_inner
        width_1 = max(2.5, min(7.8, 9.0 * r1))
        width_dir = 9.0 - width_1

        # 概略図では直接放流エリアの幅を開発区域全体の40%以下に制限する。
        # 開発区域の全幅は9.0なので、最大幅は9.0 * 0.40 = 3.6。
        # 直接放流面積が極端に大きくても、区域内流入ラベルの表示領域を確保する。
        width_dir = min(width_dir, 3.6)
        width_1 = 9.0 - width_dir
    
    x_split = 0.5 + width_1  # 境界のx座標

    # 縦方向の各要素の高さ
    y_river_top = 1.0
    dev_height = 3.0
    y_dev_top = y_river_top + dev_height  # 4.0

    # 区域外エリアの高さと、グラフ全体の縦の上限 (top_limit)
    if has_ext:
        total_all = total_inner + a_in_external
        ext_ratio = a_in_external / total_all if total_all > 0 else 0.0
        # 従来どおり最小高さ0.8から入力面積比に応じて高さを増やす。
        # 変更点は上限のみ：開発区域と同じ高さ（1:1）まで許容する。
        height_ext = max(0.8, min(dev_height, 0.8 + 2.0 * ext_ratio))
        y_ext_top = y_dev_top + height_ext
        top_limit = y_ext_top + 0.3
    else:
        height_ext = 0.0
        y_ext_top = y_dev_top
        top_limit = 4.5

    # 全体サイズ
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, top_limit)
    ax.axis('off')  # 軸の目盛りを非表示


    # 2. 背景の塗りつぶし（最背面）
    # 河川・水路背景（左右グラデーションフェード）
    nx, ny = 200, 20
    rgba = np.zeros((ny, nx, 4))
    rgba[:, :, 0] = 0.878  # R (#e0f2fe)
    rgba[:, :, 1] = 0.949  # G
    rgba[:, :, 2] = 0.996  # B
    alpha = 0.5 + 0.4 * np.sin(np.linspace(0, np.pi, nx))
    rgba[:, :, 3] = alpha
    ax.imshow(rgba, extent=[0.5, 9.5, 0.2, 1.0], aspect='auto', origin='lower', zorder=1)

    # 開発区域外背景（存在する場合のみ描画）
    if has_ext:
        ext_bg = patches.Rectangle((0.5, y_dev_top), 9.0, height_ext, facecolor='#f1f5f9', edgecolor='none', zorder=1)
        ax.add_patch(ext_bg)

    # 区域内流入エリア 塗りつぶし
    in_box_fill = patches.Rectangle((0.5, y_river_top), width_1, dev_height, facecolor='#dbfee8', edgecolor='none', zorder=1)
    ax.add_patch(in_box_fill)

    # 直接放流エリア 塗りつぶし（存在する場合のみ描画）
    if has_dir and width_dir > 0:
        dir_box_fill = patches.Rectangle((x_split, y_river_top), width_dir, dev_height, facecolor='#ffedd5', edgecolor='none', zorder=1)
        ax.add_patch(dir_box_fill)

    # 調整池 塗りつぶし（左下隅 幅2.1（横長に変更）, 高さ0.9）
    pond_width = 2.1
    pond_height = 0.9
    pond_fill = patches.Rectangle((0.5, y_river_top), pond_width, pond_height, facecolor='#06b6d4', edgecolor='none', zorder=2)
    ax.add_patch(pond_fill)


    # 3. 枠線・ライン（中間層）
    # 河川・水路の上下境界線（左右は枠線なし）
    ax.plot([0.5, 9.5], [1.0, 1.0], color='#0284c7', linewidth=1.5, zorder=3)
    ax.plot([0.5, 9.5], [0.2, 0.2], color='#0284c7', linewidth=1.5, zorder=3)

    # 開発区域外外枠（存在する場合のみ描画）
    if has_ext:
        ext_frame = patches.Rectangle((0.5, y_dev_top), 9.0, height_ext, facecolor='none', edgecolor='#64748b', linewidth=1.5, linestyle='--', zorder=3)
        ax.add_patch(ext_frame)

    # 開発区域全体 - 太い黒枠
    dev_box_frame = patches.Rectangle((0.5, y_river_top), 9.0, dev_height, facecolor='none', edgecolor='#0f172a', linewidth=2.0, zorder=3)
    ax.add_patch(dev_box_frame)

    # 調整池の上・右の青い線
    ax.plot([0.5, 0.5 + pond_width], [y_river_top + pond_height, y_river_top + pond_height], color='#0e7490', linewidth=2.0, zorder=4)
    ax.plot([0.5 + pond_width, 0.5 + pond_width], [y_river_top, y_river_top + pond_height], color='#0e7490', linewidth=2.0, zorder=4)


    # 4. テキスト（前面）
    # 面積表示は入力単位に連動させる。
    # 入力単位が ha の場合は ha の値・表記を維持し、平方メートルの場合は m2 と表示する。
    display_a_in_internal = a_in_internal
    display_a_dir_internal = a_dir_internal
    display_a_in_external = a_in_external
    area_fmt = ',.4f' if area_unit == 'ha' else ',.2f'
    area_label_unit = 'ha' if area_unit == 'ha' else 'm2'

    # pond_area_m2 は常に m2 で渡されるため、入力単位が ha のときだけ ha に換算する。
    if pond_area_m2 is None:
        display_pond_area = 0.0
    elif area_unit == 'ha':
        display_pond_area = pond_area_m2 / 10000.0
    else:
        display_pond_area = pond_area_m2
    pond_fmt = area_fmt
    pond_unit = area_label_unit

    ax.text(5.0, 0.6, '河川・水路', color='#0369a1', fontsize=10, fontweight='bold', ha='center', va='center', zorder=5)
    
    # 河川の波線（左右に3つずつ計6つ配置）
    waves = [
        (1.6, 0.45),  # 1つ目の波
        (2.6, 0.70),  # 2つ目の波
        (3.6, 0.50),  # 3つ目の波
        (6.4, 0.45),  # 4つ目の波
        (7.3, 0.70),  # 5つ目の波
        (8.2, 0.50)   # 6つ目の波
    ]
    
    for wx, wy in waves:
        ax.text(wx, wy, '～', color='#0284c7', fontsize=8.5, alpha=0.6, ha='center', va='center', zorder=4)
    
    # 開発区域外の左上ラベルとテキスト
    if has_ext:
        ax.text(0.7, y_dev_top + height_ext - 0.25, '開発区域外', fontsize=10, fontweight='bold', color='#475569', va='center', zorder=5)
        text_ext_y = y_dev_top + height_ext / 2
        ax.text(5.0, text_ext_y + 0.15, '調整池流入', fontsize=9.5, fontweight='bold', color='#475569', ha='center', va='center', zorder=5, clip_on=False)
        ax.text(5.0, text_ext_y - 0.15, f'{display_a_in_external:{area_fmt}} {area_label_unit}', fontsize=9, color='#334155', ha='center', va='center', zorder=5)
    
    # 開発区域の左上ラベル
    ax.text(0.7, y_dev_top - 0.25, '開発区域', fontsize=10, fontweight='bold', color='#0f172a', va='center', zorder=5)
    
    # 区域内流入（調整池流入）のテキスト
    in_cy = y_river_top + dev_height / 2
    ax.text(0.5 + width_1 / 2, in_cy + 0.15, '調整池流入', fontsize=9.5, fontweight='bold', color='#166534', ha='center', va='center', zorder=5, clip_on=False)
    ax.text(0.5 + width_1 / 2, in_cy - 0.15, f'{display_a_in_internal:{area_fmt}} {area_label_unit}', fontsize=9, color='#14532d', ha='center', va='center', zorder=5)

    # 直接放流エリアのテキスト
    if has_dir and width_dir > 0:
        dir_cx = x_split + width_dir / 2
        ax.text(dir_cx, in_cy + 0.15, '直接放流', fontsize=9.5, fontweight='bold', color='#c2410c', ha='center', va='center', zorder=5)
        ax.text(dir_cx, in_cy - 0.15, f'{display_a_dir_internal:{area_fmt}} {area_label_unit}', fontsize=9, color='#9a3412', ha='center', va='center', zorder=5)

    # 調整池テキスト（単位に連動）
    ax.text(0.5 + pond_width / 2, y_river_top + pond_height * 0.65, '調整池', fontsize=10.5, fontweight='bold', color='white', ha='center', va='center', zorder=5)
    ax.text(0.5 + pond_width / 2, y_river_top + pond_height * 0.3, f'{display_pond_area:{pond_fmt}} {pond_unit}', fontsize=10, fontweight='bold', color='white', ha='center', va='center', zorder=5)


    # 5. 矢印とフローのラベル（最前面）
    arrow_edge = '#ffffff'
    arrow_lw = 1.0

    # ① 区域外 → 調整池への矢印（垂直方向の直線）
    if has_ext:
        ax.annotate('', xy=(2.2, y_river_top + pond_height * 0.7), xytext=(2.2, y_ext_top - 0.6), 
                    arrowprops=dict(arrowstyle="simple,head_length=0.60,head_width=0.60,tail_width=0.30", 
                                    facecolor='#94a3b8', edgecolor=arrow_edge, lw=arrow_lw), zorder=5)

    # ② 区域内 → 調整池への矢印（水平方向の直線）※緑系に変更
    in_center_x = 0.5 + width_1 / 2
    if in_center_x > pond_width + 0.5:
        ax.annotate('', xy=(0.5 + pond_width - 0.3, y_river_top + pond_height * 0.55), 
                    xytext=(0.5 + pond_width + 1.0, y_river_top + pond_height * 0.55), 
                    arrowprops=dict(arrowstyle="simple,head_length=0.60,head_width=0.60,tail_width=0.30", 
                                    facecolor='#16a34a', edgecolor=arrow_edge, lw=arrow_lw), zorder=5)

    # ③ 調整池 → 河川への放流矢印 (Q_allow)
    ax.annotate('', xy=(0.8, 0.5), xytext=(0.8, 1.2), 
                arrowprops=dict(arrowstyle="simple,head_length=0.75,head_width=0.75,tail_width=0.30", 
                                facecolor='#0284c7', edgecolor=arrow_edge, lw=arrow_lw), zorder=5)

    # ④ 直接放流エリア → 河川への放流矢印 (Q_dir)
    if has_dir and width_dir > 0:
        dir_center_x = x_split + width_dir / 2
        ax.annotate('', xy=(dir_center_x, 0.5), xytext=(dir_center_x, 1.5), 
                    arrowprops=dict(arrowstyle="simple,head_length=0.75,head_width=0.75,tail_width=0.30", 
                                    facecolor='#f97316', edgecolor=arrow_edge, lw=arrow_lw), zorder=5)

    # 上下左右の余白を限界までカット
    plt.tight_layout(pad=0.2)
    return fig

# ====================================================
# ■ 第4章：メイン画面・UI構築
# ====================================================

# ----------------------------------------------------
# 4-1. タブ定義
# ----------------------------------------------------
tabA, tabB = st.tabs(["📋 水路流下能力", "📋 調整池容量・面積"])


# ----------------------------------------------------
# 4-2. 【タブA】水路流下能力
# ----------------------------------------------------
with tabA:
    col_left_a, col_space_a, col_right_a = st.columns([1.0, 0.1, 1.4], gap="large")
    
    # 1. 条件入力領域（左側）
    with col_left_a:
        st.subheader("⚙️ 条件入力")
        col_sub_left, col_sub_right = st.columns(2, gap="medium")
        
        with col_sub_left:
            channel_type = st.selectbox(
                "水路の形状",
                options=["U形", "円形", "台形"],
                key="channel_type_a",
                on_change=handle_channel_type_change_a,
            )
            
        with col_sub_right:
            material_options = MATERIAL_OPTIONS_A
            available_materials = list(material_options[channel_type].keys())

            # 形状変更で選択肢が変わるセレクトボックスを固定プレースホルダー内に配置。
            # 一時的に古い材質セレクトボックスが残って見える再描画を避ける。
            material_selector_slot_a = st.empty()
            selected_material = material_selector_slot_a.selectbox(
                "水路の種類",
                options=available_materials,
                key="material_a",
                on_change=update_n_a,
            )
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

        # 入力寸法の整合性チェック（試作）。寸法入力のすぐ近くに警告を表示する。
        if channel_type == "U形":
            geometry_warnings_a = validate_channel_dimensions(
                "U形", w_mm=w_a, h_mm=h_a,
                w_bottom_mm=w_bottom_a, r_bottom_mm=r_bottom_a,
            )
        elif channel_type == "台形":
            geometry_warnings_a = validate_channel_dimensions(
                "台形", b1_mm=b1_a, b2_mm=b2_a, h_mm=h_a,
            )
        else:
            geometry_warnings_a = []

        if geometry_warnings_a:
            warning_text = "\n\n".join(f"• {message}" for message in geometry_warnings_a)
            st.warning(
                "入力寸法を確認してください。\n\n"
                + warning_text
                + "\n\n警告中も計算は継続します。寸法を確認するまでは、計算結果を参考値として扱ってください。"
            )

        st.write("---") 

        col_mid_left, col_mid_right = st.columns(2, gap="medium")
        with col_mid_left:
            st.markdown('<div data-testid="stWidgetLabel" class="compact-field-heading"><p>流域面積 A</p></div>', unsafe_allow_html=True)
            with st.container(key="area_a_controls_row"):
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
            st.markdown('<div data-testid="stWidgetLabel" class="compact-field-heading"><p>勾配</p></div>', unsafe_allow_html=True)
            with st.container(key="slope_a_controls_row"):
                st.markdown('<div class="compact-row-container">', unsafe_allow_html=True)
                col_s_val, col_s_unit = st.columns([7, 3])
                
                with col_s_unit:
                    s_type_a = st.selectbox(
                        "単位", ["‰", "%", "1/N"], 
                        label_visibility="collapsed", 
                        key="s_type_a",
                        on_change=convert_slope_a
                    )
                    
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

            n_a = st.number_input(
                "粗度係数 n",
                min_value=0.001,
                max_value=0.100,
                value=st.session_state.n_input_a,
                step=0.001,
                format="%.3f",
                key="n_input_a",
            )

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

    # 2. 計算実行
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

    # 3. 判定結果 & 断面描画（右側）
    with col_right_a:
        st.subheader("📊 判定結果")
        
        g = 9.80665
        h_m = h_design_a_mm / 1000.0
        Fr = V_max_a / ((g * h_m) ** 0.5) if h_m > 0.0 else 0.0

        with st.container(height=480, border=True):
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
                render_figure_inline(fig_a, width_px=500, y_offset_px=12, tight_crop=True)
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


# ----------------------------------------------------
# 4-3. 【タブB】調整池容量・面積
# ----------------------------------------------------

# 地域ごとの降雨強度プリセット
RAIN_PRESETS = {
    "中部": {"i_safe": 28.0, "i_50": 122.0, "i_100": 134.0},
    "東部": {"i_safe": 23.0, "i_50": 104.0, "i_100": 114.0},
    "西部": {"i_safe": 22.0, "i_50": 117.0, "i_100": 128.0},
}

def update_rain_by_region():
    region = st.session_state.get("rain_region", "中部")
    preset = RAIN_PRESETS.get(region, RAIN_PRESETS["中部"])
    st.session_state["i_safe_input"] = preset["i_safe"]
    st.session_state["i_50_input"] = preset["i_50"]
    st.session_state["i_100_input"] = preset["i_100"]

with tabB:
    col_left_b, col_space_b, col_right_b = st.columns([1.0, 0.193, 1.4], gap="large")
    
    # 1. 条件入力領域（左側）
    with col_left_b:
        st.subheader("⚙️ 条件入力")
        
        current_unit = st.session_state.get("basin_area_unit", "㎡")
        
        # 単位に応じてステップとフォーマットを切り替え
        if current_unit == "ha":
            step_val = 0.0010
            fmt_val = "%.4f"
        else:
            step_val = 100.0
            fmt_val = None

        st.markdown('<p style="font-size: 24px; font-weight: bold; color: #0f172a; margin-bottom: 8px;">流域面積</p>', unsafe_allow_html=True)
        
        # 初回未登録時のセッション初期値セット
        if "a_in_int" not in st.session_state:
            st.session_state.a_in_int = 3000.0 if current_unit == "㎡" else 0.5
        if "a_dir_int" not in st.session_state:
            st.session_state.a_dir_int = 0.0 if current_unit == "㎡" else 0.2
        if "a_in_ext" not in st.session_state:
            st.session_state.a_in_ext = 0.0 if current_unit == "㎡" else 0.1

        # 4つを1行に横並び
        col_a1, col_a2, col_a3, col_a4 = st.columns([3, 3, 3, 2], gap="medium")
        
        with col_a1:
            st.markdown(f'<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 4px;">区域内調整池流入</p>', unsafe_allow_html=True)
            if current_unit == "㎡":
                a_in_internal = st.number_input("区域内流入", min_value=0.0, step=100.0, key="a_in_int", label_visibility="collapsed")
            else:
                a_in_internal = st.number_input("区域内流入", min_value=0.0, step=0.0010, format="%.4f", key="a_in_int", label_visibility="collapsed")
                
        with col_a2:
            st.markdown(f'<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 4px;">区域内直接放流</p>', unsafe_allow_html=True)
            if current_unit == "㎡":
                a_dir_internal = st.number_input("区域内直接", min_value=0.0, step=100.0, key="a_dir_int", label_visibility="collapsed")
            else:
                a_dir_internal = st.number_input("区域内直接", min_value=0.0, step=0.0010, format="%.4f", key="a_dir_int", label_visibility="collapsed")
            
        with col_a3:
            st.markdown(f'<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 4px;">区域外調整池流入</p>', unsafe_allow_html=True)
            if current_unit == "㎡":
                a_in_external = st.number_input("区域外流入", min_value=0.0, step=100.0, key="a_in_ext", label_visibility="collapsed")
            else:
                a_in_external = st.number_input("区域外流入", min_value=0.0, step=0.0010, format="%.4f", key="a_in_ext", label_visibility="collapsed")
                
        with col_a4:
            st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 4px;">単位</p>', unsafe_allow_html=True)
            area_unit = st.selectbox(
                "面積単位", ["㎡", "ha"], 
                index=0, 
                key="basin_area_unit", 
                label_visibility="collapsed",
                on_change=convert_area_b
            )

        st.markdown('<hr style="margin-top: 4px; margin-bottom: 24px; border: none; border-top: 1px solid #cbd5e1;">', unsafe_allow_html=True)

        # 降雨強度・流出係数トグル
        param_mode = st.toggle("地域(降雨強度)・流出係数選択", value=False)
        
        if param_mode:
            st.markdown('<p style="font-size: 24px; font-weight: bold; color: #0f172a; margin-top: -10px; margin-bottom: 8px;">降雨強度 (mm/h)</p>', unsafe_allow_html=True)
            
            if "rain_region" not in st.session_state:
                st.session_state.rain_region = "中部"
            if "i_safe_input" not in st.session_state:
                st.session_state.i_safe_input = RAIN_PRESETS["中部"]["i_safe"]
            if "i_50_input" not in st.session_state:
                st.session_state.i_50_input = RAIN_PRESETS["中部"]["i_50"]
            if "i_100_input" not in st.session_state:
                st.session_state.i_100_input = RAIN_PRESETS["中部"]["i_100"]

            col_r_region, col_r1, col_r2, col_r3 = st.columns([2, 3, 3, 3], gap="medium")
            
            with col_r_region:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 8px;">地域</p>', unsafe_allow_html=True)
                st.selectbox(
                    "対象地域", ["中部", "東部", "西部"], 
                    key="rain_region", 
                    label_visibility="collapsed",
                    on_change=update_rain_by_region
                )
                
            with col_r1:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 8px;">1/1確率</p>', unsafe_allow_html=True)
                i_safe = st.number_input("1/1確率", step=1.0, key="i_safe_input", label_visibility="collapsed")
                
            with col_r2:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 8px;">1/50確率</p>', unsafe_allow_html=True)
                i_50 = st.number_input("1/50確率", step=1.0, key="i_50_input", label_visibility="collapsed")
                
            with col_r3:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 8px;">1/100確率</p>', unsafe_allow_html=True)
                i_100 = st.number_input("1/100確率", step=1.0, key="i_100_input", label_visibility="collapsed")

            st.markdown('<hr style="margin-top: 16px; margin-bottom: 4px; border: none; border-top: 1px solid #cbd5e1;">', unsafe_allow_html=True)

            st.markdown('<p style="font-size: 24px; font-weight: bold; color: #0f172a; margin-top: 5px; margin-bottom: 8px;">流出係数</p>', unsafe_allow_html=True)
            
            col_rest1, col_rest2 = st.columns(2, gap="medium")
            with col_rest1:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 8px;">開発前</p>', unsafe_allow_html=True)
                f_pre = st.slider("開発前", min_value=0.1, max_value=1.0, value=0.60, step=0.05, key="f_pre_slider", label_visibility="collapsed")

            with col_rest2:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 8px;">開発後</p>', unsafe_allow_html=True)
                f_post = st.slider("開発後", min_value=0.1, max_value=1.0, value=0.90, step=0.05, key="f_post_slider", label_visibility="collapsed")

            st.markdown('<hr style="margin-top: 4px; margin-bottom: 24px; border: none; border-top: 1px solid #cbd5e1;">', unsafe_allow_html=True)
        else:
            f_pre, f_post = 0.60, 0.90
            i_safe = RAIN_PRESETS["中部"]["i_safe"]
            i_50 = RAIN_PRESETS["中部"]["i_50"]
            i_100 = RAIN_PRESETS["中部"]["i_100"]

        # 詳細検討トグル
        pro_mode = st.toggle("詳細検討(未実装)", value=False)
        
        if pro_mode:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 4px;">オリフィス中心水深 (m)</p>', unsafe_allow_html=True)
                orifice_depth = st.number_input("オリフィス中心水深", value=1.5, step=0.1, key="ori_depth_input", label_visibility="collapsed")
            with col2:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 4px;">水通し長-上幅 (m)</p>', unsafe_allow_html=True)
                weir_top_w = st.number_input("水通し長-上幅", value=2.0, step=0.1, key="weir_top_w_input", label_visibility="collapsed")
            with col3:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 4px;">水通し長-下幅 (m)</p>', unsafe_allow_html=True)
                weir_bot_w = st.number_input("水通し長-下幅", value=2.0, step=0.1, key="weir_bot_w_input", label_visibility="collapsed")

            col4, col5, col6 = st.columns(3)
            with col4:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 4px; margin-top: 8px;">放流管勾配 (%)</p>', unsafe_allow_html=True)
                pipe_slope = st.number_input("放流管勾配", value=1.0, step=0.1, format="%.1f", key="pipe_s_input", label_visibility="collapsed")
            with col5:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 4px; margin-top: 8px;">放流管粗度係数</p>', unsafe_allow_html=True)
                pipe_roughness = st.number_input("放流管粗度係数", value=0.013, step=0.001, format="%.3f", key="pipe_r_input", label_visibility="collapsed")
            with col6:
                st.markdown('<p style="font-size: 20px; font-weight: bold; color: transparent; margin-bottom: 4px; margin-top: 8px;">-</p>', unsafe_allow_html=True)
                st.empty()
        else:
            orifice_depth, weir_top_w, weir_bot_w, pipe_slope, pipe_roughness = 0.0, 0.0, 0.0, 0.0, 0.0

    # 2. 判定結果・概略図領域（右側）
    with col_right_b:
        st.subheader("📊 判定結果")
        
        v_req, v1, v2, q_pre, q_dir, q_allow, rc, weir_res, pipe_res, ori_res = calculate_detention_basin(
            a_in_internal=a_in_internal,
            a_dir_internal=a_dir_internal,
            a_in_external=a_in_external,
            f_pre=f_pre,
            f_post=f_post,
            i_safe=i_safe,
            i_50=i_50,
            i_100=i_100,
            area_unit=area_unit,
            pro_mode=pro_mode,
            orifice_depth=orifice_depth if pro_mode else 0.0,
            weir_top_w=weir_top_w if pro_mode else 0.0,
            pipe_slope=pipe_slope if pro_mode else 0.0
        )

        st.markdown("""
            <style>
            div[data-testid="stHorizontalBlock"]:has(input[aria-label="深さ (m)"]) {
                align-items: flex-start !important;
                gap: 0rem !important;
            }
            div[data-testid="stHorizontalBlock"]:has(input[aria-label="深さ (m)"]) > div:nth-child(4) {
                max-width: 150px !important;
                flex: 0 0 150px !important;
                margin-left: -60px !important;
                margin-top: 4px !important;
            }
            div[data-testid="stHorizontalBlock"]:has(input[aria-label="深さ (m)"]) > div:nth-child(4) div[data-testid="stNumberInput"] {
                width: 100% !important;
            }
            div[data-testid="stHorizontalBlock"]:has(input[aria-label="深さ (m)"]) > div:nth-child(4) [data-testid="stWidgetLabel"] p {
                color: #64748b !important;
                font-size: 21px !important;
            }
            </style>
        """, unsafe_allow_html=True)

        if "basin_depth_input" not in st.session_state:
            st.session_state["basin_depth_input"] = 1.0
        current_depth = st.session_state.get("basin_depth_input", 1.0)

        col_space_l, col_cap, col_area, col_depth, col_space_r = st.columns([0.3, 1.2, 1.2, 0.6, 1.0], gap="medium")
        
        with col_space_l:
            st.empty()
            
        with col_cap:
            st.markdown('<p style="font-size: 24px; font-weight: bold; color: #0f172a; margin-bottom: 2px;">必要容量</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 56px; font-weight: bold; color: #0284c7; margin-top: 0px; margin-bottom: 0px; line-height: 1.1;">{v_req:,.2f} <span style="font-size: 36px; font-weight: bold; color: #334155;">m³</span></p>', unsafe_allow_html=True)
            
        with col_area:
            calc_area = v_req / current_depth if current_depth > 0 else 0.0
            st.markdown(f'<p style="font-size: 24px; font-weight: bold; color: #0f172a; margin-bottom: 2px;">必要面積</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 56px; font-weight: bold; color: #0284c7; margin-top: 0px; margin-bottom: 0px; line-height: 1.1;">{calc_area:,.2f} <span style="font-size: 36px; font-weight: bold; color: #334155;">m²</span></p>', unsafe_allow_html=True)
            
        with col_depth:
            basin_depth = st.number_input("深さ (m)", value=1.0, step=0.1, format="%.1f", key="basin_depth_input")
            
        with col_space_r:
            st.empty()

        fig = draw_catchment_layout(
            v_req=v_req,
            a_in_internal=a_in_internal,
            a_dir_internal=a_dir_internal,
            a_in_external=a_in_external,
            area_unit=area_unit,
            pond_area_m2=calc_area
        )
        render_figure_inline(fig, width_px=1080)
        plt.close(fig)

# ====================================================
# 【タブC】機能C：限界集水面積の逆算（現在非表示）
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
                    render_figure_inline(fig_b, width_px=260)
