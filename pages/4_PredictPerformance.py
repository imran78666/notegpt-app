import streamlit as st
from utils.ml_model import predict_performance

st.set_page_config(page_title="Predict Performance", page_icon="📈")

st.title("📈 Predict Quiz Performance")
st.write("Use the sliders below to estimate whether a student will pass or fail a quiz.")

# Input sliders
quiz_score = st.slider("Quiz Score (%)", min_value=0, max_value=100, value=75)
quiz_time_sec = st.slider("Time Spent on Quiz (in seconds)", min_value=30, max_value=300, value=120)
num_attempts = st.slider("Number of Attempts", min_value=1, max_value=5, value=1)

# Predict button
if st.button("🔮 Predict Performance"):
    result = predict_performance(quiz_score, quiz_time_sec, num_attempts)
    
    if result == "pass":
        st.success("✅ Prediction: The student is likely to PASS the quiz.")
    else:
        st.error("❌ Prediction: The student is likely to FAIL the quiz.")
