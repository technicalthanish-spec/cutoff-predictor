import streamlit as st
import pandas as pd
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Cutoff Predictor Pro",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
# 🎓 Cutoff Predictor Pro  
### 🚀 Smart Round-wise Prediction + AI Counsellor Engine
""")

# ---------------- LOAD DATA ----------------
df = pd.read_excel("cutoff_data.xlsx")

# ---------------- INPUT SECTION ----------------
with st.container():
    st.markdown("## 🔍 Enter Your Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        percentage = st.number_input("🎯 Your Percentage", min_value=0.0, max_value=100.0)

    with col2:
        category = st.selectbox("📂 Category", df["Category"].unique())

    with col3:
        round_option = st.selectbox(
            "🗂 Select Round (Base View)",
            ["ROUND 1 CUTOFF", "ROUND 2 CUTOFF", "ROUND 3 CUTOFF", "SPOT"]
        )

    inflation = st.slider("📈 Expected Next Year Inflation (%)", 0.0, 5.0, 2.0)

# ---------------- PREDICTION ----------------
if st.button("🚀 Predict Now"):

    with st.spinner("🔍 Analyzing cutoffs and forecasting next year trends..."):
        time.sleep(1.2)

    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress.progress(i + 1)
    progress.empty()

    filtered = df[df["Category"] == category]
    results = []

    for _, row in filtered.iterrows():

        current_cutoff = row[round_option]
        predicted_cutoff = current_cutoff + (current_cutoff * inflation / 100)
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
            "Predicted Next Year Cutoff": round(predicted_cutoff, 2),
            "Safest Score Next Year": round(safest_score, 2),
            "Your Status": status
        })

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by="Safest Score Next Year")

    st.session_state["result_df"] = result_df

    # -------- SUMMARY --------
    safe_count = len(result_df[result_df["Your Status"] == "🟢 Safe"])
    borderline_count = len(result_df[result_df["Your Status"] == "🟡 Borderline"])
    risky_count = len(result_df[result_df["Your Status"] == "🔴 Risky"])

    st.markdown("## 📊 Performance Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🟢 Safe Options", safe_count)
        time.sleep(0.2)

    with col2:
        st.metric("🟡 Borderline Options", borderline_count)
        time.sleep(0.2)

    with col3:
        st.metric("🔴 Risky Options", risky_count)

    st.success("✅ Prediction Complete! Scroll down for AI insights.")

    st.markdown("## 📋 Detailed Results")
    st.dataframe(result_df, use_container_width=True)

# ---------------- AI SECTION ----------------
if "result_df" in st.session_state:

    st.markdown("---")
    st.markdown("## 🤖 AI Counsellor Recommendation")

    colA, colB = st.columns(2)

    with colA:
        user_interest = st.selectbox(
            "🎯 Your Primary Interest",
            ["Coding", "Core Engineering"]
        )

    with colB:
        risk_level = st.selectbox(
            "⚖ Risk Preference",
            ["Safe Only", "Balanced", "Aggressive"]
        )

    if st.button("🧠 Generate AI Recommendation"):

        with st.spinner("🤖 AI is analyzing your strategy..."):
            time.sleep(1)

        ai_df = df[df["Category"] == category].copy()

        # -------- Risk Based Round Selection --------
        if risk_level == "Safe Only":
            selected_round = "ROUND 1 CUTOFF"
        elif risk_level == "Balanced":
            selected_round = "ROUND 2 CUTOFF"
        else:
            selected_round = "SPOT"

        # -------- Interest Filtering --------
        if user_interest == "Coding":
            keywords = ["computer", "ai", "data", "software", "it"]
        else:
            keywords = [
                "electronics",
                "electrical",
                "mechanical",
                "civil",
                "robotics",
                "vlsi"
            ]

        ai_df = ai_df[
            ai_df["Branch Name"].str.lower().apply(
                lambda x: any(k in x for k in keywords)
            )
        ]

        if ai_df.empty:
            st.error(
                f"{user_interest} branches are not available at your current level."
            )
        else:

            ai_df["Predicted Cutoff"] = ai_df[selected_round] + (
                ai_df[selected_round] * inflation / 100
            )

            ai_df["Safest Score"] = ai_df["Predicted Cutoff"] + 3
            ai_df["Margin"] = percentage - ai_df["Safest Score"]

            ai_df = ai_df.sort_values(by="Safest Score")
            ai_df = ai_df[ai_df["Margin"] >= -2]

            if ai_df.empty:
                st.warning(
                    "No branches match your interest and risk strategy."
                )
            else:

                top_recommendations = ai_df.head(3)

                st.markdown("### 🏆 Top Recommended Branches")
                st.dataframe(
                    top_recommendations[[
                        "Branch Name",
                        "Safest Score"
                    ]],
                    use_container_width=True
                )

                best_option = top_recommendations.iloc[0]

                st.markdown("### 🧠 AI Recommendation")

                st.markdown(f"""
                <div style="padding:20px;
                background-color:#1C1F26;
                border-radius:12px;">
                <h3>🎯 Strategy Insight</h3>
                <p>You selected <b>{risk_level}</b> strategy.</p>
                <p>Prediction uses <b>{selected_round}</b> cutoff + inflation.</p>
                <p>Most strategic branch: <b>{best_option['Branch Name']}</b></p>
                <p>Required safest score: <b>{round(best_option['Safest Score'],2)}%</b></p>
                </div>
                """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built with ❤️ by Anshul | AI Cutoff Prediction Engine")