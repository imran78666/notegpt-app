import json
import os


def load_points():
    if os.path.exists("points.json"):
        with open("points.json", "r") as f:
            return json.load(f)
    return {}


def save_points(points):
    with open("points.json", "w") as f:
        json.dump(points, f)


def add_points(username, pts):
    points = load_points()
    points[username] = points.get(username, 0) + pts
    save_points(points)


def get_points(username):
    points = load_points()
    return points.get(username, 0)


def get_leaderboard():
    points = load_points()
    leaderboard = sorted(points.items(), key=lambda x: x[1], reverse=True)
    return leaderboard


def get_user_level(points):
    if points >= 120:
        return "Advanced"
    elif points >= 70:
        return "Pro"
    elif points >= 30:
        return "Beginner"
    else:
        return "New User"


def show_leaderboard():
    import streamlit as st
    st.header("🏆 Leaderboard")
    leaderboard = get_leaderboard()
    for i, (username, pts) in enumerate(leaderboard, start=1):
        st.write(f"**{i}. {username}** — {pts} points")
