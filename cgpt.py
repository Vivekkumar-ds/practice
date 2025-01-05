
import os
import pandas as pd
import streamlit as st
import re

col1, col2 = st.columns([3, 5])  

with col2:
    st.image("cgpt.jpeg", width=100)  # Replace 'logo.png' with your logo path or URL


st.title("Current Affairs GPT")   #Title

st.write("Welcome to Current Affairs GPT – your dedicated AI companion for mastering current affairs! Tailored to your unique goals, our platform is designed to support your preparation across a wide range of exams, including UPSC, SSC, NEET, banking, and more. Stay ahead with curated, goal-focused content and start your journey towards success. Sign up today to make current affairs your strongest subject!")

email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
phone_pattern = r'^\d{10}$'

file_path = "user_data.xlsx"

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "show_confirmation" not in st.session_state:
    st.session_state.show_confirmation = False
if "form_data" not in st.session_state:
    st.session_state.form_data = {}
if "show_signin" not in st.session_state:
    st.session_state.show_signin = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

signup_or_signin = st.radio("Select an option", ["Sign Up", "Sign In"])

if signup_or_signin == "Sign Up" and not st.session_state.form_submitted:
    with st.form("Signup Form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        education = st.selectbox("Education Level", ["High School", "Diploma", "Undergraduate", "Postgraduate", "PhD"])
        target_exam = st.selectbox("Target Exam", ["GRE", "GMAT", "CAT", "GATE", "UPSC", "SAT", "TOEFL", "IELTS", "Others"])
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submit = st.form_submit_button("Sign up")
    
    if submit:
        if not (name and email and phone and education and target_exam and password and confirm_password):
            st.error("Please fill all the fields.")
        elif not re.match(email_pattern, email):
            st.error("Please enter a valid email address.")
        elif not re.match(phone_pattern, phone):
            st.error("Please enter a valid phone number (10 digits).")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            st.session_state.show_confirmation = True
            st.session_state.form_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "education": education,
                "target_exam": target_exam,
                "password": password
            }

if st.session_state.show_confirmation:
    st.write("Please confirm the details you entered:")
    st.write(f"**Name:** {st.session_state.form_data['name']}")
    st.write(f"**Email:** {st.session_state.form_data['email']}")
    st.write(f"**Phone Number:** {st.session_state.form_data['phone']}")
    st.write(f"**Education Level:** {st.session_state.form_data['education']}")
    st.write(f"**Target Exam:** {st.session_state.form_data['target_exam']}")
    
    if st.button("Confirm Signup"):
        st.session_state.form_submitted = True
        st.session_state.show_confirmation = False  
        
        user_data = st.session_state.form_data

        if os.path.exists(file_path):
            existing_data = pd.read_excel(file_path)
            new_data = pd.DataFrame([user_data])
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            updated_data = pd.DataFrame([user_data])

        updated_data.to_excel(file_path, index=False)

        st.success("You have successfully registered!")
        
        st.session_state.form_submitted = False
        st.session_state.show_confirmation = False
        st.session_state.form_data = {}  

        if st.button("Register Another User"):
            st.session_state.form_submitted = False
            st.session_state.show_confirmation = False
            st.experimental_rerun()  # Rerun to clear form inputs

elif signup_or_signin == "Sign In":
    email_signin = st.text_input("Email Address")
    password_signin = st.text_input("Password", type="password")
    
    if st.button("Sign In"):
        if os.path.exists(file_path):
            user_data = pd.read_excel(file_path)
            
            user = user_data[user_data["email"] == email_signin]
            
            if not user.empty:
                stored_password = user["password"].values[0]
                if password_signin == stored_password:
                    st.session_state.current_user = email_signin
                    st.success(f"Welcome back, {email_signin}!")
                else:
                    st.error("Incorrect password.")
            else:
                st.error("Email not registered. Please sign up first.")
        else:
            st.error("No user data found. Please sign up first.")
    
    st.write("Or sign in with Google")


import streamlit as st
import requests
from urllib.parse import urlencode

CLIENT_ID = "948659542381-8ds6lfnpoq4q669hqj1fm8feqb0ovvgi0988909875.apps.googleusercontent.com"
CLIENT_SECRET = "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qwertyuiop"  
REDIRECT_URI = "http://localhost:8501" 

SCOPE = "openid email profile"
AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def get_google_auth_url():
    """Generate the Google OAuth2 Authorization URL."""
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",
    }
    url = f"{AUTH_URL}?{urlencode(params)}"
    return url


def get_google_access_token(auth_code):
    """Exchange authorization code for access token."""
    data = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()


def get_user_info(access_token):
    """Fetch user information using the access token."""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(USER_INFO_URL, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    st.subheader("Sign in with Google")

    auth_code = st.query_params.get("code", None)

    if auth_code:
        try:
            token_response = get_google_access_token(auth_code)
            access_token = token_response["access_token"]

            user_info = get_user_info(access_token)
            st.success(f"Welcome {user_info['name']}!")
            st.write("Email:", user_info["email"])
            st.image(user_info["picture"], width=100)
        except Exception as e:
            st.error(f"Authentication failed: {e}")
    else:
        auth_url = get_google_auth_url()
        st.markdown(f"[Sign in with Google]({auth_url})")


if __name__ == "__main__":
    main()

