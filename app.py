import streamlit as st
import math

# ページ設定（ワイドモード）
st.set_page_config(page_title="雨水排水設計支援ツール", layout="wide")

# アプリ起動時に、上流雨水量を保持する箱（変数）を用意しておく
if "upstream_Q" not in st.session_state:
    st.session_state["upstream_Q"] = 0.0

# ----------------------------------------------------
# CSSの埋め込み（レイアウト比率を最優先で最適化）
# ----------------------------------------------------
st.markdown("""
    <style>
    /* 1. 入力項目のラベル（見出し文字）：24px */
    div[data-testid="stWidgetLabel"] p,
    label,
    .stSelectbox label p,
    .stNumberInput label p,
    .stSlider label p {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #0f172a !important;
        line-height: 1.4 !important;
        margin-bottom: 8px !important;
    }
    
    /* 2. 【修正】通常の入力ボックスの最大幅を、単位選択ありの行の幅とピタッと揃える */
    div[data-testid="stNumberInput"],
    div[data-testid="stSelectbox"],
    div[data-testid="stSlider"] {
        width: 100% !important;
        max-width: 435px !important; /* ★ 320px から 435px に拡張し、右端を一直線に揃えます */
    }
    
    /* 3. Number Input と Selectbox の外枠・コンテナの高さ設定 */
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stSelectbox"] > div {
        height: 56px !important;
        min-height: 56px !important;
    }
    div[data-baseweb="input"],
    div[data-baseweb="select"],
    div[data-baseweb="base-input"] {
        height: 56px !important;
        min-height: 56px !important;
        border-radius: 8px !important;
    }
    
    /* 4. 入力ボックスの中の文字サイズ（太字解除・ノーマル） */
    input {
        font-size: 24px !important;
        font-weight: normal !important;
        color: #0f172a !important;
        height: 54px !important;
        line-height: 54px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    
    /* 5. Number Input の右側にある「＋/ー」ボタンのサイズと高さを強制固定 */
    div[data-testid="stNumberInput"] button {
        height: 54px !important;
        min-height: 54px !important;
        width: 45px !important;
    }
    div[data-testid="stNumberInput"] button svg {
        transform: scale(1.3) !important;
    }
    
    /* 6. セレクトボックスの内枠と選択中テキスト（太字解除・ノーマル） */
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
    
    /* 7. 【両方拡大版】スライダーの見出しも、中の数字もすべて大きく太くする */
    /* ① 見出し文字の強制拡大 */
    div[data-testid="stSlider"] > label div p,
    div[data-testid="stSlider"] label p {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #0f172a !important;
        line-height: 1.4 !important;
    }
    /* ② 数字部分（現在大きくなっている部分）の維持・確定 */
    div[data-testid="stSlider"] div[data-testid="stWidgetLabel"] + div div p,
    div[data-testid="stSlider"] [role="slider"] div {
        font-size: 22px !important;
        font-weight: bold !important;
    }
    
    /* 8. 各セクションのグループ見出しの余白 */
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
    
    /* 9. タブの中のサブヘッダーの余白調整 */
    h3 {
        font-size: 32px !important;
        font-weight: bold !important;
        margin-top: 0px !important;
        margin-bottom: 5px !important;
    }

    /* 10. タブの文字サイズ */
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

    /* 11. 判定結果カード内の各項目の見出し（文字サイズを24pxに大きくし、太字化） */
    div[data-testid="stMetric"] label[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] {
        font-size: 24px !important;            /* 24pxに大きく設定（お好みで22px〜26pxに微調整も可能です） */
        font-weight: bold !important;          /* くっきり太字に */
        color: #334155 !important;             /* 視認性の良い濃いめのグレー */
        line-height: 1.4 !important;
        margin-bottom: 6px !important;
    }

    /* 【修正】横並びコンテナ全体の最大幅も、他の通常コンポーネントと同一幅に引き伸ばす */
    .compact-row-container {
        max-width: 435px !important; /* ★ ここも 435px に揃えることで完璧に同じ横幅になります */
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌧️ 雨水排水設計支援ツール")

# ----------------------------------------------------
# 共通水理計算関数
# ----------------------------------------------------
def calculate_manning(
    shape_type,
    slope_val,
    slope_type,
    roughness_n,
    ratio,
    # U形用パラメータ
    w_mm=None,
    h_mm=None,
    w_bottom_mm=None,
    r_bottom_mm=None,
    # 円形用パラメータ
    d_mm=None,
    # 台形用パラメータ
    b1_mm=None,
    b2_mm=None
):
    """
    U形（底面R・下幅考慮対応）、円形、台形の各断面に対して、
    マニングの公式に基づき設計水深でのQ_max、V_max、および設計水深(mm)を計算する
    """
    
    # ------------------------------------------------
    # 1. 勾配 S の換算 (共通)
    # ------------------------------------------------
    # ‰, % などの表記揺れ、またはs_type_aの選択肢（"‰", "%", "1/N"）に対応
    if "‰" in slope_type or "パーミル" in slope_type:
        S = slope_val / 1000.0
    elif "%" in slope_type or "パーセント" in slope_type:
        S = slope_val / 100.0
    else:  # 1/N 表示
        S = 1.0 / slope_val if slope_val > 0 else 0.0

    # ------------------------------------------------
    # 2. 各形状ごとの断面積 A (m2) と 潤辺 P (m) の計算
    # ------------------------------------------------
    A_max = 0.0
    P_max = 0.0
    h_design_mm = 0.0

    if shape_type == "U形":
        # ミリメートルからメートルへの変換
        B1 = w_mm / 1000.0
        H = h_mm / 1000.0
        h_design = H * ratio
        h_design_mm = h_design * 1000.0
        
        # 下幅・底面Rのデフォルト（未指定時は矩形）
        B2 = (w_bottom_mm / 1000.0) if w_bottom_mm is not None else B1
        R = (r_bottom_mm / 1000.0) if r_bottom_mm is not None else 0.0
        
        # 側壁の斜辺長
        slope_len = math.sqrt(((B1 - B2) / 2.0)**2 + H**2)
        
        # 設計水深における仮の水面幅 bh
        bh = B2 + (B1 - B2) * (h_design / H)
        
        if R > 0.0:
            if h_design >= R:
                # 1) 水深が底角R以上のとき（Rを完全に水没させている状態）
                # 通常の台形断面から、四角の隅R控除分 (2 - π/2)*R^2 を引く
                A_max = ((B2 + bh) * h_design / 2.0) - (2.0 - math.pi / 2.0) * (R ** 2)
                # 底面 B2 ＋ 側壁長さ 2h(斜辺/高さ) から、直線角部2つ分 2R*(斜辺/高さ + 1) を引き、円弧の濡れ縁 πR を足す
                P_max = B2 + 2.0 * h_design * (slope_len / H) - 2.0 * R * ((slope_len / H) + 1.0) + math.pi * R
            else:
                # 2) 水深が底角R未満のとき（水深が非常に浅く、底のカーブの途中までしか水がない状態）
                # 幾何学的に、円弧の一部を近似。水深比に応じた簡易面積に丸めます。
                A_max = ((B2 + bh) * h_design / 2.0) * (h_design / R)  # 水深がR以下は簡易的な三角・放物線近似
                P_max = B2 + 2.0 * h_design
        else:
            # 3) Rの指定がない（または0）のとき（通常の台形・矩形計算）
            A_max = (B2 + bh) * h_design / 2.0
            P_max = B2 + 2.0 * h_design * (slope_len / H)

    elif shape_type == "円形":
        D = d_mm / 1000.0
        r = D / 2.0
        h_design = D * ratio
        h_design_mm = h_design * 1000.0
        
        # 中心角 theta (ラジアン) の計算
        # cos(theta/2) = (r - h) / r  (※浮力・満水時の逆転防止用のクリップ)
        cos_val = (r - h_design) / r
        cos_val = max(-1.0, min(1.0, cos_val))
        theta = 2.0 * math.acos(cos_val)
        
        # 水断面積 A と 潤辺 P の計算（弓形断面公式）
        if h_design <= r:
            # 半分以下
            A_max = (r ** 2) * (theta - math.sin(theta)) / 2.0
        else:
            # 半分以上（円全体の面積から、上部の空洞部分の面積を引く）
            A_max = (math.pi * (r ** 2)) - ((r ** 2) * ((2.0 * math.pi - theta) - math.sin(2.0 * math.pi - theta)) / 2.0)
            
        P_max = r * theta

    elif shape_type == "台形":
        B1 = b1_mm / 1000.0  # 上幅
        B2 = b2_mm / 1000.0  # 下幅
        H = h_mm / 1000.0    # 総深さ
        h_design = H * ratio
        h_design_mm = h_design * 1000.0
        
        # 斜壁の傾斜から、水深hにおける水面幅 bh を計算
        bh = B2 + (B1 - B2) * (h_design / H)
        
        # 側壁の斜辺長
        slope_len = math.sqrt(((B1 - B2) / 2.0)**2 + H**2)
        
        # 台形の水断面積と濡れ縁
        A_max = (B2 + bh) * h_design / 2.0
        P_max = B2 + 2.0 * h_design * (slope_len / H)

    # ------------------------------------------------
    # 3. マニング公式による流速・流量の算出
    # ------------------------------------------------
    if P_max > 0.0 and S > 0.0:
        R_max = A_max / P_max  # 径深
        V_max = (1.0 / roughness_n) * (R_max ** (2.0 / 3.0)) * (S ** (1.0 / 2.0))
        Q_max = A_max * V_max
    else:
        V_max = 0.0
        Q_max = 0.0

    R_max = A_max / P_max if P_max > 0.0 else 0.0

    return Q_max, V_max, h_design_mm, A_max, P_max, R_max

# ----------------------------------------------------
# メイン画面：タブ切り替え
# ----------------------------------------------------
tabA, tabB = st.tabs(["📋 あふれるか判定", "📐 限界集水面積の逆算"])

# ====================================================
# 【タブA】機能A：あふれるか判定
# ====================================================
with tabA:
    # 【修正】左右の間に「空の列（0.3）」を挟んで、物理的な余白をしっかり作ります
    # 比率は 左：中（空白）：右 ＝ 1.0 : 0.1 : 1.4
    col_left_a, col_space_a, col_right_a = st.columns([1.0, 0.1, 1.4], gap="large")
    
    # --- 左側：条件入力領域 ---
    with col_left_a:
        st.subheader("⚙️ 条件入力")
        
        # 条件入力の中をさらに綺麗な2列に分割（それぞれ最大435px幅で並びます）
        col_sub_left, col_sub_right = st.columns(2, gap="medium")
        
        # --- 1. 最上部に「水路の形状」と「水路の種類」を2列で配置 ---
        with col_sub_left:
            channel_type = st.selectbox(
                "水路の形状",
                options=["U形", "円形", "台形"],
                key="channel_type_a"
            )
            
        with col_sub_right:
            # 形状ごとに選択できる材質とデフォルト粗度係数(n)の定義
            material_options = {
                "U形": {
                    "コンクリート(二次製品)": 0.013,
                    "土側溝": 0.025,
                    "石積み側溝": 0.025
                },
                "円形": {
                    "塩ビ管": 0.010,
                    "コルゲート管": 0.025
                },
                "台形": {
                    "コンクリート(現場打ち)": 0.015,
                    "土側溝": 0.025,
                    "石積み側溝": 0.025
                }
            }
            
            # 選択された形状に対応する材質のリストを取得
            available_materials = list(material_options[channel_type].keys())
            
            # --- コールバック関数の定義 ---
            # 材質が変わったときに、強制的に粗度係数の入力値をデフォルト値に書き換える関数
            def update_n_a():
                # ユーザーが現在選択した材質を取得
                sel_mat = st.session_state.material_a
                # 対応するデフォルトのnを取得
                new_default_n = material_options[channel_type][sel_mat]
                # セッション内の入力ボックスの値を強制上書き
                st.session_state.n_input_a = new_default_n

            selected_material = st.selectbox(
                "水路の種類",
                options=available_materials,
                key="material_a",
                on_change=update_n_a  # ★値が変わったときに上の関数を走らせる
            )
            
            # 選択された材質から、デフォルトの粗度係数 n を決定（初期値連動用）
            default_n = material_options[channel_type][selected_material]
            
        # --- 2. 形状に応じて寸法入力ボックスを切り替える ---
        if channel_type == "U形":
            # 1段目：基本となる上幅と高さを入力
            col_dim_l, col_dim_r = st.columns(2, gap="medium")
            with col_dim_l:
                w_a = st.number_input("水路幅 B (mm)", min_value=50, max_value=5000, value=300, step=50, key="w_a")
            with col_dim_r:
                h_a = st.number_input("水路深 H (mm)", min_value=50, max_value=5000, value=300, step=50, key="h_a")
            
            # 2段目：詳細設定（下幅・底面R）のオプショントグル
            show_detail = st.checkbox("詳細設定（下幅・底面Rを指定する）", value=False, key="show_detail_a")
            
            if show_detail:
                col_opt_l, col_opt_r = st.columns(2, gap="medium")
                with col_opt_l:
                    w_bottom_a = st.number_input("下幅 B2 (mm) ", min_value=50, max_value=5000, value=290, step=10, key="w_bottom_a")
                with col_opt_r:
                    r_bottom_a = st.number_input("底面角 R (mm) ", min_value=0, max_value=500, value=30, step=5, key="r_bottom_a")
            else:
                # チェックがない（―のまま）場合は、計算用に初期値を自動代入
                w_bottom_a = None
                r_bottom_a = None
                
        elif channel_type == "円形":
            col_dim_l, col_dim_r = st.columns(2, gap="medium")
            with col_dim_l:
                d_a = st.number_input("管径 D (mm)", min_value=50, max_value=5000, value=300, step=50, key="d_a")
                w_a = d_a
                h_a = d_a
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

        # 【位置変更】水路の寸法入力がすべて終わったこの位置に区切り線を配置！
        st.write("---") 

        # --- 3. 勾配・流域面積・粗度係数・降雨強度の配置 ---
        col_mid_left, col_mid_right = st.columns(2, gap="medium")
        
        # --- 中段・左ミニ列 ---
        with col_mid_left:
            # 流域面積の設定
            st.markdown("<label style='font-size:22px; font-weight:bold;'>流域面積 A</label>", unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="compact-row-container">', unsafe_allow_html=True)
                col_a_val, col_a_unit = st.columns([7, 3])
                with col_a_unit:
                    area_unit_a = st.selectbox("単位", ["㎡", "ha"], label_visibility="collapsed", key="area_unit_a")
                with col_a_val:
                    if area_unit_a == "㎡":
                        # ★ stepを「1.0」にします。これで「873」のような半端な手入力でも絶対に警告は出ません
                        area_m2_a = st.number_input("流域面積 A (㎡)", min_value=0.0, value=1000.0, step=1.0, label_visibility="collapsed", key="area_m2_a")
                        area_ha_a = area_m2_a / 10000.0
                    else:
                        # ★ ha側も stepを細かく（0.0001）します。これで4桁までの任意の小数が完全フリーで打てます
                        area_ha_a = st.number_input("流域面積 A (ha)", min_value=0.0, value=0.1000, step=0.0001, format="%.4f", label_visibility="collapsed", key="area_ha_a")
                        area_m2_a = area_ha_a * 10000.0
                st.markdown('</div>', unsafe_allow_html=True)

            # 設計降雨強度
            # ★ こちらも stepを「1.0」にします。これで1mm/h刻みの手入力がすべてノーエラーになります
            I_a = st.number_input("降雨強度 I (mm/h)", min_value=0.0, max_value=300.0, value=119.0, step=1.0, key="I_a")

        # --- 中段・右ミニ列 ---
        with col_mid_right:
            # 勾配の設定
            st.markdown("<label style='font-size:22px; font-weight:bold;'>勾配</label>", unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="compact-row-container">', unsafe_allow_html=True)
                col_s_val, col_s_unit = st.columns([7, 3])
                with col_s_unit:
                    s_type_a = st.selectbox("単位", ["‰", "%", "1/N"], label_visibility="collapsed", key="s_type_a")
                with col_s_val:
                    if s_type_a == "‰":
                        s_val_a = st.number_input("勾配値 (‰)", min_value=0.0, max_value=100.0, value=5.0, step=0.5, format="%.2f", label_visibility="collapsed", key="s_val_a_per")
                    elif s_type_a == "%":
                        s_val_a = st.number_input("勾配値 (%)", min_value=0.0, max_value=10.0, value=0.5, step=0.1, format="%.2f", label_visibility="collapsed", key="s_val_a_pct")
                    else:
                        s_val_a = st.number_input("Nの値 (1/N)", min_value=1, max_value=10000, value=200, step=10, label_visibility="collapsed", key="s_val_a_n")
                st.markdown('</div>', unsafe_allow_html=True)

            # --- 復活した粗度係数 n の入力ボックス ---
            # セッション状態に値が入っていない初回だけ初期値を設定
            if "n_input_a" not in st.session_state:
                st.session_state.n_input_a = default_n

            n_a = st.number_input(
                "粗度係数 n", 
                min_value=0.001, 
                max_value=0.100, 
                value=st.session_state.n_input_a,  # ★常にセッション状態の値を参照させる
                step=0.001, 
                format="%.3f", 
                key="n_input_a"
            )

        # --- 4. 最下段（スライダー） ---
        col_sub_bottom_left, col_sub_bottom_right = st.columns(2, gap="medium")
        with col_sub_bottom_left:
            C_a = st.slider("流出係数 C", min_value=0.0, max_value=1.0, value=0.9, step=0.05, key="C_a")
        with col_sub_bottom_right:
            ratio_a = st.slider("水深比 (%)", min_value=10, max_value=100, value=80, step=5, key="ratio_a") / 100.0

    # --- 計算実行 ---
    # 形状ごとに必要な引数のみを、新しい calculate_manning 関数に引き渡します
    if channel_type == "U形":
        Q_max_a, V_max_a, h_design_a_mm, A_design_a, P_design_a, R_design_a = calculate_manning(
            shape_type="U形",
            slope_val=s_val_a,
            slope_type=s_type_a,
            roughness_n=n_a,
            ratio=ratio_a,
            w_mm=w_a,
            h_mm=h_a,
            w_bottom_mm=w_bottom_a,
            r_bottom_mm=r_bottom_a
        )
    elif channel_type == "円形":
        Q_max_a, V_max_a, h_design_a_mm, A_design_a, P_design_a, R_design_a = calculate_manning(
            shape_type="円形",
            slope_val=s_val_a,
            slope_type=s_type_a,
            roughness_n=n_a,
            ratio=ratio_a,
            d_mm=d_a
        )
    elif channel_type == "台形":
        Q_max_a, V_max_a, h_design_a_mm, A_design_a, P_design_a, R_design_a = calculate_manning(
            shape_type="台形",
            slope_val=s_val_a,
            slope_type=s_type_a,
            roughness_n=n_a,
            ratio=ratio_a,
            b1_mm=b1_a,
            b2_mm=b2_a,
            h_mm=h_a
        )

    # 流入雨水量の計算（これは全形状共通）
    Q_in_a = (1.0 / 360.0) * C_a * I_a * area_ha_a

# --- 右側：結果表示 ---
    with col_right_a:
        st.subheader("📊 判定結果")
        
        # 1. フルード数 (Fr) の事前計算
        g = 9.80665
        h_m = h_design_a_mm / 1000.0  # 設計水深をメートルに変換
        if h_m > 0.0:
            Fr = V_max_a / ((g * h_m) ** 0.5)
        else:
            Fr = 0.0

        # --- 判定結果のボックス（コンテナ）開始 ---
        with st.container(border=True):
            
            # セッション状態からチェックボックスのON/OFFを読み取る
            use_modified_v_a = st.session_state.get("use_modified_v_a", False)

            # 2. オプションの適用状態とフルード数による分岐処理 ＆ 表示テキストの動的決定
            if use_modified_v_a and Fr > 1.0:
                V_design = V_max_a / Fr
                Q_design = Q_max_a / Fr
                flow_status = f"{Fr:.2f}&emsp;射流"
                v_value_str = f"{V_design:.2f} m/s (修正流速)"
            else:
                V_design = V_max_a
                Q_design = Q_max_a
                v_value_str = f"{V_design:.2f} m/s"
                if Fr > 1.0:
                    flow_status = f"{Fr:.2f}&emsp;射流"
                elif Fr > 0.0:
                    flow_status = f"{Fr:.2f}&emsp;常流"
                else:
                    flow_status = f"0.00&emsp;静止"

            # ========================================================
            # 【ロジックのみ先行処理】
            # ========================================================
            stored_Q = st.session_state.get("upstream_Q", 0.0)
            
            # 画面下部にあるチェックボックスの状態を先読みして計算に反映
            add_upstream = st.session_state.get("add_upstream_a", False) if stored_Q > 0.0 else False

            # 加算判定
            Q_total_in = Q_in_a + stored_Q if add_upstream else Q_in_a

            # 4. 安全率の計算
            margin_ratio = (Q_design / Q_total_in * 100) if Q_total_in > 0 else 0

            # 3. 「流れます」「ぎりぎりです」「あふれます」の判定
            if margin_ratio >= 120.0:
                st.success("## ⭕ 流れます")
            elif 100.0 <= margin_ratio < 120.0:
                st.warning("## ⚠️ ぎりぎりです")
            else:
                st.error("## ❌ あふれます")

            # 5. 3列×3行（計9項目）のグリッドレイアウト
            col_space, col_res_a1, col_res_a2, col_res_a3 = st.columns([0.2, 3, 3, 3])
            
            # --- 1列目（左列） ---
            with col_res_a1:
                st.metric(label="安全率", value=f"{margin_ratio / 100.0:.1f}")
                st.metric(label="設計流速 V_max", value=v_value_str)
                st.metric(label="断面積 A", value=f"{A_design_a:.4f} ㎡")
                
            # --- 2列目（中央列） ---
            with col_res_a2:
                st.metric(label="流入雨水量 Q ", value=f"{Q_in_a:.4f} m³/s")
                st.metric(label="フルード数 Fr", value=flow_status)
                st.metric(label="潤辺 P", value=f"{P_design_a:.4f} m")
                
            # --- 3列目（右列） ---
            with col_res_a3:
                st.metric(label="設計流量 Q_max", value=f"{Q_design:.4f} m³/s")
                
                st.markdown(
                    """
                    <style>
                    /* 空のmetricでも高さを他と全く同じに維持させる */
                    div[data-testid="stMetric"] {
                        min-height: 78px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.metric(label=" ", value=" ")  # 半角スペースを入れて表示領域を確保
                st.metric(label="径深 R", value=f"{R_design_a:.4f} m")

            # （上の st.container(border=True) のインデントの終わり）
            # ⚠️ ここにあった st.write("") は完全に削除しました！

        # ========================================================
        # 🚀【階層変更版】隙間をさらに限界まで詰める専用コンテナ
        # ========================================================
        with st.container(key="checkbox_zone"):
            st.markdown(
                """
                <style>
                /* 1. チェックボックスの文字を太字にしない ＆ \n での改行を有効にする指定 */
                div[data-testid="stCheckbox"] label p {
                    font-weight: normal !important;
                    white-space: pre-line !important; 
                }
                
                /* 2. 【変更】チェックボックスが配置されている「列のコンテナ（HorizontalBlock）」自体を上に引き上げる */
                div[data-testid="checkbox_zone"] div[data-testid="stHorizontalBlock"] {
                    margin-top: -35px !important;    /* 💡 動かない場合はここを -35px, -40px に増やしてみてください */
                    margin-bottom: 0px !important;
                }
                
                /* 3. 各要素の無駄なパディングも合わせてゼロ化 */
                div[data-testid="checkbox_zone"] div[data-testid="element-container"] {
                    padding-top: 0px !important;
                    padding-bottom: 0px !important;
                    margin-top: 0px !important;
                    margin-bottom: 0px !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            # 要素の間隔を最小（small）に指定した2列を固定配置
            col_opt1, col_opt2 = st.columns([5.0, 5.0], gap="small")
            
            with col_opt1:
                use_modified_v_a = st.checkbox(
                    "射流（Fr > 1.0）のときに\n修正流速（V/Fr）を適用する", 
                    value=False, 
                    key="use_modified_v_a"
                )
            with col_opt2:
                st.checkbox(
                    f"上流からの流入量（{stored_Q:.4f} m³/s）を\n今回の流入雨水量に加算する", 
                    value=True if stored_Q > 0.0 else False,
                    disabled=(stored_Q == 0.0),
                    key="add_upstream_a"
                )

        # --- 【追加】上流流入量の記憶機能 ---
        st.write("---")  # 区切り線
        
        # 現在記憶している上流の流量を表示
        current_stored_Q = st.session_state["upstream_Q"]
        st.write(f"💾 **現在記憶している上流からの流入量**: `{current_stored_Q:.4f} m³/s`")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            # 今回の流入雨水量を上流として記憶するボタン
            if st.button("📥 この流入雨水量を記憶する"):
                st.session_state["upstream_Q"] = Q_in_a
                st.rerun()  # 画面を再更新して表示を更新
                
        with col_btn2:
            # 記憶をクリアするボタン
            if st.button("🗑️ 記憶をリセット"):
                st.session_state["upstream_Q"] = 0.0
                st.rerun()
                
# ====================================================
# 【タブB】機能B：限界集水面積の逆算
# ====================================================
with tabB:
    # 3カラムに分割（仕様入力、気象入力、右側グラフ/結果表示用）
    col_spec_b, col_rain_b, col_right_b = st.columns([1, 1, 3], gap="large")

    # --- 左側：水路の仕様入力エリア (col_spec_b) ---
    with col_spec_b:
        st.markdown("### 📐 水路の仕様")
        
        # 1. 水路の形状の選択
        channel_type_b = st.selectbox(
            "水路の形状",
            options=["U形", "円形", "台形"],
            key="channel_type_b"
        )
        
        # 形状ごとの材質とデフォルト粗度係数のマッピング
        material_options_b = {
            "U形": {
                "コンクリート(二次製品)": 0.013,
                "土側溝": 0.025,
                "石積み側溝": 0.025
            },
            "円形": {
                "塩ビ管": 0.010,
                "コルゲート管": 0.025
            },
            "台形": {
                "コンクリート(現場打ち)": 0.015,
                "土側溝": 0.025,
                "石積み側溝": 0.025
            }
        }
        
        # 2. 水路の材質の選択
        available_materials_b = list(material_options_b[channel_type_b].keys())
        selected_material_b = st.selectbox(
            "水路の材質",
            options=available_materials_b,
            key="material_b"
        )
        
        # デフォルト粗度係数
        default_n_b = material_options_b[channel_type_b][selected_material_b]
        
        # 3. 形状に応じた寸法入力の切り替え
        if channel_type_b == "U形":
            w_b = st.number_input("水路幅 B (mm)", min_value=50, max_value=5000, value=300, step=50, key="w_b")
            h_b = st.number_input("水路深 H (mm)", min_value=50, max_value=5000, value=300, step=50, key="h_b")
            
            # 詳細設定（下幅・底面R）
            show_detail_b = st.checkbox("詳細設定（下幅・底面Rを指定）", value=False, key="show_detail_b")
            if show_detail_b:
                w_bottom_b = st.number_input("下幅 B2 (mm) [初期値: ―]", min_value=50, max_value=5000, value=290, step=10, key="w_bottom_b")
                r_bottom_b = st.number_input("底面角 R (mm) [初期値: ―]", min_value=0, max_value=500, value=30, step=5, key="r_bottom_b")
            else:
                w_bottom_b = None
                r_bottom_b = None
                
        elif channel_type_b == "円形":
            d_b = st.number_input("管径 D (mm)", min_value=50, max_value=5000, value=300, step=50, key="d_b")
            # 内部計算用のダミー
            w_b = d_b
            h_b = d_b
            w_bottom_b = None
            r_bottom_b = None

        elif channel_type_b == "台形":
            b1_b = st.number_input("上幅 B1 (mm)", min_value=50, max_value=5000, value=400, step=50, key="b1_b")
            b2_b = st.number_input("下幅 B2 (mm)", min_value=50, max_value=5000, value=300, step=50, key="b2_b")
            h_b = st.number_input("水路深 H (mm)", min_value=50, max_value=5000, value=300, step=50, key="h_b")
            w_bottom_b = None
            r_bottom_b = None

    # --- 中央：雨量・勾配などの仕様入力エリア (col_rain_b) ---
    with col_rain_b:
        st.markdown("### 🌧️ 雨量・勾配仕様")
        
        # 勾配の設定
        st.markdown("<label style='font-weight:bold;'>勾配</label>", unsafe_allow_html=True)
        col_s_val_b, col_s_unit_b = st.columns([7, 3])
        with col_s_unit_b:
            s_type_b = st.selectbox("単位", ["‰", "%", "1/N"], label_visibility="collapsed", key="s_type_b")
        with col_s_val_b:
            if s_type_b == "‰":
                s_val_b = st.number_input("勾配値 (‰)", min_value=0.0, max_value=100.0, value=5.0, step=0.5, format="%.2f", label_visibility="collapsed", key="s_val_b_per")
            elif s_type_b == "%":
                s_val_b = st.number_input("勾配値 (%)", min_value=0.0, max_value=10.0, value=0.5, step=0.1, format="%.2f", label_visibility="collapsed", key="s_val_b_pct")
            else:
                s_val_b = st.number_input("Nの値 (1/N)", min_value=1, max_value=10000, value=200, step=10, label_visibility="collapsed", key="s_val_b_n")

        # 粗度係数 n (材質連動＋手動調整可能)
        n_b = st.number_input(
            "粗度係数 n", 
            min_value=0.001, 
            max_value=0.100, 
            value=default_n_b, 
            step=0.001, 
            format="%.3f", 
            key="n_input_b"
        )
        
        # 流出係数・降雨強度
        I_b = st.number_input("降雨強度 I (mm/h)", min_value=1.0, max_value=300.0, value=50.0, step=5.0, key="I_b")
        C_b = st.slider("流出係数 C", min_value=0.0, max_value=1.0, value=0.9, step=0.05, key="C_b")
        ratio_b = st.slider("設計水深比 (%)", min_value=10, max_value=100, value=80, step=5, key="ratio_b") / 100.0

    # --- 計算実行（b系統） ---
    # 形状ごとに新しい「calculate_manning」関数に正しく引数を渡して計算します
    if channel_type_b == "U形":
        Q_max_b, V_max_b, h_design_b_mm, A_design_b, P_design_b, R_design_b = calculate_manning(
            shape_type="U形",
            slope_val=s_val_b,
            slope_type=s_type_b,
            roughness_n=n_b,
            ratio=ratio_b,
            w_mm=w_b,
            h_mm=h_b,
            w_bottom_mm=w_bottom_b,
            r_bottom_mm=r_bottom_b
        )
    elif channel_type_b == "円形":
        Q_max_b, V_max_b, h_design_b_mm = calculate_manning(
            shape_type="円形",
            slope_val=s_val_b,
            slope_type=s_type_b,
            roughness_n=n_b,
            ratio=ratio_b,
            d_mm=d_b
        )
    elif channel_type_b == "台形":
        Q_max_b, V_max_b, h_design_b_mm = calculate_manning(
            shape_type="台形",
            slope_val=s_val_b,
            slope_type=s_type_b,
            roughness_n=n_b,
            ratio=ratio_b,
            b1_mm=b1_b,
            b2_mm=b2_b,
            h_mm=h_b
        )

    # 限界集水面積 A_limit の計算（流出量Q_maxから流域面積を逆算する機能用）
    # Q = (1/360) * C * I * A  ==>  A = (360 * Q) / (C * I) (ha)
    if C_b > 0 and I_b > 0:
        area_ha_limit_b = (360.0 * Q_max_b) / (C_b * I_b)
        area_m2_limit_b = area_ha_limit_b * 10000.0
    else:
        area_ha_limit_b = 0.0
        area_m2_limit_b = 0.0

    max_area_m2 = area_m2_limit_b
    max_area_ha = area_ha_limit_b

    # --- 3列目（右端：60%）：逆算結果 ---
    with col_right_b:
        st.subheader("📊 逆算結果")
        
        # 限界値の表示カード
        with st.container(border=True):
            st.info("### 基準をクリアできる最大面積")
            
            st.metric(label="限界集水面積 (㎡)", value=f"{max_area_m2:,.1f} ㎡")
            st.metric(label="限界集水面積 (ha)", value=f"{max_area_ha:.4f} ha")
            
            st.markdown("---")
            st.markdown("**【このときの水路の基本能力】**")
            col_res_b1, col_res_b2 = st.columns(2)
            with col_res_b1:
                st.metric(label="許容通水量 Q_max", value=f"{Q_max_b:.4f} m³/s")
            with col_res_b2:
                st.metric(label="許容流速 V_max", value=f"{V_max_b:.2f} m/s")
                
            st.caption(f"設計水深: {h_design_b_mm:.0f} mm (余裕高: {h_b - h_design_b_mm:.0f} mm)")
            st.caption(f"※これ以上の面積になると、降雨強度 {I_b} mm/h の時にあふれます。")