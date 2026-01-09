import streamlit as st
import bcrypt
from db import query_db, execute_db # Import both query_db and execute_db

def register():
    st.subheader("📝 Register")
    name = st.text_input("Name")
    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")
    # Optional: Add fields for age, gender, height, weight if needed during registration
    age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
    gender = st.selectbox("Gender", options=["Male", "Female", "Other"])
    height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1)
    weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.1)

    if st.button("Sign Up"):
        # Check if email already exists before attempting to insert
        existing_user = query_db("SELECT id FROM users WHERE email = ?", (email,), fetchone=True)
        if existing_user:
            st.error("Email already registered. Please use a different email address.")
        else:
            # Hash the password using bcrypt
            pwd_hash_bytes = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
            pwd_hash_str = pwd_hash_bytes.decode('utf-8') # Decode bytes to string for storage

            # Use execute_db for the INSERT operation
            # Use ? placeholders for SQLite
            result = execute_db(
                "INSERT INTO users (name, email, password, age, gender, height, weight) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, email, pwd_hash_str, age, gender, height, weight)
            )
            if result != -1: # Check if execute_db was successful
                st.success("Account created successfully! Please log in.")
            else:
                # This case might occur if there's an unexpected database error beyond the UNIQUE constraint
                st.error("Registration failed due to a database error. Please try again.")


def login():
    st.subheader("🔐 Login")
    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        # Use query_db for the SELECT operation, with ? placeholders
        user = query_db("SELECT * FROM users WHERE email = ?", (email,), fetchone=True)
        if user:
            # Retrieve the stored password hash (string)
            stored_hash_str = user["password"] # Ensure this matches your DB column name
            # Encode the input password
            pwd_bytes = pwd.encode('utf-8')
            # Encode the stored hash string back to bytes for bcrypt.checkpw
            stored_hash_bytes = stored_hash_str.encode('utf-8')
            # Check the password
            if bcrypt.checkpw(pwd_bytes, stored_hash_bytes):
                st.session_state.user_id = user["id"]
                st.session_state.user = dict(user) # Convert Row object to dict if necessary
                st.success("Login successful!")
                st.rerun() # Refresh the app state after login
            else:
                st.error("Invalid credentials. Please check your email and password.")
        else:
            st.error("Invalid credentials. Please check your email and password.")
