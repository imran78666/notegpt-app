import streamlit as st
import io
import time
from utils.pdf_parser import extract_text
from utils.summarizer import get_summary
from utils.qa_engine import load_chunks, answer_question
from utils.quiz_generator import generate_quiz, generate_quiz_by_topic
from utils.points_manager import add_points, get_points
from utils.ml_model import predict_performance

# ✅ Stop unauthenticated access
if "username" not in st.session_state:
    st.warning("Please login first to access this page.")
    st.stop()

st.set_page_config(page_title="NoteGPT Quiz", layout="wide", page_icon="📚")
st.title("📚 NoteGPT - AI Quiz Section")

# ----------------- 📄 Upload PDF on Main Page -----------------
st.header("1️⃣ Upload PDF File")
pdf = st.file_uploader("Upload your study material (PDF only)", type=["pdf"])

if pdf:
    text = extract_text(pdf)
    st.success("📄 PDF successfully processed!")

    with st.expander("🔍 Preview extracted text (Top 30 Lines)"):
        preview = "\n".join(text.split("\n")[:30])
        st.text_area("Preview:", value=preview, height=300)

    # ----------------- 🔎 Choose Action on Main Page -----------------
    st.header("2️⃣ Choose What You Want to Do")
    option = st.selectbox("Select Action:", [
        "Quick Summary",
        "Quiz for Complete PDF",
        "Ask on Specific Topic",
        "Quiz by Topic & Question Count"
    ])

    chunks = load_chunks(text)

    # ------------------- QUICK SUMMARY -------------------
    if option == "Quick Summary":
        st.header("📄 Summary")
        if st.button("Generate Summary"):
            with st.spinner("Generating detailed summary..."):
                summary = get_summary(text)
                add_points(st.session_state.username, 2)
            st.markdown(summary)

    # ------------------- QUIZ FOR COMPLETE PDF -------------------
    elif option == "Quiz for Complete PDF":
        st.header("🧠 Quiz from Entire PDF")

        if "quiz_data" not in st.session_state:
            qcount = st.radio("How many questions?", [5, 10, 15], key="qcount_main")
            if st.button("Generate Quiz"):
                quiz = generate_quiz(text, qcount)
                st.session_state.quiz_data = quiz
                st.session_state.answers = {}
                st.session_state.submitted = False
                st.session_state.quiz_start_time = time.time()
                st.rerun()

        if "quiz_data" in st.session_state:
            quiz = st.session_state.quiz_data

            st.subheader("Answer the following questions:")
            for i, (question, choices, correct, hint, explanation) in enumerate(quiz):
                st.markdown(f"### **Q{i+1}:** {question}")
                st.session_state.answers[i] = st.radio(
                    "Choose an answer:", choices, key=f"ans_{i}"
                )
                show_hint = st.toggle("💡 Show Hint", key=f"hint_{i}")
                if show_hint:
                    st.info(hint)

            if not st.session_state.get("submitted"):
                if st.button("✅ Submit Quiz"):
                    quiz_end_time = time.time()
                    total_time = int(quiz_end_time - st.session_state.quiz_start_time)
                    score = sum(
                        1 for i, (_, _, correct, _, _) in enumerate(quiz)
                        if st.session_state.answers.get(i, "") == correct
                    )
                    percent_score = (score / len(quiz)) * 100

                    st.session_state.score = score
                    st.session_state.percent_score = percent_score
                    st.session_state.quiz_time_sec = total_time
                    st.session_state.submitted = True

                    add_points(st.session_state.username, score)
                    st.rerun()

        if st.session_state.get("submitted"):
            quiz = st.session_state.quiz_data
            st.header(f"🎯 Your Final Score: {st.session_state.score}/{len(quiz)}")
            st.write(f"📊 Percentage Score: {st.session_state.percent_score:.2f}%")
            st.write(f"⏱️ Time Taken: {st.session_state.quiz_time_sec} seconds")

            try:
                result = predict_performance(
                    st.session_state.percent_score,
                    st.session_state.quiz_time_sec,
                    1  # Defaulting to 1 attempt for now
                )
                if result == "pass":
                    st.success("🔮 Prediction: Likely to PASS")
                else:
                    st.error("🔮 Prediction: Likely to FAIL")
            except Exception as e:
                st.warning(f"Prediction failed: {e}")

            for i, (q, choices, correct, hint, explanation) in enumerate(quiz):
                st.markdown(f"### **Q{i+1}:** {q}")
                user_answer = st.session_state.answers.get(i, "")
                st.write(f"Your Answer: **{user_answer}**")
                if user_answer == correct:
                    st.success("✅ Correct")
                else:
                    st.error(f"❌ Incorrect. Correct Answer: {correct}")
                st.caption(f"Explanation: {explanation}")

            buffer = io.StringIO()
            report = ""
            for i, (q, choices, correct, hint, explanation) in enumerate(quiz):
                user_answer = st.session_state.answers.get(i, "")
                report += f"Q{i+1}: {q}\nYour Answer: {user_answer}\nCorrect: {correct}\n\n"
            buffer.write(f"Name: {st.session_state.username}\nScore: {st.session_state.score}/{len(quiz)}\nTime: {st.session_state.quiz_time_sec} sec\nPercentage: {st.session_state.percent_score:.2f}%\n\n{report}")
            st.download_button("📄 Download Report", data=buffer.getvalue(), file_name=f"{st.session_state.username}_quiz_report.txt")

            if st.button("🔄 Regenerate New Quiz"):
                for key in ["quiz_data", "answers", "score", "percent_score", "quiz_time_sec", "submitted"]:
                    st.session_state.pop(key, None)
                st.rerun()

    # ------------------- ASK ON SPECIFIC TOPIC -------------------
    elif option == "Ask on Specific Topic":
        st.subheader("🔎 Ask a Topic")
        topic = st.text_input("Enter your question or topic:")
        if topic:
            with st.spinner("Searching the document for answer..."):
                answer = answer_question(topic, chunks)
            if answer.strip():
                st.write(answer)
            else:
                st.warning("Sorry, I couldn't find information on that topic in the PDF.")

    # ------------------- QUIZ BY TOPIC & QUESTION COUNT -------------------
    elif option == "Quiz by Topic & Question Count":
        st.subheader("🎯 Topic-Based Quiz")
        topic = st.text_input("Enter topic keyword (e.g., Photosynthesis):")
        num_q = st.radio("Select number of questions", [5, 10, 15], key="qcount_topic")
        if st.button("Generate Quiz", key="topic_generate") and topic:
            quiz = generate_quiz_by_topic(text, topic, int(num_q))
            st.session_state.topic_quiz = quiz
            st.session_state.topic_answers = {}
            st.session_state.topic_submitted = False
            st.session_state.quiz_start_time = time.time()
            st.rerun()

        if "topic_quiz" in st.session_state:
            quiz = st.session_state.topic_quiz
            st.subheader("Answer the following questions:")

            for i, (question, choices, correct, hint, explanation) in enumerate(quiz):
                st.markdown(f"### **Q{i+1}:** {question}")
                st.session_state.topic_answers[i] = st.radio(
                    "Choose an answer:", choices, key=f"topic_ans_{i}"
                )
                show_hint = st.toggle("💡 Show Hint", key=f"topic_hint_{i}")
                if show_hint:
                    st.info(hint)

            if not st.session_state.get("topic_submitted"):
                if st.button("Submit Topic Quiz"):
                    quiz_end_time = time.time()
                    total_time = int(quiz_end_time - st.session_state.quiz_start_time)
                    score = sum(
                        1 for i, (_, _, correct, _, _) in enumerate(quiz)
                        if st.session_state.topic_answers.get(i, "") == correct
                    )
                    percent_score = (score / len(quiz)) * 100

                    st.session_state.topic_score = score
                    st.session_state.topic_percent = percent_score
                    st.session_state.topic_time_sec = total_time
                    st.session_state.topic_submitted = True
                    st.rerun()

        if st.session_state.get("topic_submitted"):
            quiz = st.session_state.topic_quiz
            st.header(f"🎯 Your Final Score: {st.session_state.topic_score}/{len(quiz)}")
            st.write(f"📊 Percentage Score: {st.session_state.topic_percent:.2f}%")
            st.write(f"⏱️ Time Taken: {st.session_state.topic_time_sec} seconds")

            try:
                result = predict_performance(
                    st.session_state.topic_percent,
                    st.session_state.topic_time_sec,
                    1
                )
                if result == "pass":
                    st.success("🔮 Prediction: Likely to PASS")
                else:
                    st.error("🔮 Prediction: Likely to FAIL")
            except Exception as e:
                st.warning(f"Prediction failed: {e}")

            for i, (q, choices, correct, hint, explanation) in enumerate(quiz):
                st.markdown(f"### **Q{i+1}:** {q}")
                user_answer = st.session_state.topic_answers.get(i, "")
                st.write(f"Your Answer: **{user_answer}**")
                if user_answer == correct:
                    st.success("✅ Correct")
                else:
                    st.error(f"❌ Incorrect. Correct Answer: {correct}")
                st.caption(f"Explanation: {explanation}")

            buffer = io.StringIO()
            report = ""
            for i, (q, choices, correct, hint, explanation) in enumerate(quiz):
                user_answer = st.session_state.topic_answers.get(i, "")
                report += f"Q{i+1}: {q}\nYour Answer: {user_answer}\nCorrect: {correct}\n\n"
            buffer.write(f"Name: {st.session_state.username}\nScore: {st.session_state.topic_score}/{len(quiz)}\nTime: {st.session_state.topic_time_sec} sec\nPercentage: {st.session_state.topic_percent:.2f}%\n\n{report}")
            st.download_button("📄 Download Report", data=buffer.getvalue(), file_name=f"{st.session_state.username}_topic_quiz.txt")

            if st.button("🔄 Regenerate New Topic Quiz"):
                for key in ["topic_quiz", "topic_answers", "topic_score", "topic_percent", "topic_time_sec", "topic_submitted"]:
                    st.session_state.pop(key, None)
                st.rerun()

else:
    st.warning("📂 Please upload a PDF to get started.")