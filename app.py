import streamlit as st
import pandas as pd
import bcrypt
import os
from utils.points_manager import add_points, get_points, get_user_level


# ---------------------- Helper Functions ------------------------
def load_users():
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    else:
        df = pd.DataFrame(columns=["username", "email", "password"])
        df.to_csv("users.csv", index=False)
        return df


def save_user(username, email, password):
    users = load_users()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_user = pd.DataFrame([[username, email, hashed_pw]], columns=["username", "email", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv("users.csv", index=False)


def authenticate(username, password):
    users = load_users()
    user_row = users[users["username"] == username]
    if user_row.empty:
        return False
    stored_password = user_row.iloc[0]["password"]
    return bcrypt.checkpw(password.encode(), stored_password.encode())


# ---------------------- Streamlit Config ------------------------
st.set_page_config(page_title="NoteGPT", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "signup"


# ---------------------- Signup Page ------------------------
def show_signup():
    st.title("🚀 Welcome to NoteGPT - Create Account")
    new_username = st.text_input("Username")
    new_email = st.text_input("Email")
    new_password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if not new_username or not new_email or not new_password:
            st.warning("Please fill all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            users = load_users()
            if new_username in users["username"].values:
                st.error("Username already exists.")
            else:
                save_user(new_username, new_email, new_password)
                add_points(new_username, 10)  # Reward points on signup
                st.success("Account created successfully! You received **+10 points**. You can now log in.")
                st.session_state.page = "login"
                st.rerun()

    st.markdown("---")
    if st.button("Already have an account? Login here"):
        st.session_state.page = "login"
        st.rerun()


# ---------------------- Login Page ------------------------
def show_login():
    st.title("🔑 Login to NoteGPT")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.username = username
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.markdown("---")
    if st.button("Don't have an account? Sign up here"):
        st.session_state.page = "signup"
        st.rerun()


# ---------------------- Dashboard ------------------------
def show_dashboard():
    col1, col2 = st.columns([5, 1])   # 👈 Make logout column bit wider

    with col1:
        st.markdown(f"### 👋 Welcome, **{st.session_state.username}**")
        points = get_points(st.session_state.username)
        level = get_user_level(points)
        st.markdown(f"**Your Points:** {points} | **Your Level:** {level} 🎖️")

    with col2:
        logout = st.button("Logout", help="Logout & Return to Login")
        if logout:
            st.session_state.page = "login"
            del st.session_state.username
            st.rerun()

    st.title("📚 NoteGPT - Your AI Study Assistant")
    st.markdown("""
    ### How it works:
    - 📄 Upload your study PDFs  
    - ✨ Get AI-powered summaries  
    - 🧠 Take AI-generated quizzes  
    - 🏆 Earn points and view leaderboard
    """)
    st.info("Use the **sidebar** to access **Quiz / Leaderboard / About**.")

# ---------------------- Routing ------------------------
if st.session_state.page == "signup":
    show_signup()
elif st.session_state.page == "login":
    show_login()
elif st.session_state.page == "dashboard":
    show_dashboard()
