import streamlit as st

st.set_page_config(page_title="Bill Generator", layout="wide")

# ----------------------------
# MENU DATA (Item: Price)
# ----------------------------
MENU = {
    "Burger": 120,
    "Pizza": 250,
    "Pasta": 180,
    "Sandwich": 90,
    "French Fries": 80,
    "Cold Coffee": 100,
    "Ice Cream": 70,
    "Salad": 110,
    "Soup": 95,
    "Garlic Bread": 85,
}

# ----------------------------
# SESSION STATE
# ----------------------------
if "cart" not in st.session_state:
    st.session_state.cart = {}

st.title("🧾 Bill Generator")

left_col, right_col = st.columns([1, 1.3])

# ----------------------------
# LEFT SIDE - MENU
# ----------------------------
with left_col:
    st.header("Menu")
    for item, price in MENU.items():
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.write(f"**{item}**")
        with c2:
            st.write(f"₹{price}")
        with c3:
            if st.button("Add", key=f"add_{item}"):
                st.session_state.cart[item] = st.session_state.cart.get(item, 0) + 1

# ----------------------------
# RIGHT SIDE - BILL / CART
# ----------------------------
with right_col:
    st.header("Your Bill")

    if not st.session_state.cart:
        st.info("No items added yet. Click 'Add' on a menu item to start.")
    else:
        subtotal = 0

        # header row
        h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
        h1.write("**Item**")
        h2.write("**Qty**")
        h3.write("**Price**")
        h4.write("**Total**")

        for item in list(st.session_state.cart.keys()):
            qty = st.session_state.cart[item]
            price = MENU[item]

            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                st.write(item)
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
                st.write(f"₹{price}")
            with c4:
                st.write(f"₹{price * new_qty}")

            subtotal += price * new_qty

        # remove items whose quantity was set to 0
        st.session_state.cart = {k: v for k, v in st.session_state.cart.items() if v > 0}

        st.divider()
        st.write(f"**Subtotal: ₹{subtotal:.2f}**")

        # GST option
        apply_gst = st.checkbox("Apply GST")
        gst_percent = 0
        if apply_gst:
            gst_percent = st.selectbox("GST %", [5, 12, 18, 28], index=2)

        calc_col, clear_col = st.columns(2)

        with calc_col:
            if st.button("Calculate Bill", type="primary", use_container_width=True):
                gst_amount = subtotal * gst_percent / 100
                total = subtotal + gst_amount

                st.success("Bill Calculated!")
                st.write(f"Subtotal: ₹{subtotal:.2f}")
                if apply_gst:
                    st.write(f"GST ({gst_percent}%): ₹{gst_amount:.2f}")
                st.markdown(f"### Total: ₹{total:.2f}")

        with clear_col:
            if st.button("Clear Cart", use_container_width=True):
                st.session_state.cart = {}
                st.rerun()