import streamlit as st

st.set_page_config(page_title="Fresh Bites Café - Bill Generator", layout="wide", page_icon="🧾")

# ----------------------------
# STYLING
# ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600..700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap');

.stApp {
    background-color: #FBF7EF;
    font-family: 'Inter', sans-serif;
    color: #29352E;
}

/* Headings */
h1 {
    font-family: 'Fraunces', serif;
    color: #2F4A3C;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin-bottom: 0;
}
h3, h4, h5 {
    font-family: 'Fraunces', serif;
    color: #2F4A3C;
}

/* Card-style containers (st.container(border=True)) */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF;
    border: 1px solid #E6DFD0 !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 8px rgba(47, 74, 60, 0.06);
    margin-bottom: 10px;
    padding: 4px 6px;
}

/* Default buttons (Add to cart) */
div[data-testid="stButton"] button {
    background-color: #2F4A3C;
    color: #FBF7EF;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.4rem 1.2rem;
    transition: background-color 0.2s ease, color 0.2s ease;
}
div[data-testid="stButton"] button:hover {
    background-color: #F2A93B;
    color: #2F4A3C;
}

/* Primary button (Calculate Bill) */
div[data-testid="stButton"] button[kind="primary"] {
    background-color: #F2A93B;
    color: #2F4A3C;
    font-size: 1.05rem;
    border-radius: 8px;
    border: none;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #2F4A3C;
    color: #FBF7EF;
}

/* Number input + select box */
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    border-radius: 8px;
    border-color: #E6DFD0 !important;
}
div[data-testid="stNumberInput"] button {
    background-color: #F4EFE3;
    border-color: #E6DFD0;
}

/* Checkbox label */
div[data-testid="stCheckbox"] label p {
    font-weight: 600;
    color: #2F4A3C;
}

/* Receipt-style amounts */
.receipt-amount {
    font-family: 'IBM Plex Mono', monospace;
    color: #2F4A3C;
}

/* Dashed divider for receipt feel */
.dashed-divider {
    border: none;
    border-top: 2px dashed #C9C2B0;
    margin: 10px 0 14px 0;
}

/* Subtotal line */
.subtotal-line {
    text-align: right;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.05rem;
    font-weight: 600;
    color: #2F4A3C;
    padding-top: 4px;
}

/* Final total box */
.total-box {
    background-color: #2F4A3C;
    color: #FBF7EF;
    border-radius: 12px;
    padding: 16px 20px;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1.8;
    margin-top: 14px;
}
.total-box .grand-total {
    font-size: 1.4rem;
    font-weight: 700;
    color: #F2A93B;
    border-top: 1px dashed #5C766A;
    padding-top: 8px;
    margin-top: 6px;
    display: block;
}

/* Tagline */
.tagline {
    color: #6E7C73;
    font-size: 0.95rem;
    margin-top: 2px;
    margin-bottom: 22px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# MENU DATA (Item: Price)
# ----------------------------
MENU = {
    "🍔 Burger": 120,
    "🍕 Pizza": 250,
    "🍝 Pasta": 180,
    "🥪 Sandwich": 90,
    "🍟 French Fries": 80,
    "🥤 Cold Coffee": 100,
    "🍦 Ice Cream": 70,
    "🥗 Salad": 110,
    "🍲 Soup": 95,
    "🥖 Garlic Bread": 85,
}

# ----------------------------
# SESSION STATE
# ----------------------------
if "cart" not in st.session_state:
    st.session_state.cart = {}

# ----------------------------
# HEADER
# ----------------------------
st.markdown("# 🧾 Fresh Bites Café")
st.markdown("<div class='tagline'>Order from the menu, adjust quantities, and generate your bill</div>", unsafe_allow_html=True)

left_col, right_col = st.columns([1, 1.2], gap="large")

# ----------------------------
# LEFT SIDE - MENU
# ----------------------------
with left_col:
    st.markdown("### 🍽️ Menu")
    for item, price in MENU.items():
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"**{item}**")
            with c2:
                st.markdown(f"<span class='receipt-amount'>₹{price}</span>", unsafe_allow_html=True)
            with c3:
                if st.button("Add", key=f"add_{item}"):
                    st.session_state.cart[item] = st.session_state.cart.get(item, 0) + 1

# ----------------------------
# RIGHT SIDE - BILL / CART
# ----------------------------
with right_col:
    st.markdown("### 🧾 Your Bill")

    if not st.session_state.cart:
        st.info("Your cart is empty. Click **Add** on a menu item to get started.")
    else:
        subtotal = 0

        with st.container(border=True):
            h1c, h2c, h3c, h4c = st.columns([3, 1, 1, 1])
            h1c.markdown("**Item**")
            h2c.markdown("**Qty**")
            h3c.markdown("**Price**")
            h4c.markdown("**Total**")
            st.markdown("<hr class='dashed-divider'>", unsafe_allow_html=True)

            for item in list(st.session_state.cart.keys()):
                qty = st.session_state.cart[item]
                price = MENU[item]

                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                with c1:
                    st.markdown(item)
                with c2:
                    new_qty = st.number_input(
                        "Qty",
                        min_value=0,
                        value=qty,
                        step=1,
                        key=f"qty_{item}",
                        label_visibility="collapsed",
                    )
                    st.session_state.cart[item] = new_qty
                with c3:
                    st.markdown(f"<span class='receipt-amount'>₹{price}</span>", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"<span class='receipt-amount'>₹{price * new_qty}</span>", unsafe_allow_html=True)

                subtotal += price * new_qty

            # remove items whose quantity was set to 0
            st.session_state.cart = {k: v for k, v in st.session_state.cart.items() if v > 0}

            st.markdown("<hr class='dashed-divider'>", unsafe_allow_html=True)
            st.markdown(f"<div class='subtotal-line'>Subtotal: ₹{subtotal:.2f}</div>", unsafe_allow_html=True)

        st.write("")

        # GST option
        apply_gst = st.checkbox("Apply GST")
        gst_percent = 0
        if apply_gst:
            gst_percent = st.selectbox("GST %", [5, 12, 18, 28], index=2)

        calc_col, clear_col = st.columns(2)
        with calc_col:
            calc_clicked = st.button("Calculate Bill", type="primary", use_container_width=True)
        with clear_col:
            if st.button("Clear Cart", use_container_width=True):
                st.session_state.cart = {}
                st.rerun()

        if calc_clicked:
            gst_amount = subtotal * gst_percent / 100
            total = subtotal + gst_amount

            gst_line = f"GST ({gst_percent}%): ₹{gst_amount:.2f}<br>" if apply_gst else ""

            st.markdown(f"""
            <div class='total-box'>
                Subtotal: ₹{subtotal:.2f}<br>
                {gst_line}
                <span class='grand-total'>Total: ₹{total:.2f}</span>
            </div>
            """, unsafe_allow_html=True)