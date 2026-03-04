import streamlit as st
import pandas as pd
import time
import pyrebase
st.cache_data.clear()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Cutoff Predictor Pro",
    page_icon="🎓",
    layout="wide"
)

# ---------------- FIREBASE CONFIG ----------------
firebaseConfig = {
    "apiKey": "AIzaSyA6enUAvvHTKj_A-525fXzBnXhgckiPO2c",
    "authDomain": "cutoff-predictor.firebaseapp.com",
    "projectId": "cutoff-predictor",
    "storageBucket": "cutoff-predictor.firebasestorage.app",
    "messagingSenderId": "694561033415",
    "appId": "1:694561033415:web:0012224da667a1b7f542e2",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# ---------------- LOGIN SYSTEM ----------------
if "user" not in st.session_state:

    st.title("🔐 Login to Cutoff Predictor")

    login_tab, signup_tab = st.tabs(["Login", "Signup"])

    # -------- LOGIN --------
   with login_tab:

    with st.form("login_form"):

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        login_button = st.form_submit_button("Login")

        if login_button:

            if email == "" or password == "":
                st.warning("Enter email and password")

            else:
                try:
                    user = auth.sign_in_with_email_and_password(email, password)

                    if user:
                        st.session_state.user = user
                        st.rerun()

                except Exception as e:
                    error_message = str(e)

                    if "INVALID_PASSWORD" in error_message:
                        st.error("Wrong password")

                    elif "EMAIL_NOT_FOUND" in error_message:
                        st.error("Email not registered")

                    else:
                        st.error("Login failed. Try again.")

    # -------- SIGNUP --------
    with signup_tab:

        with st.form("signup_form"):

            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")

            signup_button = st.form_submit_button("Create Account")

            if signup_button:

                try:
                    auth.create_user_with_email_and_password(new_email, new_password)
                    st.success("Account Created Successfully 🎉")

                except:
                    st.error("Signup Failed")

    st.stop()

# ---------------- LOGOUT ----------------
col1, col2 = st.columns([9,1])

with col2:
    if st.button("Logout"):
        del st.session_state.user
        st.rerun()

# ---------------- HEADER ----------------
st.markdown("""
# 🎓 Cutoff Predictor Pro  
### 🚀 Smart Round-wise Prediction + AI Counsellor Engine
""")

st.success("Welcome to Cutoff Predictor 🎓")

# ---------------- LOAD DATA ----------------
df = pd.read_excel("cutoff_data.xlsx")

# ---------------- INPUT SECTION ----------------
with st.container():

    st.markdown("## 🔍 Enter Your Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        percentage = st.number_input(
            "🎯 Your Percentage",
            min_value=0.0,
            max_value=100.0
        )

    with col2:
        category = st.selectbox(
            "📂 Category",
            df["Category"].unique()
        )

    with col3:
        round_option = st.selectbox(
            "🗂 Select Round (Base View)",
            ["ROUND 1 CUTOFF","ROUND 2 CUTOFF","ROUND 3 CUTOFF","SPOT"]
        )

    inflation = st.slider(
        "📈 Expected Next Year Inflation (%)",
        0.0,5.0,2.0
    )

# ---------------- PREDICTION ----------------
if st.button("🚀 Predict Now"):

    with st.spinner("🔍 Analyzing cutoffs..."):
        time.sleep(1)

    progress = st.progress(0)

    for i in range(100):
        time.sleep(0.01)
        progress.progress(i+1)

    progress.empty()

    filtered = df[df["Category"] == category]

    results = []

    for _, row in filtered.iterrows():

        current_cutoff = row[round_option]
        predicted_cutoff = current_cutoff + (
            current_cutoff * inflation / 100
        )

        safest_score = predicted_cutoff + 3

        difference = percentage - current_cutoff

        if difference >= 3:
            status = "🟢 Safe"
        elif difference >= 0:
            status = "🟡 Borderline"
        elif difference >= -2:
            status = "🔴 Risky"
        else:
            status = "❌ Not Eligible"

        results.append({
            "Program": row["Program"],
            "Branch Name": row["Branch Name"],
            "Current Cutoff": current_cutoff,
            "Predicted Next Year Cutoff": round(predicted_cutoff,2),
            "Safest Score Next Year": round(safest_score,2),
            "Your Status": status
        })

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(
        by="Safest Score Next Year"
    )

    st.session_state["result_df"] = result_df

    # -------- SUMMARY --------
    safe_count = len(
        result_df[result_df["Your Status"]=="🟢 Safe"]
    )

    borderline_count = len(
        result_df[result_df["Your Status"]=="🟡 Borderline"]
    )

    risky_count = len(
        result_df[result_df["Your Status"]=="🔴 Risky"]
    )

    st.markdown("## 📊 Performance Summary")

    c1,c2,c3 = st.columns(3)

    c1.metric("🟢 Safe Options",safe_count)
    c2.metric("🟡 Borderline",borderline_count)
    c3.metric("🔴 Risky",risky_count)

    st.markdown("## 📋 Detailed Results")

    st.dataframe(result_df,use_container_width=True)

# ---------------- AI SECTION ----------------
if "result_df" in st.session_state:

    st.markdown("---")
    st.markdown("## 🤖 AI Counsellor Recommendation")

    colA,colB = st.columns(2)

    with colA:
        user_interest = st.selectbox(
            "🎯 Your Primary Interest",
            ["Coding","Core Engineering"]
        )

    with colB:
        risk_level = st.selectbox(
            "⚖ Risk Preference",
            ["Safe Only","Balanced","Aggressive"]
        )

    if st.button("🧠 Generate AI Recommendation"):

        ai_df = df[df["Category"] == category].copy()

        if risk_level=="Safe Only":
            selected_round="ROUND 1 CUTOFF"

        elif risk_level=="Balanced":
            selected_round="ROUND 2 CUTOFF"

        else:
            selected_round="SPOT"

        if user_interest=="Coding":
            keywords=["computer","ai","data","software","it"]

        else:
            keywords=[
                "electronics",
                "electrical",
                "mechanical",
                "civil",
                "robotics",
                "vlsi"
            ]

        ai_df = ai_df[
            ai_df["Branch Name"].str.lower().apply(
                lambda x:any(k in x for k in keywords)
            )
        ]

        if ai_df.empty:

            st.error(
                "Branches not available for your interest."
            )

        else:

            ai_df["Predicted Cutoff"] = ai_df[selected_round] + (
                ai_df[selected_round] * inflation / 100
            )

            ai_df["Safest Score"] = ai_df["Predicted Cutoff"] + 3

            ai_df = ai_df.sort_values(by="Safest Score")

            top = ai_df.head(3)

            st.markdown("### 🏆 Top Recommended Branches")

            st.dataframe(
                top[["Branch Name","Safest Score"]],
                use_container_width=True
            )

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built with ❤️ by Anshul | AI Cutoff Prediction Engine")

