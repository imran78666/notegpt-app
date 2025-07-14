import streamlit as st
import pandas as pd
from utils.points_manager import get_leaderboard, get_points

st.set_page_config(page_title="NoteGPT - Leaderboard", layout="wide", page_icon="🏆")
st.title("🏆 Leaderboard - NoteGPT Total Points")

# ----------------- Badge System --------------------
def get_badge(points):
    if points < 20:
        return "Beginner"
    elif points < 50:
        return "Intermediate"
    else:
        return "Master Learner"

# ----------------- Show Leaderboard --------------------
leaderboard = get_leaderboard()

if leaderboard:
    leaderboard_data = []

    for idx, (name, points) in enumerate(leaderboard, start=1):
        if idx == 1:
            rank_display = "🥇 1"
        elif idx == 2:
            rank_display = "🥈 2"
        elif idx == 3:
            rank_display = "🥉 3"
        else:
            rank_display = str(idx)

        leaderboard_data.append({
            "Rank": rank_display,
            "Username": name,
            "Points": points,
            "Badge": get_badge(points)
        })

    df = pd.DataFrame(leaderboard_data)

    # ✅ Set 'Rank' as index to remove default 0,1,2... 
    df.set_index('Rank', inplace=True)

    # ✅ Streamlit will no longer show 0,1,2...
    st.dataframe(df, use_container_width=True)

else:
    st.info("No leaderboard data yet.")


# ----------------- User-Specific Info --------------------
if "username" in st.session_state:
    username = st.session_state["username"]
    user_points = get_points(username)
    user_badge = get_badge(user_points)

    st.divider()
    st.subheader(f"👤 Your Progress ({username})")
    st.write(f"Total Points: **{user_points}**")
    st.write(f"Your Badge: **{user_badge}**")

    progress = min(user_points / 50, 1.0)
    st.progress(progress, text="Progress to Master Learner")
else:
    st.warning("🔑 Please login to see your points.")


# ----------------- Points Structure --------------------
st.divider()
st.subheader("🎯 How Points Are Calculated")

st.markdown("""
| **Action**                | **Points Awarded**  |
|----------------------------|---------------------|
| ✅ **Sign Up**             | +10 Points          |
| 📄 **Quick Summary Used**  | +2 Points           |
| 🧠 **Correct Quiz Answer** | +1 Point / Question |
| 🧠 **Attempting Full PDF Quiz** | +3 per quiz     |
| 📚 **Topic-Based Quiz**    | 0 Points            |
| 🔎 **Ask on Specific Topic** | 0 Points          |
""")

st.caption("📌 Points help track your progress and rank you on the leaderboard.")
st.markdown("🚀 Keep learning, keep growing! 📚")
