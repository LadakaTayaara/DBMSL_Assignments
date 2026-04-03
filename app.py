import streamlit as st
import pandas as pd
from db_manager import fetch_data, execute_query
import plotly.express as px

st.set_page_config(page_title="E-Com Inventory Pro", layout="wide")

st.title("📦 E-Commerce Inventory Management")
st.sidebar.header("Navigation")
menu = st.sidebar.radio("Go to:", ["Dashboard", "Manage Stock", "Add Product"])

# --- DASHBOARD ---
if menu == "Dashboard":
    st.subheader("Inventory Overview")
    
    df = fetch_data("SELECT p.name, p.price, p.stock_quantity, c.category_name FROM Products p JOIN Categories c ON p.category_id = c.category_id")
    
    if not df.empty:
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total SKU Count", len(df))
        col2.metric("Total Stock Value", f"₹{ (df['price'] * df['stock_quantity']).sum():,.2f}")
        col3.error(f"Low Stock Items: {len(df[df['stock_quantity'] < 5])}")

        # Visualization
        fig = px.bar(df, x="name", y="stock_quantity", color="category_name", title="Current Stock Levels")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No products found. Add some in the 'Add Product' tab!")

# --- MANAGE STOCK ---
elif menu == "Manage Stock":
    st.subheader("Update Inventory Levels")
    df = fetch_data("SELECT product_id, name, stock_quantity FROM Products")
    
    selected_product = st.selectbox("Select Product", df['name'].tolist())
    new_qty = st.number_input("New Quantity", min_value=0)
    
    if st.button("Update Stock"):
        pid = df[df['name'] == selected_product]['product_id'].values[0]
        execute_query("UPDATE Products SET stock_quantity = %s WHERE product_id = %s", (new_qty, int(pid)))
        st.success(f"Updated {selected_product} to {new_qty}")
        st.rerun()

# --- ADD PRODUCT ---
elif menu == "Add Product":
    st.subheader("Register New Item")
    cat_df = fetch_data("SELECT * FROM Categories")
    
    with st.form("product_form"):
        name = st.text_input("Product Name")
        cat_name = st.selectbox("Category", cat_df['category_name'].tolist())
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        qty = st.number_input("Initial Stock", min_value=0)
        
        if st.form_submit_button("Save Product"):
            cid = cat_df[cat_df['category_name'] == cat_name]['category_id'].values[0]
            execute_query("INSERT INTO Products (name, category_id, price, stock_quantity) VALUES (%s, %s, %s, %s)", 
                          (name, int(cid), price, qty))
            st.success(f"Product '{name}' added successfully!")
