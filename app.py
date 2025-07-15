
import streamlit as st
import pandas as pd
import os
import random
import string
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mentee Tracker", layout="wide")

if not os.path.exists("data"):
    os.makedirs("data")

def generate_access_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_user_key(email_or_phone):
    key_file = "data/access_keys.csv"
    if not os.path.exists(key_file):
        pd.DataFrame(columns=["user", "key"]).to_csv(key_file, index=False)
    df = pd.read_csv(key_file)
    if email_or_phone in df["user"].values:
        return df[df["user"] == email_or_phone]["key"].values[0]
    else:
        new_key = generate_access_key()
        pd.DataFrame([{"user": email_or_phone, "key": new_key}]).to_csv(key_file, mode="a", header=False, index=False)
        return new_key

st.title("🔐 Mentee Tracker System")
role = st.radio("Login as", ["Student", "Mentor"], horizontal=True)

email = st.text_input("📧 Enter Email")
phone = st.text_input("📱 Enter Phone Number")
user_identifier = email if email else phone
access_key = get_user_key(user_identifier) if (email or phone) else None

if access_key and role == "Student":
    st.info(f"Access Key (for demo): `{access_key}`")

user_key_input = st.text_input("🔑 Enter Access Key", type="password")

if user_key_input == access_key or role == "Mentor":
    st.success("Login Successful ✅")
    tabs = st.tabs(["🎓 Marks", "📅 Meetings", "🏆 Activity Points", "📊 Mentor Dashboard"])

    # MARKS TAB
    with tabs[0]:
        st.header("🎓 Academic Marks Entry")
        semester = st.selectbox("📚 Select Semester", [f"{i}th Sem" for i in range(1, 9)])
        sub_count = st.number_input("📌 Number of Subjects", min_value=1, max_value=12, value=4)
        grades = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C+": 5, "C": 4, "PP": 0}
        data, total_credits, weighted_score = [], 0, 0

        for i in range(sub_count):
            sub = st.text_input(f"Subject {i+1}", key=f"sub{i}")
            m1 = st.number_input(f"MSE1 - {sub}", 0, 50, key=f"m1{i}")
            m2 = st.number_input(f"MSE2 - {sub}", 0, 50, key=f"m2{i}")
            see = st.number_input(f"SEE - {sub}", 0, 100, key=f"see{i}")
            task = st.number_input(f"Task - {sub}", 0, 20, key=f"task{i}")
            grade = st.selectbox(f"Grade - {sub}", list(grades.keys()), key=f"gr{i}")
            credit = st.number_input(f"Credits - {sub}", 1, 5, key=f"cr{i}")
            gp = grades[grade]
            total_credits += credit
            weighted_score += gp * credit
            data.append([user_identifier, semester, sub, m1, m2, see, task, grade, credit])

        if st.button("💾 Save Marks"):
            df = pd.DataFrame(data, columns=["ID", "Semester", "Subject", "MSE1", "MSE2", "SEE", "Task", "Grade", "Credits"])
            df.to_csv(f"data/marks_{user_identifier}_{semester.replace(' ', '_')}.csv", index=False)
            st.success("Marks Saved Successfully")

        if total_credits:
            st.info(f"📈 CGPA for {semester}: {round(weighted_score / total_credits, 2)}")

    # MEETINGS TAB
    with tabs[1]:
        st.header("📅 Mentor Meeting Log")
        semester = st.selectbox("📚 Select Semester", [f"{i}th Sem" for i in range(1, 9)], key="meeting_sem")
        meeting_date = st.date_input("🗓 Date")
        discussion = st.text_area("📝 What was discussed?")
        if st.button("💾 Save Meeting Log"):
            df = pd.DataFrame([[user_identifier, semester, str(meeting_date), discussion]], columns=["ID", "Semester", "Date", "Discussion"])
            df.to_csv(f"data/meeting_{user_identifier}_{semester.replace(' ', '_')}.csv", mode="a", header=not os.path.exists(f"data/meeting_{user_identifier}_{semester.replace(' ', '_')}.csv"), index=False)
            st.success("Meeting Logged Successfully")

    # ACTIVITY TAB
    with tabs[2]:
        st.header("🏆 Activity Points Upload")
        semester = st.selectbox("📚 Select Semester", [f"{i}th Sem" for i in range(1, 9)], key="activity_sem")
        activity_name = st.text_input("🏅 Activity Name")
        certificate_link = st.text_input("🔗 Certificate Link (Google Drive)")
        if st.button("💾 Save Activity"):
            df = pd.DataFrame([[user_identifier, semester, activity_name, certificate_link]], columns=["ID", "Semester", "Activity", "Link"])
            df.to_csv(f"data/activity_{user_identifier}_{semester.replace(' ', '_')}.csv", mode="a", header=not os.path.exists(f"data/activity_{user_identifier}_{semester.replace(' ', '_')}.csv"), index=False)
            st.success("Activity Saved Successfully")

    # MENTOR DASHBOARD
    with tabs[3]:
        st.header("📊 Mentor Dashboard")
        if role != "Mentor":
            st.warning("Login as Mentor to view dashboard")
        else:
            all_files = os.listdir("data")
            student_ids = sorted(set(f.split("_")[1] for f in all_files if f.startswith("marks_")))
            selected_student = st.selectbox("Select a student", student_ids)
            selected_sem = st.selectbox("Select Semester", [f"{i}th Sem" for i in range(1, 9)], key="mentor_sem")
            marks_path = f"data/marks_{selected_student}_{selected_sem.replace(' ', '_')}.csv"
            if os.path.exists(marks_path):
                df = pd.read_csv(marks_path)
                st.subheader(f"📄 Marks Data for {selected_student} - {selected_sem}")
                st.dataframe(df)

                # CGPA calculation
                grade_map = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C+": 5, "C": 4, "PP": 0}
                df["GPoints"] = df["Grade"].map(grade_map)
                df["Weighted"] = df["GPoints"] * df["Credits"]
                cgpa = round(df["Weighted"].sum() / df["Credits"].sum(), 2)
                st.success(f"🎓 CGPA: {cgpa}")

                # Graph
                fig, ax = plt.subplots()
                ax.bar(df["Subject"], df["SEE"], label="SEE", color='skyblue')
                ax.bar(df["Subject"], df["MSE1"], bottom=df["SEE"], label="MSE1", color='orange')
                ax.set_ylabel("Marks")
                ax.set_title(f"SEE + MSE1 Comparison for {selected_student} - {selected_sem}")
                ax.legend()
                st.pyplot(fig)
            else:
                st.warning("❌ No marks data found for this student and semester.")
