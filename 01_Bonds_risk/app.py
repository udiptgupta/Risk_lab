# app.py
from dotenv import load_dotenv
load_dotenv()

import math
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils.db import get_conn
from src.utils.market_data import get_latest_curve, get_yield_curve, get_credit_spread
from src.bond_analytics import price_and_duration as compute_live_metrics


# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
DEFAULT_AS_OF = date(2025, 7, 20)
st.set_page_config(page_title="Synthetic Bond Risk Dashboard", layout="wide")


# ------------------------------------------------------------------
# Data Loaders (cached)
# ------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def load_bonds_df() -> pd.DataFrame:
    """Load base bond info."""
    with get_conn() as conn:
        df = pd.read_sql(
            """
            SELECT bond_id, isin, issuer, maturity_date, coupon_rate, coupon_frequency,
                   face_value, credit_rating
            FROM bonds;
            """,
            conn,
        )
    return df


@st.cache_data(ttl=300, show_spinner=False)
def load_metrics_df(as_of: date) -> pd.DataFrame:
    """Load precomputed risk metrics for a given as_of date."""
    with get_conn() as conn:
        df = pd.read_sql(
            """
            SELECT m.bond_id, m.as_of, m.price, m.macaulay_duration,
                   m.modified_duration, m.convexity
            FROM bond_risk_metrics m
            WHERE m.as_of = %s;
            """,
            conn,
            params=[as_of],
        )
    return df


def get_curve_df(as_of: date) -> pd.DataFrame:
    """Fetch latest curve <= as_of."""
    curve_date = get_latest_curve(as_of)
    if curve_date is None:
        return pd.DataFrame(columns=["Years", "Yield", "CurveDate"])
    rows = get_yield_curve(curve_date)  # [(yrs, yld), ...]
    df = pd.DataFrame(rows, columns=["Years", "Yield"])
    df["CurveDate"] = curve_date
    return df


def get_bond_row(bond_id: int, bonds_df: pd.DataFrame) -> pd.Series:
    row = bonds_df.loc[bonds_df["bond_id"] == bond_id]
    return row.iloc[0] if not row.empty else None


def ensure_numeric(df: pd.DataFrame, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


# ------------------------------------------------------------------
# Layout: sidebar controls
# ------------------------------------------------------------------
st.title("📊 Synthetic Bond Risk Dashboard")

bonds_df = load_bonds_df()
bonds_df = ensure_numeric(bonds_df, ["coupon_rate", "face_value"])

# AS OF DATE (used to pull metrics + curve)
as_of_date = st.sidebar.date_input("Valuation Date", value=DEFAULT_AS_OF)

# Load precomputed metrics for that date
metrics_df = load_metrics_df(as_of_date)
metrics_df = ensure_numeric(metrics_df, ["price", "macaulay_duration", "modified_duration", "convexity"])

# Merge bonds + metrics
df_full = bonds_df.merge(metrics_df, on="bond_id", how="left")

# Sidebar search
search_txt = st.sidebar.text_input("Search ISIN / Issuer", value="")
if search_txt:
    mask = (
        df_full["isin"].str.contains(search_txt, case=False, na=False)
        | df_full["issuer"].str.contains(search_txt, case=False, na=False)
    )
    df_filtered = df_full[mask]
else:
    df_filtered = df_full

# Bond selector
if df_filtered.empty:
    st.sidebar.warning("No bonds match search.")
    selected_bond_id = None
else:
    selected_bond_id = st.sidebar.selectbox(
        "Select Bond",
        df_filtered["bond_id"].tolist(),
        format_func=lambda bid: f"{bid} | {df_filtered.loc[df_filtered['bond_id']==bid,'isin'].iloc[0]}"
    )

# Sidebar: optional recompute live
recompute_live = st.sidebar.checkbox("Recompute analytics live (ignore stored metrics)", value=False)


# ------------------------------------------------------------------
# Tabs
# ------------------------------------------------------------------
tab_single, tab_portfolio, tab_curve = st.tabs(["Single Bond", "Portfolio", "Curve & Scenarios"])


# ------------------------------------------------------------------
# TAB 1: SINGLE BOND ANALYTICS
# ------------------------------------------------------------------
with tab_single:
    st.subheader("Single Bond Analytics")

    if selected_bond_id is None:
        st.info("Select a bond from the sidebar.")
    else:
        # Base bond info
        bond_row = get_bond_row(selected_bond_id, bonds_df)
        st.markdown(f"**Bond ID:** {selected_bond_id}")
        st.markdown(f"**ISIN:** {bond_row['isin']}")
        st.markdown(f"**Issuer:** {bond_row['issuer']}")
        st.markdown(f"**Maturity:** {bond_row['maturity_date']}")
        st.markdown(f"**Coupon Rate:** {float(bond_row['coupon_rate']):.4%}")
        st.markdown(f"**Frequency:** {int(bond_row['coupon_frequency'])}x / year")
        st.markdown(f"**Face Value:** {float(bond_row['face_value']):,.2f}")
        st.markdown(f"**Rating:** {bond_row['credit_rating']}")

        # Analytics: choose stored metrics or live recompute
        if recompute_live:
            metrics = compute_live_metrics(selected_bond_id, as_of_date)
            price_val = metrics["price"]
            mac_dur = metrics["macaulay_duration"]
            mod_dur = metrics["modified_duration"]
            convex = metrics["convexity"]
            cf_data = metrics["cash_flows"]
            metrics_source = "Live"
        else:
            stored = df_full.loc[df_full["bond_id"] == selected_bond_id].iloc[0]
            price_val = stored["price"] if pd.notnull(stored["price"]) else None
            mac_dur = stored["macaulay_duration"] if pd.notnull(stored["macaulay_duration"]) else None
            mod_dur = stored["modified_duration"] if pd.notnull(stored["modified_duration"]) else None
            convex = stored["convexity"] if pd.notnull(stored["convexity"]) else None

            # Fallback to live compute if missing
            if price_val is None:
                metrics = compute_live_metrics(selected_bond_id, as_of_date)
                price_val = metrics["price"]
                mac_dur = metrics["macaulay_duration"]
                mod_dur = metrics["modified_duration"]
                convex = metrics["convexity"]
                cf_data = metrics["cash_flows"]
                metrics_source = "Live (fallback)"
            else:
                # If stored, we don't have per-CF PV; recompute light if user wants to see CF table
                show_cf = st.checkbox("Show cash flow PV detail (compute live)", value=False)
                if show_cf:
                    metrics = compute_live_metrics(selected_bond_id, as_of_date)
                    cf_data = metrics["cash_flows"]
                    metrics_source = "Stored + Live CF"
                else:
                    cf_data = []
                    metrics_source = "Stored"

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Price", f"{price_val:,.2f}" if price_val is not None else "NA")
        col2.metric("MacDur (yrs)", f"{mac_dur:.2f}" if mac_dur is not None else "NA")
        col3.metric("ModDur (yrs)", f"{mod_dur:.2f}" if mod_dur is not None else "NA")
        col4.metric("Convexity", f"{convex:.2f}" if convex is not None else "NA")

        st.caption(f"Metrics source: {metrics_source}")

        # Yield Curve used
        curve_df = get_curve_df(as_of_date)
        if curve_df.empty:
            st.warning("No yield curve available.")
        else:
            st.write(f"### Yield Curve (Date: {curve_df['CurveDate'].iloc[0]})")
            fig_curve = px.line(curve_df, x="Years", y="Yield", markers=True, title="Risk-Free Yield Curve")
            st.plotly_chart(fig_curve, use_container_width=True)

        # Cash Flow PVs
        if cf_data:
            cf_df = pd.DataFrame(cf_data, columns=["Time (yrs)", "Cash Flow", "PV"])
            st.write("### Cash Flow PV Breakdown")
            st.dataframe(cf_df, use_container_width=True)
            cf_fig = px.bar(cf_df, x="Time (yrs)", y="Cash Flow", title="Cash Flow Schedule")
            st.plotly_chart(cf_fig, use_container_width=True)


# ------------------------------------------------------------------
# TAB 2: PORTFOLIO VIEW
# ------------------------------------------------------------------
with tab_portfolio:
    st.subheader("Portfolio Metrics")

    # Filters
    ratings = ["All"] + sorted(df_full["credit_rating"].dropna().unique().tolist())
    rating_sel = st.multiselect("Ratings", ratings, default=["All"])

    df_port = df_full.copy()

    if "All" not in rating_sel:
        df_port = df_port[df_port["credit_rating"].isin(rating_sel)]

    # Duration slider
    dur_min = float(df_port["macaulay_duration"].min(skipna=True)) if not df_port["macaulay_duration"].isna().all() else 0.0
    dur_max = float(df_port["macaulay_duration"].max(skipna=True)) if not df_port["macaulay_duration"].isna().all() else 0.0
    dur_range = st.slider("Macaulay Duration Range (yrs)", min_value=0.0, max_value=max(dur_max, 1.0), value=(0.0, max(dur_max, 1.0)))
    df_port = df_port[
        (df_port["macaulay_duration"].fillna(0.0) >= dur_range[0])
        & (df_port["macaulay_duration"].fillna(0.0) <= dur_range[1])
    ]

    # Display table
    st.write("### Bonds (Filtered)")
    st.dataframe(
        df_port.sort_values(by="macaulay_duration", ascending=False),
        use_container_width=True,
    )

    # Scatter: Price vs Duration
    if not df_port.empty:
        fig_scatter = px.scatter(
            df_port,
            x="macaulay_duration",
            y="price",
            color="credit_rating",
            hover_data=["isin", "issuer", "maturity_date"],
            title="Price vs Macaulay Duration",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Top N longest duration
    st.write("### Top 10 Longest Duration Bonds")
    st.dataframe(
        df_port.nlargest(10, "macaulay_duration")[["bond_id", "isin", "issuer", "macaulay_duration", "price", "credit_rating"]],
        use_container_width=True,
    )


# ------------------------------------------------------------------
# TAB 3: CURVE & SCENARIOS
# ------------------------------------------------------------------
with tab_curve:
    st.subheader("Curve Shock Scenario (Single Bond)")

    if selected_bond_id is None:
        st.info("Select a bond in the sidebar.")
    else:
        # Choose shock amount
        shock_bps = st.slider("Parallel Shift (bps)", min_value=-300, max_value=300, value=0, step=25)

        # Base curve
        curve_df = get_curve_df(as_of_date)
        curve_df["Yield"] = curve_df["Yield"].astype(float)
        if curve_df.empty:
            st.warning("No yield curve available.")
        else:
            # Show base + shocked curve
            curve_df["Yield_Shocked"] = curve_df["Yield"].astype(float) + float(shock_bps) / 10000.0

            fig = px.line(curve_df, x="Years", y="Yield", markers=True, title="Base vs Shocked Yield Curve")
            fig.add_scatter(x=curve_df["Years"], y=curve_df["Yield_Shocked"], mode="lines+markers", name="Shocked")
            st.plotly_chart(fig, use_container_width=True)

            # Reprice bond under shock (simple: add shock to yields, leave spread)
            # We'll reuse the analytics function but override yields via manual PV calc.
            bond_row = get_bond_row(selected_bond_id, bonds_df)
            if bond_row is not None:
                # Build simple CF schedule similar to analytics:
                coupon_rate = float(bond_row["coupon_rate"])
                freq = int(bond_row["coupon_frequency"])
                face_value = float(bond_row["face_value"])
                maturity = pd.to_datetime(bond_row["maturity_date"]).date()
                years_to_mat = (maturity - as_of_date).days / 365.0

                if years_to_mat <= 0:
                    st.error("Bond matured; cannot scenario price.")
                else:
                    n_payments = max(1, math.ceil(years_to_mat * freq))
                    coupon_amt = face_value * (coupon_rate / freq)
                    cf_sched = []
                    for i in range(1, n_payments + 1):
                        t = i / freq
                        amt = coupon_amt
                        if i == n_payments:
                            amt += face_value
                        cf_sched.append((t, amt))

                    # Spread
                    sprd = float(get_credit_spread(bond_row["credit_rating"]) or 0.0)

                    # helper: shocked rf for t
                    curve_pts = list(zip(curve_df["Years"], curve_df["Yield_Shocked"]))
                    def rf_shocked_for_t(t):
                        for yrs, y in curve_pts:
                            if t <= yrs:
                                return y
                        return curve_pts[-1][1]

                    # PV
                    shock_price = 0.0
                    for t, cf in cf_sched:
                        r = rf_shocked_for_t(t) + sprd
                        pv = cf * math.exp(-r * t)
                        shock_price += pv

                    st.metric("Scenario Price", f"{shock_price:,.2f}", help=f"Parallel shift: {shock_bps:+} bps")


# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.write("---")
st.caption("Synthetic Bond Risk Lab — Day 2 build")
