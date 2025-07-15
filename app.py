import streamlit as st
import pandas as pd
import os
import random
import string
import altair as alt

# ---------------------------- CONFIG ---------------------------- #
st.set_page_config(page_title="Mentee Tracker", layout="wide")

DATA_DIR = "data"
STUDENT_DB = "students.csv"
ADMIN_PASS = "mentor123"

grade_point_map = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C+": 5,
    "C": 4,
    "PP": 3
}

# ---------------------------- UTILITIES ---------------------------- #
def generate_key(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_user_file(access_key, section):
    return os.path.join(DATA_DIR, f"{access_key}_{section}.csv")

def init_student_db():
    if not os.path.exists(STUDENT_DB):
        df = pd.DataFrame(columns=["email", "phone", "access_key"])
        df.to_csv(STUDENT_DB, index=False)

def load_student(access_key):
    return pd.read_csv(STUDENT_DB).query("access_key == @access_key")

def load_data(file):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame()

# ---------------------------- AUTH ---------------------------- #
st.title("🔐 Mentee Tracker System")

init_student_db()

auth_type = st.radio("Login as", ["Student", "Mentor"])

if auth_type == "Student":
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("📧 Enter Email")
    with col2:
        phone = st.text_input("📱 Enter Phone Number")

    if st.button("Get Access Key"):
        if email and phone:
            students = pd.read_csv(STUDENT_DB)
            existing = students[(students['email'] == email) | (students['phone'] == phone)]
            if not existing.empty:
                access_key = existing.iloc[0]['access_key']
                st.success(f"Welcome back! Your Access Key: `{access_key}`")
            else:
                access_key = generate_key()
                students.loc[len(students.index)] = [email, phone, access_key]
                students.to_csv(STUDENT_DB, index=False)
                st.success(f"New Access Key Generated: `{access_key}`")
    access_key_input = st.text_input("Enter your Access Key to Continue")

    if access_key_input and access_key_input in pd.read_csv(STUDENT_DB)['access_key'].values:
        st.success("Login successful ✅")
        tabs = st.tabs(["🎓 Marks", "📅 Meetings", "🏆 Activity Points"])

        # ------------ MARKS SECTION ------------ #
        with tabs[0]:
            st.header("🎓 Academic Marks Entry")
            subject = st.text_input("Subject Name")
            mse1 = st.number_input("MSE 1", 0, 50)
            mse2 = st.number_input("MSE 2", 0, 50)
            cie = mse1 + mse2
            see = st.number_input("SEE", 0, 100)
            task = st.number_input("Task", 0, 10)
            grade = st.selectbox("Grade", list(grade_point_map.keys()))
            credits = st.number_input("Credits", 1, 5)

            if st.button("Save Subject Marks"):
                marks_file = get_user_file(access_key_input, "marks")
                total_marks = cie + see + task
                new_entry = pd.DataFrame([{
                    "Subject": subject,
                    "MSE1": mse1,
                    "MSE2": mse2,
                    "CIE": cie,
                    "SEE": see,
                    "Task": task,
                    "Grade": grade,
                    "Grade Point": grade_point_map[grade],
                    "Credits": credits,
                    "Total Marks": total_marks
                }])
                file_exists = os.path.exists(marks_file)
                new_entry.to_csv(marks_file, mode="a", index=False, header=not file_exists)
                st.success("Marks saved!")

            # Show marks + CGPA
            marks_file = get_user_file(access_key_input, "marks")
            df = load_data(marks_file)
            if not df.empty:
                st.subheader("📊 Your Subjects and CGPA")
                st.dataframe(df)
                total_credits = df['Credits'].sum()
                weighted_sum = (df['Credits'] * df['Grade Point']).sum()
                cgpa = weighted_sum / total_credits if total_credits else 0
                st.success(f"🎯 Your CGPA: **{round(cgpa, 2)}**")

                chart = alt.Chart(df).mark_bar().encode(
                    x='Subject', y='Total Marks', color='Grade'
                )
                st.altair_chart(chart, use_container_width=True)

        # ------------ MEETING SECTION ------------ #
        with tabs[1]:
            st.header("📅 Mentor Meeting Log")
            meet_date = st.date_input("Meeting Date")
            discussion = st.text_area("What was discussed?")

            if st.button("Save Meeting Log"):
                meet_file = get_user_file(access_key_input, "meetings")
                new_entry = pd.DataFrame([{
                    "Date": meet_date,
                    "Discussion": discussion
                }])
                file_exists = os.path.exists(meet_file)
                new_entry.to_csv(meet_file, mode="a", index=False, header=not file_exists)
                st.success("Meeting details saved!")

        # ------------ ACTIVITY SECTION ------------ #
        with tabs[2]:
            st.header("🏆 Activity Points & Certificates")
            activity = st.text_input("Activity Name")
            drive_link = st.text_input("Google Drive Certificate Link")

            if st.button("Save Activity"):
                act_file = get_user_file(access_key_input, "activities")
                new_entry = pd.DataFrame([{
                    "Activity": activity,
                    "Certificate": drive_link
                }])
                file_exists = os.path.exists(act_file)
                new_entry.to_csv(act_file, mode="a", index=False, header=not file_exists)
                st.success("Activity saved!")

elif auth_type == "Mentor":
    password = st.text_input("Enter Mentor Password", type="password")
    if password == ADMIN_PASS:
        st.success("Admin access granted ✅")
        students = pd.read_csv(STUDENT_DB)
        selected_key = st.selectbox("Select Student Access Key", students['access_key'])

        tabs = st.tabs(["🎓 Marks", "📅 Meetings", "🏆 Activities"])
        with tabs[0]:
            st.header(f"Marks for {selected_key}")
            df = load_data(get_user_file(selected_key, "marks"))
            if not df.empty:
                st.dataframe(df)
                total_credits = df['Credits'].sum()
                weighted_sum = (df['Credits'] * df['Grade Point']).sum()
                cgpa = weighted_sum / total_credits if total_credits else 0
                st.success(f"CGPA: {round(cgpa, 2)}")
        with tabs[1]:
            st.header(f"Meetings for {selected_key}")
            df = load_data(get_user_file(selected_key, "meetings"))
            st.dataframe(df if not df.empty else pd.DataFrame(columns=["Date", "Discussion"]))
        with tabs[2]:
            st.header(f"Activities for {selected_key}")
            df = load_data(get_user_file(selected_key, "activities"))
            st.dataframe(df if not df.empty else pd.DataFrame(columns=["Activity", "Certificate"]))
    elif password != "":
        st.error("❌ Incorrect password.")
