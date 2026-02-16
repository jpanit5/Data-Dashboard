import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Casino Dashboard",
    layout="wide"
)

# -----------------------------
# Language Selector
# -----------------------------
language = st.radio(
    "🌐 Language / 语言",
    ["English", "中文"],
    horizontal=True
)

# -----------------------------
# Translation Dictionary
# -----------------------------
translations = {
    "English": {
        "title": "🎰 Online Casino Dashboard",
        "filters": "Filters",
        "country": "Select Country",
        "game": "Select Game Type",
        "vip": "Select VIP Level",
        "date": "Select Date Range",
        "total_ggr": "Total GGR",
        "total_ngr": "Total NGR",
        "deposit": "Total Deposits",
        "active": "Active Players (7d)",
        "arpu": "ARPU",
        "ggr_country": "GGR by Country",
        "ngr_game": "NGR Distribution by Game Type",
        "monthly": "Monthly GGR Trend",
        "vip_profit": "NGR by VIP Level",
        "footer": "Built with Streamlit | Online Casino Data Analytics"
    },
    "中文": {
        "title": "🎰 在线赌场 仪表板",
        "filters": "筛选",
        "country": "选择国家",
        "game": "选择游戏类型",
        "vip": "选择 VIP 等级",
        "date": "选择日期范围",
        "total_ggr": "总 GGR",
        "total_ngr": "总 NGR",
        "deposit": "总存款",
        "active": "活跃玩家 (7天)",
        "arpu": "每用户平均收入",
        "ggr_country": "各国家 GGR",
        "ngr_game": "游戏类型 NGR 分布",
        "monthly": "每月 GGR 趋势",
        "vip_profit": "VIP 等级 NGR",
        "footer": "使用 Streamlit 构建 | 在线赌场数据分析"
    }
}

st.title(translations[language]["title"])

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Online_Casino_Practice_Dataset.xlsx")

    df["Transaction_Date"] = pd.to_datetime(df["Transaction_Date"])
    df["Last_Login_Date"] = pd.to_datetime(df["Last_Login_Date"])

    df["Game_Type"] = df["Game_Type"].astype(str).str.strip().str.title()

    # Force VIP to categorical ordered
    df["VIP_Level"] = df["VIP_Level"].astype(str).str.strip()
    vip_sorted = sorted(df["VIP_Level"].unique(), key=lambda x: int(x))
    df["VIP_Level"] = pd.Categorical(
        df["VIP_Level"],
        categories=vip_sorted,
        ordered=True
    )

    df["GGR"] = df["Bet_Amount"] - df["Win_Amount"]
    df["NGR"] = df["GGR"] - df["Bonus_Amount"] - df["Payment_Fee"]

    return df


df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header(translations[language]["filters"])

country_filter = st.sidebar.multiselect(
    translations[language]["country"],
    options=df["Country"].unique(),
    default=df["Country"].unique()
)

game_filter = st.sidebar.multiselect(
    translations[language]["game"],
    options=df["Game_Type"].unique(),
    default=df["Game_Type"].unique()
)

vip_filter = st.sidebar.multiselect(
    translations[language]["vip"],
    options=df["VIP_Level"].unique(),
    default=df["VIP_Level"].unique()
)

date_range = st.sidebar.date_input(
    translations[language]["date"],
    [df["Transaction_Date"].min(), df["Transaction_Date"].max()]
)

# -----------------------------
# Apply Filters
# -----------------------------
filtered_df = df[
    (df["Country"].isin(country_filter)) &
    (df["Game_Type"].isin(game_filter)) &
    (df["VIP_Level"].isin(vip_filter)) &
    (df["Transaction_Date"] >= pd.to_datetime(date_range[0])) &
    (df["Transaction_Date"] <= pd.to_datetime(date_range[1]))
].copy()

# -----------------------------
# KPI Calculations
# -----------------------------
total_ggr = filtered_df["GGR"].sum()
total_ngr = filtered_df["NGR"].sum()
total_deposit = filtered_df["Deposit_Amount"].sum()
unique_players = filtered_df["Player_ID"].nunique()

active_players = filtered_df[
    filtered_df["Last_Login_Date"] >= pd.Timestamp.today() - pd.Timedelta(days=7)
]["Player_ID"].nunique()

arpu = total_ngr / unique_players if unique_players > 0 else 0

# -----------------------------
# KPI Display
# -----------------------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(translations[language]["total_ggr"], f"${total_ggr:,.2f}")
col2.metric(translations[language]["total_ngr"], f"${total_ngr:,.2f}")
col3.metric(translations[language]["deposit"], f"${total_deposit:,.2f}")
col4.metric(translations[language]["active"], active_players)
col5.metric(translations[language]["arpu"], f"${arpu:,.2f}")

st.markdown("---")

# -----------------------------
# Charts
# -----------------------------
colA, colB = st.columns(2)

# GGR by Country
ggr_country = filtered_df.groupby("Country", observed=False)["GGR"].sum().reset_index()
fig1 = px.bar(ggr_country, x="Country", y="GGR",
              title=translations[language]["ggr_country"])
colA.plotly_chart(fig1, width="stretch")

# NGR by Game Type
ngr_game = filtered_df.groupby("Game_Type", observed=False)["NGR"].sum().reset_index()
fig2 = px.pie(ngr_game, names="Game_Type", values="NGR",
              title=translations[language]["ngr_game"])
colB.plotly_chart(fig2, width="stretch")

colC, colD = st.columns(2)

# Monthly GGR Trend
filtered_df["Month"] = filtered_df["Transaction_Date"].dt.to_period("M").astype(str)
monthly_ggr = filtered_df.groupby("Month")["GGR"].sum().reset_index()

fig3 = px.line(monthly_ggr, x="Month", y="GGR",
               title=translations[language]["monthly"])
colC.plotly_chart(fig3, width="stretch")

# VIP Profitability (FINAL FIX)
vip_profit = filtered_df.groupby("VIP_Level", observed=False)["NGR"].sum().reset_index()

fig4 = px.bar(
    vip_profit,
    x="VIP_Level",
    y="NGR",
    title=translations[language]["vip_profit"]
)

# 🔥 FORCE categorical axis (THIS FIXES 1.5 / 2.5 ISSUE)
fig4.update_xaxes(type='category')

colD.plotly_chart(fig4, width="stretch")

st.markdown("---")
st.caption(translations[language]["footer"])
