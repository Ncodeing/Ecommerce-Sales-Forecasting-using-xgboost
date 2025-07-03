import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as colors

# -------------------- Page Setup --------------------
st.set_page_config(page_title="E-commerce Sales Dashboard", layout="wide")
st.title("📊 E-commerce Sales & Profit Dashboard")

# -------------------- Load Data --------------------
@st.cache_data
def load_data():
    df = pd.read_csv("sales_forecasting.csv", encoding="latin1")
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Month of order'] = df['Order Date'].dt.month
    df['Year of order'] = df['Order Date'].dt.year
    df['Day of order'] = df['Order Date'].dt.day_name()
    return df

df = load_data()

# -------------------- Sidebar Filters --------------------
st.sidebar.header("🔎 Filter Options")

segments = st.sidebar.multiselect(
    "Select Segment:",
    options=df['Segment'].unique(),
    default=df['Segment'].unique()
)

categories = st.sidebar.multiselect(
    "Select Category:",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

start_date = st.sidebar.date_input("Start Date", df['Order Date'].min())
end_date = st.sidebar.date_input("End Date", df['Order Date'].max())

# Apply Filters
filtered_df = df[
    (df['Segment'].isin(segments)) &
    (df['Category'].isin(categories)) &
    (df['Order Date'] >= pd.to_datetime(start_date)) &
    (df['Order Date'] <= pd.to_datetime(end_date))
]

# -------------------- KPIs --------------------
st.subheader("Key Metrics")
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
profit_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Profit", f"${total_profit:,.2f}")
col3.metric("Profit Margin", f"{profit_margin:.2f}%")

# -------------------- Visualizations --------------------

# Q1 - Monthly Sales
st.subheader("Monthly Sales Analysis")
monthly_sales = filtered_df.groupby('Month of order')['Sales'].sum().reset_index()
fig = px.line(monthly_sales, x="Month of order", y="Sales", title="Monthly Sales Analysis", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Q2 - Sales by Category
st.subheader("Sales Analysis by Category")
category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
fig = px.pie(category_sales, values="Sales", names='Category', title="Sales by Category", hole=0.1)
fig.update_traces(textposition="inside", textinfo="percent+label")
st.plotly_chart(fig, use_container_width=True)

# Q3 - Sales by Sub-Category
st.subheader("Sales Analysis by Sub-Category")
subcategory_sales = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index()
fig = px.bar(subcategory_sales, x='Sub-Category', y="Sales", title="Sales by Sub-Category")
st.plotly_chart(fig, use_container_width=True)

# Q4 - Monthly Profit
st.subheader("Monthly Profit Analysis")
monthly_profit = filtered_df.groupby('Month of order')['Profit'].sum().reset_index()
fig = px.line(monthly_profit, x="Month of order", y="Profit", title="Monthly Profit Analysis", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Q5 - Profit by Category and Sub-Category
st.subheader("Profit by Category")
p_c = filtered_df.groupby('Category')['Profit'].sum().reset_index()
fig = px.bar(p_c, x="Category", y="Profit", title="Profit by Category")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Profit by Sub-Category")
p_sc = filtered_df.groupby('Sub-Category')['Profit'].sum().reset_index()
fig = px.bar(p_sc, x="Sub-Category", y="Profit", title="Profit by Sub-Category")
st.plotly_chart(fig, use_container_width=True)

# Q6 - Sales and Profit by Segment
st.subheader("Sales & Profit by Segment")
sp_segment = filtered_df.groupby('Segment').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
cp = colors.qualitative.Pastel

fig = go.Figure()
fig.add_trace(go.Bar(x=sp_segment['Segment'], y=sp_segment['Sales'], name='Sales', marker_color=cp[2]))
fig.add_trace(go.Bar(x=sp_segment['Segment'], y=sp_segment['Profit'], name='Profit', marker_color=cp[4]))
fig.update_layout(title="Sales and Profit by Segment", xaxis_title="Customer Segment", yaxis_title="Amount", barmode="group")
st.plotly_chart(fig, use_container_width=True)

# Q7 - Sales to Profit Ratio
st.subheader("Sales to Profit Ratio by Segment")
sp_segment['Sales_to_Profit_Ratio'] = sp_segment['Sales'] / sp_segment['Profit']
st.dataframe(sp_segment[['Segment', 'Sales_to_Profit_Ratio']])

# Q8 - Year-over-Year Sales Growth
st.subheader("Year-over-Year Sales Growth") 
yearly_sales_growth = filtered_df.groupby('Year of order')['Sales'].sum().reset_index()
fig = px.bar(yearly_sales_growth, x="Year of order", y="Sales", title='Year-over-Year Sales Growth')
fig.update_layout(xaxis_type='category')
st.plotly_chart(fig, use_container_width=True)

# Q9 - Monthly Trend of Units Sold
st.subheader("Monthly Trend of Units Sold")         
monthly_units = filtered_df.groupby('Month of order')['Quantity'].sum().reset_index()
fig = px.line(monthly_units, x='Month of order', y='Quantity', title='Monthly Trend of Units Sold', markers=True)
st.plotly_chart(fig, use_container_width=True)  

# Q10 - Region-wise Sales Contribution
st.subheader("Region-wise Sales Contribution")      
region_contrib = filtered_df.groupby('Region')['Sales'].sum().reset_index()
region_contrib['Sales_Percentage'] = round(region_contrib['Sales'] / region_contrib['Sales'].sum() * 100, 2)
fig = px.pie(region_contrib, names='Region', values='Sales_Percentage', title='Region-wise Sales Contribution (%)')
fig.update_traces(textposition="inside", textinfo="percent+label")  
st.plotly_chart(fig, use_container_width=True)


# Q11 - Sales to Profit Ratio
sp_segment = df.groupby('Segment').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
sp_segment['Sales_to_Profit_Ratio'] = sp_segment['Sales'] / sp_segment['Profit']
print(sp_segment[['Segment', 'Sales_to_Profit_Ratio']])

# Q12 - 3-Month Moving Average of Sales
st.subheader("3-Month Moving Average of Sales")
df_sorted = df.sort_values('Order Date')
df_sorted['Sales_MA_3'] = df_sorted['Sales'].rolling(window=3).mean()
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_sorted['Order Date'], y=df_sorted['Sales'], mode='lines', name='Actual Sales'))
fig.add_trace(go.Scatter(x=df_sorted['Order Date'], y=df_sorted['Sales_MA_3'], mode='lines', name='3-Month Moving Avg', line=dict(dash='dash')))
fig.update_layout(title='Sales with 3-Month Moving Average')
st.plotly_chart(fig, use_container_width=True)

# -------------------- Show Raw Data --------------------
with st.expander("View Raw Data"):
    st.dataframe(filtered_df)

