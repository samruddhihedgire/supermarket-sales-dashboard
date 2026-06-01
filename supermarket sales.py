import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Supermarket Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)


st.markdown("""
<style>

/* ---------------- KPI CARDS ---------------- */

[data-testid="metric-container"] {
    padding: 12px !important;
    border-radius: 10px;
}

[data-testid="stMetricLabel"] {
    font-size: 15px !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 700 !important;
}

/* ---------------- SECTION HEADINGS ---------------- */

h4 {
    font-size: 20px !important;
    font-weight: 600 !important;
    margin-bottom: 10px !important;
}

h5 {
    font-size: 18px !important;
    font-weight: 600 !important;
    margin-bottom: 10px !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------- LOAD DATA --------------------
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        "supermarkt_sales.xlsx",
        engine="openpyxl",
        header=3,
        usecols="B:R"
    )

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    df["Month"] = df["Date"].dt.month_name()
    df["Month_Num"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day_name()
    df["Year"] = df["Date"].dt.year

    return df

df = get_data_from_excel()

# -------------------- SIDEBAR --------------------
st.sidebar.title("🛒 Supermarket Dashboard")

page = st.sidebar.radio(
    "Select Page",
    [
        "📊 Sales Overview",
        "👥 Customer Insights",
        "📦 Product & Data View"
    ]
)

st.sidebar.caption(
    f"Data available from {df['Date'].min().date()} to {df['Date'].max().date()}"
)

start_date = st.sidebar.date_input(
    "Start Date",
    value=df["Date"].min().date()
)

end_date = st.sidebar.date_input(
    "End Date",
    value=df["Date"].max().date()
)

city = st.sidebar.multiselect(
    "Select City",
    sorted(df["City"].dropna().unique())
)

branch = st.sidebar.multiselect(
    "Select Branch",
    sorted(df["Branch"].dropna().unique())
)

product = st.sidebar.multiselect(
    "Select Product Line",
    sorted(df["Product line"].dropna().unique())
)

payment = st.sidebar.multiselect(
    "Select Payment",
    sorted(df["Payment"].dropna().unique())
)

# -------------------- FILTER LOGIC --------------------
df_filtered = df.copy()

start_datetime = pd.to_datetime(start_date)
end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1)

df_filtered = df_filtered[
    (df_filtered["Date"] >= start_datetime) &
    (df_filtered["Date"] < end_datetime)
]

if city:
    df_filtered = df_filtered[df_filtered["City"].isin(city)]

if branch:
    df_filtered = df_filtered[df_filtered["Branch"].isin(branch)]

if product:
    df_filtered = df_filtered[df_filtered["Product line"].isin(product)]

if payment:
    df_filtered = df_filtered[df_filtered["Payment"].isin(payment)]

if df_filtered.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# -------------------- KPI CALCULATIONS --------------------
total_sales = df_filtered["Total"].sum()
revenue = df_filtered["Total"].sum()
gross_income = df_filtered["gross income"].sum()
total_quantity = df_filtered["Quantity"].sum()
total_orders = df_filtered["Invoice ID"].nunique()
avg_sale = df_filtered["Total"].mean()
avg_rating = df_filtered["Rating"].mean()

top_city = df_filtered.groupby("City")["Total"].sum().idxmax()
top_product = df_filtered.groupby("Product line")["Total"].sum().idxmax()

top_product_revenue = (
    df_filtered.groupby("Product line")["Total"]
    .sum()
    .max()
)

# -------------------- DOWNLOAD BUTTON --------------------
csv = df_filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Filtered Data",
    csv,
    "filtered_supermarket_sales.csv",
    "text/csv"
)

# -------------------- PAGE 1 --------------------
if page == "📊 Sales Overview":

    st.title("🛒 Supermarket Sales Dashboard")
    st.caption("Executive Analytics & Business Insights")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
    col2.metric("📊 Revenue", f"${revenue:,.0f}")
    col3.metric("🛒 Quantity", f"{total_quantity:,}")
    col4.metric("🧾 Orders", f"{total_orders:,}")

    col5, col6, col7, col8 = st.columns(4)

    col5.metric("💵 Gross Income", f"${gross_income:,.0f}")
    col6.metric("📈 Avg Sale", f"${avg_sale:,.2f}")
    col7.metric("⭐ Avg Rating", f"{avg_rating:.2f}")
    col8.metric("🏙️ Top City", top_city)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        sales_city = (
            df_filtered.groupby("City")["Total"]
            .sum()
            .reset_index()
            .sort_values("Total", ascending=False)
        )

        fig = px.bar(
            sales_city,
            x="City",
            y="Total",
            title="Sales by City",
            color="City",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        daily_sales = (
            df_filtered.groupby("Date")["Total"]
            .sum()
            .reset_index()
        )

        fig = px.line(
            daily_sales,
            x="Date",
            y="Total",
            title="Daily Sales Trend",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        branch_sales = (
            df_filtered.groupby("Branch")["Total"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            branch_sales,
            names="Branch",
            values="Total",
            title="Sales Share by Branch",
            hole=0.45
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        payment_sales = (
            df_filtered.groupby("Payment")["Total"]
            .sum()
            .reset_index()
            .sort_values("Total", ascending=False)
        )

        fig = px.bar(
            payment_sales,
            x="Payment",
            y="Total",
            title="Sales by Payment Method",
            color="Payment",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Sales Heatmap")

    heatmap_data = (
        df_filtered.groupby(["Month", "Day"])["Total"]
        .sum()
        .reset_index()
    )

    fig = px.density_heatmap(
        heatmap_data,
        x="Day",
        y="Month",
        z="Total",
        title="Sales Heatmap by Day and Month",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------- PAGE 2 --------------------
elif page == "👥 Customer Insights":

    st.title("👥 Customer Insights Dashboard")
    st.caption("Customer Type, Gender, Ratings & Buying Behavior")

    male_customers = df_filtered[df_filtered["Gender"] == "Male"].shape[0]
    female_customers = df_filtered[df_filtered["Gender"] == "Female"].shape[0]
    members = df_filtered[df_filtered["Customer_type"] == "Member"].shape[0]
    normal_customers = df_filtered[df_filtered["Customer_type"] == "Normal"].shape[0]

    male_revenue = df_filtered[df_filtered["Gender"] == "Male"]["Total"].sum()
    female_revenue = df_filtered[df_filtered["Gender"] == "Female"]["Total"].sum()
    member_revenue = df_filtered[df_filtered["Customer_type"] == "Member"]["Total"].sum()
    normal_revenue = df_filtered[df_filtered["Customer_type"] == "Normal"]["Total"].sum()

    st.markdown("#### Customer Count")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👨 Male", male_customers)
    col2.metric("👩 Female", female_customers)
    col3.metric("🎫 Members", members)
    col4.metric("🧍 Normal", normal_customers)

    st.markdown("#### Customer Revenue")

    col5, col6, col7, col8 = st.columns(4)

    col5.metric("👨 Male Revenue", f"${male_revenue:,.0f}")
    col6.metric("👩 Female Revenue", f"${female_revenue:,.0f}")
    col7.metric("🎫 Member Revenue", f"${member_revenue:,.0f}")
    col8.metric("🧍 Normal Revenue", f"${normal_revenue:,.0f}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        gender_sales = (
            df_filtered.groupby("Gender")["Total"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            gender_sales,
            names="Gender",
            values="Total",
            title="Sales by Gender",
            hole=0.45
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        customer_sales = (
            df_filtered.groupby("Customer_type")["Total"]
            .sum()
            .reset_index()
            .sort_values("Total", ascending=False)
        )

        fig = px.bar(
            customer_sales,
            x="Customer_type",
            y="Total",
            title="Sales by Customer Type",
            color="Customer_type",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        rating_gender = (
            df_filtered.groupby("Gender")["Rating"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            rating_gender,
            x="Gender",
            y="Rating",
            title="Average Rating by Gender",
            color="Gender",
            text_auto=".2f"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        payment_customer = (
            df_filtered.groupby(["Customer_type", "Payment"])["Total"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            payment_customer,
            x="Customer_type",
            y="Total",
            color="Payment",
            title="Payment Preference by Customer Type",
            barmode="group",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

# -------------------- PAGE 3 --------------------
else:

    st.title("📦 Product & Data View")
    st.caption("Product Performance, Rankings & Detailed Dataset")

    st.markdown("#### Product Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("🏆 Best Product", top_product)
    col2.metric("💰 Best Product Revenue", f"${top_product_revenue:,.0f}")
    col3.metric("📊 Total Revenue", f"${revenue:,.0f}")

    col4, col5, col6 = st.columns(3)

    col4.metric("🛒 Quantity Sold", f"{total_quantity:,}")
    col5.metric("⭐ Avg Rating", f"{avg_rating:.2f}")
    col6.metric("🧾 Total Orders", f"{total_orders:,}")

    st.markdown("---")

    st.markdown("### Top 5 Products by Revenue")

    top_products = (
        df_filtered.groupby("Product line")["Total"]
        .sum()
        .reset_index()
        .sort_values("Total", ascending=False)
        .head(5)
    )

    top_products["Revenue %"] = (
        top_products["Total"] / df_filtered["Total"].sum() * 100
    ).round(2)

    top_products["Total"] = top_products["Total"].round(2)

    st.dataframe(
    top_products,
    use_container_width=True,
    hide_index=True
)

    col1, col2 = st.columns(2)

    with col1:
        product_sales = (
            df_filtered.groupby("Product line")["Total"]
            .sum()
            .reset_index()
            .sort_values("Total", ascending=True)
        )

        fig = px.bar(
            product_sales,
            x="Total",
            y="Product line",
            orientation="h",
            title="Revenue by Product Line",
            color="Total",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        product_quantity = (
            df_filtered.groupby("Product line")["Quantity"]
            .sum()
            .reset_index()
            .sort_values("Quantity", ascending=True)
        )

        fig = px.bar(
            product_quantity,
            x="Quantity",
            y="Product line",
            orientation="h",
            title="Quantity Sold by Product Line",
            color="Quantity",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        product_rating = (
            df_filtered.groupby("Product line")["Rating"]
            .mean()
            .reset_index()
            .sort_values("Rating", ascending=True)
        )

        fig = px.bar(
            product_rating,
            x="Rating",
            y="Product line",
            orientation="h",
            title="Average Rating by Product Line",
            color="Rating",
            text_auto=".2f"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        monthly_sales = (
            df_filtered.groupby(["Year", "Month_Num", "Month"])["Total"]
            .sum()
            .reset_index()
            .sort_values(["Year", "Month_Num"])
        )

        monthly_sales["Year-Month"] = (
            monthly_sales["Year"].astype(str) + " - " + monthly_sales["Month"]
        )

        fig = px.bar(
            monthly_sales,
            x="Year-Month",
            y="Total",
            title="Monthly Revenue",
            color="Total",
            text_auto=True
        )

        fig.update_layout(xaxis_tickangle=-45)

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Filtered Dataset")
    st.dataframe(df_filtered, use_container_width=True)