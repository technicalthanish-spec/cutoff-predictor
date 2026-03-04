import streamlit as st
import pandas as pd
import time
import pyrebase

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Cutoff Predictor Pro",
    page_icon="🎓",
    layout="wide"
)

# ---------------- UI STYLE ----------------
st.markdown("""
<style>

.main-title {
font-size:40px;
font-weight:700;
text-align:center;
background: linear-gradient(90deg,#3a7bd5,#00d2ff);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
}

.login-box {
padding:25px;
border-radius:12px;
background-color:#111111;
box-shadow:0px 0px 20px rgba(0,0,0,0.3);
}

</style>
""", unsafe_allow_html=True)

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

    st.markdown("<h1 class='main-title'>🎓 Cutoff Predictor Pro</h1>", unsafe_allow_html=True)

    st.info("Login to continue")

    login_tab, signup_tab = st.tabs(["Login","Signup"])

    # -------- LOGIN --------
    with login_tab:

        with st.form("login_form"):

            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            login_btn = st.form_submit_button("Login")

            if login_btn:

                if email == "" or password == "":
                    st.warning("Enter email and password")

                else:
                    with st.spinner("Authenticating..."):
                        time.sleep(0.7)

                        try:

                            user = auth.sign_in_with_email_and_password(email,password)

                            if user:
                                st.session_state.user = user
                                st.rerun()

                        except Exception as e:

                            error = str(e)

                            if "EMAIL_NOT_FOUND" in error:
                                st.error("Email not registered")

                            elif "INVALID_PASSWORD" in error:
                                st.error("Wrong password")

                            else:
                                st.error("Login failed. Try again.")

    # -------- SIGNUP --------
    with signup_tab:

        with st.form("signup_form"):

            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")

            signup_btn = st.form_submit_button("Create Account")

            if signup_btn:

                if new_email == "" or new_password == "":
                    st.warning("Enter email & password")

                else:

                    with st.spinner("Creating account..."):
                        time.sleep(0.7)

                        try:

                            auth.create_user_with_email_and_password(new_email,new_password)

                            st.success("Account created successfully 🎉")

                        except:
                            st.error("Signup failed")

    st.stop()

# ---------------- LOGOUT ----------------
col1,col2 = st.columns([9,1])

with col2:
    if st.button("Logout"):
        del st.session_state.user
        st.rerun()

# ---------------- HEADER ----------------
st.markdown("<h1 class='main-title'>🎓 Cutoff Predictor Pro</h1>", unsafe_allow_html=True)

st.success("Welcome! Login successful 🎉")

# ---------------- LOAD DATA ----------------
df = pd.read_excel("cutoff_data.xlsx")

# ---------------- INPUT SECTION ----------------
st.markdown("## 🔍 Enter Your Details")

c1,c2,c3 = st.columns(3)

with c1:
    percentage = st.number_input("🎯 Your Percentage",0.0,100.0)

with c2:
    category = st.selectbox("📂 Category",df["Category"].unique())

with c3:
    round_option = st.selectbox(
        "🗂 Select Round",
        ["ROUND 1 CUTOFF","ROUND 2 CUTOFF","ROUND 3 CUTOFF","SPOT"]
    )

inflation = st.slider("📈 Expected Next Year Inflation (%)",0.0,5.0,2.0)

# ---------------- PREDICTION ----------------
if st.button("🚀 Predict Now"):

    with st.spinner("Analyzing cutoffs..."):
        time.sleep(1)

    filtered = df[df["Category"]==category]

    results=[]

    for _,row in filtered.iterrows():

        current=row[round_option]
        predicted=current+(current*inflation/100)
        safest=predicted+3

        diff=percentage-current

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
            "Branch":row["Branch Name"],
            "Current Cutoff":current,
            "Predicted Cutoff":round(predicted,2),
            "Safest Score":round(safest,2),
            "Status":status
        })

    result_df=pd.DataFrame(results)
    result_df=result_df.sort_values(by="Safest Score")

    st.session_state["result_df"]=result_df

    # SUMMARY
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
