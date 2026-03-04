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

# ---------------- LOGIN ----------------
if "user" not in st.session_state:

    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        try:

            user = auth.sign_in_with_email_and_password(email,password)

            account = auth.get_account_info(user['idToken'])
            verified = account['users'][0]['emailVerified']

            if verified:

                st.session_state.user=user
                st.rerun()

            else:
                st.error("Verify email first")

        except:
            st.warning("Login failed — retry")

    st.stop()

# ---------------- HEADER ----------------
st.title("🎓 Jaypee Noida Cutoff Predictor")

# ---------------- NAVIGATION ----------------
page = st.radio(
    "Navigation",
    ["🎯 Predictor","📊 Rank ↔ Percentile","🧠 Branch Analyzer"],
    horizontal=True
)

# =====================================================
# 🎯 PREDICTOR
# =====================================================

if page == "🎯 Predictor":

    mode = st.radio(
        "Admission Mode",
        ["Boards Percentage","JEE AIR"],
        horizontal=True
    )

    if mode == "Boards Percentage":

        df = pd.read_excel("cutoff_data.xlsx")

        percentage = st.number_input("Your Percentage",0.0,100.0)

        category = st.selectbox(
            "Category",
            df["Category"].unique()
        )

        round_option = st.selectbox(
            "Round",
            ["ROUND 1 CUTOFF","ROUND 2 CUTOFF","ROUND 3 CUTOFF","SPOT"]
        )

        inflation = st.slider("Inflation %",0.0,5.0,2.0)

        filtered = df[df["Category"]==category]

    else:

        df = pd.read_excel("jee_cutoff.xlsx")

        percentage = st.number_input("Your JEE Rank",1,1000000)

        round_option = st.selectbox(
            "Round",
            ["ROUND 1","ROUND 2","ROUND 2 UPGRADATION 5","SPOT"]
        )

        inflation = st.slider("Inflation %",0.0,5.0,2.0)

        filtered = df

    if st.button("Predict"):

        results=[]

        for _,row in filtered.iterrows():

            current=row[round_option]

            predicted=current+(current*inflation/100)

            safest=predicted+3

            if mode=="Boards Percentage":
                diff=percentage-current
            else:
                diff=current-percentage

            if diff>=3:
                status="🟢 Safe"
            elif diff>=0:
                status="🟡 Borderline"
            elif diff>=-2:
                status="🔴 Risky"
            else:
                status="❌ Not Eligible"

            results.append({
                "Branch":row["Branch Name"],
                "Current":current,
                "Predicted":round(predicted,2),
                "Safest":round(safest,2),
                "Status":status
            })

        result_df=pd.DataFrame(results)

        result_df=result_df.sort_values(by="Safest")

        st.dataframe(result_df,use_container_width=True)

# =====================================================
# 📊 RANK ↔ PERCENTILE
# =====================================================

if page == "📊 Rank ↔ Percentile":

    col1,col2=st.columns(2)

    with col1:

        st.subheader("Percentile → Rank")

        p=st.number_input("Percentile",0.0,100.0)

        if st.button("Calculate Rank"):

            rank=(100-p)*16000

            st.success(f"Expected Rank ≈ {int(rank)}")

    with col2:

        st.subheader("Rank → Percentile")

        r=st.number_input("Rank",1,2000000)

        if st.button("Calculate Percentile"):

            percentile=100-(r/16000)

            st.success(f"Expected Percentile ≈ {round(percentile,3)}")

# =====================================================
# 🧠 BRANCH ANALYZER
# =====================================================

if page == "🧠 Branch Analyzer":

    mode = st.radio(
        "Analyze Using",
        ["Boards","JEE AIR"],
        horizontal=True
    )

    if mode=="Boards":

        df=pd.read_excel("cutoff_data.xlsx")

        round1="ROUND 1 CUTOFF"
        round2="ROUND 2 CUTOFF"

    else:

        df=pd.read_excel("jee_cutoff.xlsx")

        round1="ROUND 1"
        round2="ROUND 2"

    results=[]

    for _,row in df.iterrows():

        r1=row[round1]
        r2=row[round2]

        safest_rank=max(r1,r2)

        safest_percentile=100-(safest_rank/16000)

        results.append({

            "Branch":row["Branch Name"],
            "Round 1":r1,
            "Round 2":r2,
            "Safest Rank":safest_rank,
            "Safest Percentile":round(safest_percentile,3),
            "Basis":"Round1 & Round2 closing ranks"

        })

    safety_df=pd.DataFrame(results)

    safety_df=safety_df.sort_values(
        by="Safest Percentile",
        ascending=False
    )

    st.dataframe(safety_df,use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built with ❤️ by Anshul")
