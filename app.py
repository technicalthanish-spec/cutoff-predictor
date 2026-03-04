import streamlit as st
import pandas as pd
import time
import pyrebase

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Jaypee Noida Cutoff Predictor",
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

    st.title("🔐 Jaypee Noida Cutoff Login")

    login_tab, signup_tab = st.tabs(["Login","Signup"])

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

                        user = auth.sign_in_with_email_and_password(email,password)

                        time.sleep(0.4)

                        account_info = auth.get_account_info(user['idToken'])

                        verified = account_info['users'][0]['emailVerified']

                        if verified:

                            st.session_state.user = user
                            st.rerun()

                        else:

                            st.error("Please verify your email before login 📧")

                    except Exception as e:

                        error=str(e)

                        if "INVALID_PASSWORD" in error:
                            st.error("Wrong password")

                        elif "EMAIL_NOT_FOUND" in error:
                            st.error("Email not registered")

                        else:
                            st.warning("Connection retry — click login again")

    with signup_tab:

        with st.form("signup_form"):

            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")

            signup_button = st.form_submit_button("Create Account")

            if signup_button:

                try:

                    user = auth.create_user_with_email_and_password(new_email,new_password)

                    auth.send_email_verification(user['idToken'])

                    st.success("Account created! Check your email to verify 📧")

                except:

                    st.error("Signup Failed")

    st.stop()

# ---------------- LOGOUT ----------------
col1,col2 = st.columns([9,1])

with col2:
    if st.button("Logout"):
        del st.session_state.user
        st.rerun()

# ---------------- HEADER ----------------
st.markdown("""
# 🎓 Jaypee Noida Cutoff Predictor  
### 🚀 Smart Round-wise Prediction + AI Counsellor
""")

# ---------------- ANIMATED BUTTON STYLE ----------------
st.markdown("""
<style>
.stRadio > div {
    background: linear-gradient(90deg,#1f4fff,#00d4ff);
    padding:10px;
    border-radius:12px;
}
.stRadio label {
    font-weight:600;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- MODE SELECT ----------------
mode = st.radio(
    "Select Admission Mode",
    ["Boards Percentage","JEE AIR 🚀"],
    horizontal=True
)

# ---------------- LOAD DATA ----------------
if mode == "Boards Percentage":
    df = pd.read_excel("cutoff_data.xlsx")
else:
    df = pd.read_excel("jee_cutoff.xlsx")

# ---------------- INPUT SECTION ----------------
with st.container():

    st.markdown("## 🔍 Enter Your Details")

    col1,col2,col3 = st.columns(3)

    with col1:

        if mode == "Boards Percentage":
            score = st.number_input("🎯 Your Percentage",0.0,100.0)

        else:
            score = st.number_input("🎯 Your JEE AIR Rank",1,1000000)

    if mode == "Boards Percentage":

        with col2:
            category = st.selectbox("📂 Category",df["Category"].unique())

        filtered_df = df[df["Category"] == category]

    else:

        filtered_df = df

    with col3:
        round_option = st.selectbox(
            "🗂 Select Round",
            ["ROUND 1 CUTOFF","ROUND 2 CUTOFF","ROUND 3 CUTOFF","SPOT"]
        )

    inflation = st.slider("📈 Expected Inflation (%)",0.0,5.0,2.0)

# ---------------- PREDICTION ----------------
if st.button("🚀 Predict Now"):

    with st.spinner("Analyzing cutoffs..."):
        time.sleep(1)

    filtered = filtered_df

    results=[]

    for _,row in filtered.iterrows():

        if mode == "JEE AIR 🚀":
    
    if round_option == "ROUND 1 CUTOFF":
        current = row["ROUND 1"]

    elif round_option == "ROUND 2 CUTOFF":
        current = row["ROUND 2"]

    elif round_option == "ROUND 3 CUTOFF":
        current = row["ROUND 2 UPGRADATION"]

    else:
        current = row["SPOT"]

else:

    current = row[round_option]

        predicted=current+(current*inflation/100)

        safest=predicted+3

        if mode == "Boards Percentage":
            diff = score-current
        else:
            diff = current-score

        if diff>=3:
            status="🟢 Safe"
        elif diff>=0:
            status="🟡 Borderline"
        elif diff>=-2:
            status="🔴 Risky"
        else:
            status="❌ Not Eligible"

        results.append({
            "Program":row["Program"],
            "Branch Name":row["Branch Name"],
            "Current Cutoff":current,
            "Predicted Cutoff":round(predicted,2),
            "Safest Score":round(safest,2),
            "Status":status
        })

    result_df=pd.DataFrame(results)

    result_df=result_df.sort_values(by="Safest Score")

    st.session_state["result_df"]=result_df

    safe=len(result_df[result_df["Status"]=="🟢 Safe"])
    borderline=len(result_df[result_df["Status"]=="🟡 Borderline"])
    risky=len(result_df[result_df["Status"]=="🔴 Risky"])

    st.markdown("## 📊 Summary")

    a,b,c=st.columns(3)

    a.metric("Safe",safe)
    b.metric("Borderline",borderline)
    c.metric("Risky",risky)

    st.markdown("## 📋 Results")

    st.dataframe(result_df,use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built with ❤️ by Anshul")

