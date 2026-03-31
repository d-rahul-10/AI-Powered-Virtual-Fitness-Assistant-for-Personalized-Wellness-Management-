import streamlit as st
import bcrypt
from db import query_db, execute_db # Import both query_db and execute_db

def register():
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>Create an Account</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Join Nova Fitness Assistant to start your journey.</p>", unsafe_allow_html=True)
    
    with st.container():
        # Use columns to make the form look more balanced
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="john@example.com")
            pwd = st.text_input("Password", type="password", placeholder="••••••••")
            gender = st.selectbox("Gender", options=["Male", "Female", "Other"])
            
        with col2:
            age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1)
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.1)
            
        st.markdown("<br>", unsafe_allow_html=True)
        # Center the submit button
        submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
        with submit_col2:
            if st.button("Sign Up", use_container_width=True, type="primary"):
                if not name or not email or not pwd:
                    st.warning("Please fill in all required fields (Name, Email, Password).")
                else:
                    # Check if email already exists before attempting to insert
                    existing_user = query_db("SELECT id FROM users WHERE email = ?", (email,), fetchone=True)
                    if existing_user:
                        st.error("Email already registered. Please go to Login.")
                    else:
                        # Hash the password using bcrypt
                        pwd_hash_bytes = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
                        pwd_hash_str = pwd_hash_bytes.decode('utf-8')

                        result = execute_db(
                            "INSERT INTO users (name, email, password, age, gender, height, weight) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (name, email, pwd_hash_str, age, gender, height, weight)
                        )
                        if result != -1:
                            st.success("✅ Account created successfully! Please proceed to Login.")
                        else:
                            st.error("Registration failed due to a database error. Please try again.")


def login():
    st.markdown("<h2 style='text-align: center; color: #008CBA;'>Welcome Back</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Login to continue achieving your goals.</p>", unsafe_allow_html=True)
    
    # Use columns to center the login form, making it look like a cohesive card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container(border=True): # Streamlit 1.29+ border feature for a card-like look
            email = st.text_input("Email", placeholder="your_email@example.com")
            pwd = st.text_input("Password", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login", use_container_width=True, type="primary"):
                if not email or not pwd:
                    st.warning("Please enter both email and password.")
                else:
                    user = query_db("SELECT * FROM users WHERE email = ?", (email,), fetchone=True)
                    if user:
                        stored_hash_str = user["password"]
                        pwd_bytes = pwd.encode('utf-8')
                        stored_hash_bytes = stored_hash_str.encode('utf-8')
                        
                        if bcrypt.checkpw(pwd_bytes, stored_hash_bytes):
                            st.session_state.user_id = user["id"]
                            st.session_state.user = dict(user)
                            st.success("Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please check your email and password.")
                    else:
                        st.error("Account not found. Please register first.")
