import streamlit as st
import pandas as pd
from models import db, InventoryItem, AuditLog
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database setup
DATABASE_URL = 'sqlite:///inventory.db'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize database
if not os.path.exists('inventory.db'):
    from models import db
    db.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def login_user():
    st.title("Inventory Management System - Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "password":
            st.session_state.logged_in = True
            st.session_state.user_id = 1
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def main_app():
    st.title("Inventory Management System")

    menu = ["View Inventory", "Add Item", "Edit Item", "Delete Item", "Audit Log"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "View Inventory":
        st.header("Inventory Items")
        db = get_db()
        items = db.query(InventoryItem).all()
        if items:
            df = pd.DataFrame([{
                'ID': item.id,
                'Product Name': item.product_name,
                'SKU': item.sku,
                'Category': item.category,
                'Quantity': item.quantity,
                'Supplier': item.supplier,
                'Price': item.price,
                'Location': item.location
            } for item in items])
            st.dataframe(df)
        else:
            st.info("No items in inventory")

    elif choice == "Add Item":
        st.header("Add New Item")
        with st.form("add_item"):
            product_name = st.text_input("Product Name")
            sku = st.text_input("SKU")
            category = st.text_input("Category")
            quantity = st.number_input("Quantity", min_value=0, value=0)
            supplier = st.text_input("Supplier")
            price = st.number_input("Price", min_value=0.0, value=0.0)
            location = st.text_input("Location")

            submitted = st.form_submit_button("Add Item")
            if submitted:
                if not sku:
                    st.error("SKU is required")
                else:
                    db = get_db()
                    existing = db.query(InventoryItem).filter_by(sku=sku).first()
                    if existing:
                        st.error("SKU already exists")
                    else:
                        item = InventoryItem(
                            product_name=product_name,
                            sku=sku,
                            category=category,
                            quantity=quantity,
                            supplier=supplier,
                            price=price,
                            location=location
                        )
                        db.add(item)
                        db.commit()

                        # Audit log
                        log = AuditLog(
                            user_id=st.session_state.user_id,
                            action='CREATE',
                            item_id=item.id,
                            details=f'Created item {product_name}'
                        )
                        db.add(log)
                        db.commit()

                        st.success("Item added successfully!")
                        st.rerun()

    elif choice == "Edit Item":
        st.header("Edit Item")
        db = get_db()
        items = db.query(InventoryItem).all()
        if items:
            item_options = {f"{item.id}: {item.product_name} ({item.sku})": item for item in items}
            selected_item_key = st.selectbox("Select Item to Edit", list(item_options.keys()))
            selected_item = item_options[selected_item_key]

            with st.form("edit_item"):
                product_name = st.text_input("Product Name", value=selected_item.product_name or "")
                sku = st.text_input("SKU", value=selected_item.sku)
                category = st.text_input("Category", value=selected_item.category or "")
                quantity = st.number_input("Quantity", min_value=0, value=selected_item.quantity)
                supplier = st.text_input("Supplier", value=selected_item.supplier or "")
                price = st.number_input("Price", min_value=0.0, value=selected_item.price)
                location = st.text_input("Location", value=selected_item.location or "")

                submitted = st.form_submit_button("Update Item")
                if submitted:
                    old_values = f'quantity={selected_item.quantity}, price={selected_item.price}, location={selected_item.location}'
                    selected_item.product_name = product_name
                    selected_item.sku = sku
                    selected_item.category = category
                    selected_item.quantity = quantity
                    selected_item.supplier = supplier
                    selected_item.price = price
                    selected_item.location = location
                    db.commit()

                    # Audit log
                    new_values = f'quantity={quantity}, price={price}, location={location}'
                    log = AuditLog(
                        user_id=st.session_state.user_id,
                        action='UPDATE',
                        item_id=selected_item.id,
                        details=f'Updated from {old_values} to {new_values}'
                    )
                    db.add(log)
                    db.commit()

                    st.success("Item updated successfully!")
                    st.rerun()
        else:
            st.info("No items to edit")

    elif choice == "Delete Item":
        st.header("Delete Item")
        db = get_db()
        items = db.query(InventoryItem).all()
        if items:
            item_options = {f"{item.id}: {item.product_name} ({item.sku})": item for item in items}
            selected_item_key = st.selectbox("Select Item to Delete", list(item_options.keys()))
            selected_item = item_options[selected_item_key]

            if st.button("Delete Item", type="primary"):
                db.delete(selected_item)
                db.commit()

                # Audit log
                log = AuditLog(
                    user_id=st.session_state.user_id,
                    action='DELETE',
                    item_id=selected_item.id,
                    details=f'Deleted item {selected_item.product_name}'
                )
                db.add(log)
                db.commit()

                st.success("Item deleted successfully!")
                st.rerun()
        else:
            st.info("No items to delete")

    elif choice == "Audit Log":
        st.header("Audit Log")
        db = get_db()
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
        if logs:
            df = pd.DataFrame([{
                'ID': log.id,
                'User ID': log.user_id,
                'Action': log.action,
                'Item ID': log.item_id,
                'Details': log.details,
                'Timestamp': log.timestamp
            } for log in logs])
            st.dataframe(df)
        else:
            st.info("No audit logs available")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

def main():
    st.set_page_config(page_title="Inventory Management", page_icon="📦", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        main_app()
    else:
        login_user()

if __name__ == "__main__":
    main()
