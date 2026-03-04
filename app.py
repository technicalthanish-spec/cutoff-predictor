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

                try:

                    # retry login once
                    for i in range(2):
                        try:
                            user = auth.sign_in_with_email_and_password(email,password)
                            break
                        except:
                            time.sleep(1)

                    account_info = auth.get_account_info(user['idToken'])
                    verified = account_info['users'][0]['emailVerified']

                    if verified:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Please verify your email first")

                except Exception as e:

                    error=str(e)

                    if "INVALID_PASSWORD" in error:
                        st.error("Wrong password")

                    elif "EMAIL_NOT_FOUND" in error:
                        st.error("Email not registered")

                    else:
                        st.warning("Network retry — click login again")

    with signup_tab:

        with st.form("signup_form"):

            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")

            signup_button = st.form_submit_button("Create Account")

            if signup_button:

                try:

                    user = auth.create_user_with_email_and_password(new_email,new_password)
                    auth.send_email_verification(user['idToken'])

                    st.success("Account created! Verify your email")

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
### 🚀 Smart Round-wise Prediction Tool
""")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stRadio > div {
background: linear-gradient(90deg,#1f4fff,#00d4ff);
padding:10px;
border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- MODE SELECT ----------------
mode = st.radio(
    "Select Admission Mode",
    ["Boards Percentage","JEE AIR"],
    horizontal=True
)

# ---------------- LOAD DATA ----------------
if mode == "Boards Percentage":
    df = pd.read_excel("cutoff_data.xlsx")
else:
    df = pd.read_excel("jee_cutoff.xlsx")

# ---------------- INPUT SECTION ----------------
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

    if mode == "Boards Percentage":

        round_option = st.selectbox(
            "🗂 Select Round",
            ["ROUND 1 CUTOFF","ROUND 2 CUTOFF","ROUND 3 CUTOFF","SPOT"]
        )

    else:

        round_option = st.selectbox(
            "🗂 Select Round",
            ["ROUND 1","ROUND 2","ROUND 2 UPGRADATION 5","SPOT"]
        )

inflation = st.slider("📈 Expected Inflation (%)",0.0,5.0,2.0)

# ---------------- PREDICTION ----------------
if st.button("🚀 Predict Now"):

    with st.spinner("Analyzing cutoffs..."):
        time.sleep(1)

    results=[]

    for _,row in filtered_df.iterrows():

        current=row[round_option]

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

    st.markdown("## 📋 Results")

    st.dataframe(result_df,use_container_width=True)

# ---------------- RANK ↔ PERCENTILE TOOL ----------------
st.markdown("---")
st.markdown("## 📊 Rank ↔ Percentile Calculator")

colA,colB = st.columns(2)

with colA:

    st.markdown("### Percentile → Rank")

    percentile = st.number_input(
        "Enter Percentile",
        min_value=0.0,
        max_value=100.0,
        step=0.01
    )

    if st.button("Calculate Rank"):

        rank = (100 - percentile) * 16000

        st.success(f"Expected Rank: {int(rank)}")

with colB:

    st.markdown("### Rank → Percentile")

    rank_input = st.number_input(
        "Enter Rank",
        min_value=1,
        max_value=2000000
    )

    if st.button("Calculate Percentile"):

        percentile_calc = 100 - (rank_input / 16000)

        st.success(f"Expected Percentile: {round(percentile_calc,3)}")
# ---------------- SAFEST PERCENTILE FINDER ----------------

st.markdown("---")
st.markdown("## 🎯 Safest Percentile for Preferred Branch Type")

preference = st.selectbox(
    "Select Your Preferred Field",
    ["Coding Branches","Electrical / Core Branches"]
)

if st.button("Find Safest Percentile"):

    jee_df = pd.read_excel("jee_cutoff.xlsx")

    if preference == "Coding Branches":

        keywords = ["computer","ai","software","data","it"]

    else:

        keywords = ["electrical","electronics","robotics","vlsi"]

    filtered = jee_df[
        jee_df["Branch Name"].str.lower().apply(
            lambda x: any(k in x for k in keywords)
        )
    ]

    if filtered.empty:

        st.warning("No branches matched.")

    else:

        r1 = filtered["ROUND 1"].max()
        r2 = filtered["ROUND 2"].max()

        safest_rank = max(r1,r2)

        safest_percentile = 100 - (safest_rank / 16000)

        st.success(f"Safest Percentile ≈ {round(safest_percentile,3)}")

        st.caption("Calculated using Round 1 and Round 2 closing ranks.")
        # ---------------- BRANCH SAFETY ANALYZER ----------------

st.markdown("---")
st.markdown("## 🎯 Branch Wise Safest Percentile Analysis")

jee_df = pd.read_excel("jee_cutoff.xlsx")

branches = jee_df["Branch Name"].unique()

results = []

for _,row in jee_df.iterrows():

    r1 = row["ROUND 1"]
    r2 = row["ROUND 2"]

    # safest rank = worse closing rank
    safest_rank = max(r1,r2)

    safest_percentile = 100 - (safest_rank/16000)

    results.append({
        "Branch":row["Branch Name"],
        "Round 1 Rank":r1,
        "Round 2 Rank":r2,
        "Safest Rank":safest_rank,
        "Safest Percentile":round(safest_percentile,3),
        "Basis":"Calculated from Round 1 & Round 2 closing ranks"
    })

safety_df = pd.DataFrame(results)

safety_df = safety_df.sort_values(by="Safest Percentile",ascending=False)

st.dataframe(safety_df,use_container_width=True)
# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built with ❤️ by Anshul")


