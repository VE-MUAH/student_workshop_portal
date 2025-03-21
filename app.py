import streamlit as st
import sqlite3
import qrcode
import io
import smtplib
import pandas as pd
import matplotlib.pyplot as plt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------------- Database Setup ---------------------- #
def connect_db():
    """Ensures the database and required columns exist."""
    conn = sqlite3.connect("data/workshop.db")
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT NOT NULL,
                        institution TEXT NOT NULL,
                        course TEXT NOT NULL,
                        workshop TEXT NOT NULL,
                        referrer TEXT DEFAULT NULL
                    )''')

    # Check if "referrer" column exists, if not, add it
    cursor.execute("PRAGMA table_info(students)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "referrer" not in columns:
        cursor.execute("ALTER TABLE students ADD COLUMN referrer TEXT DEFAULT NULL")
        conn.commit()
    
    conn.close()

connect_db()  # Ensure database is set up correctly

# ---------------------- Helper Functions ---------------------- #
def add_student(name, email, phone, institution, course, workshop, referrer=None):
    """Adds a student to the database."""
    try:
        conn = sqlite3.connect("data/workshop.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, email, phone, institution, course, workshop, referrer) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (name, email, phone, institution, course, workshop, referrer))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Email already exists

def generate_qr(data):
    """Generates a QR code with the given data."""
    qr = qrcode.make(data)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return buf

def send_email(name, email, workshop):
    """Sends a confirmation email (dummy function)."""
    sender_email = "your_email@gmail.com"
    sender_password = "your_password"
    receiver_email = email

    subject = "Workshop Registration Confirmation"
    body = f"Hello {name},\n\nYou have successfully registered for the {workshop} workshop.\n\nBest Regards,\nWorkshop Team"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
    except Exception as e:
        st.write('sent')
        # st.warning("⚠️ Could not send email")

# ---------------------- Streamlit UI ---------------------- #
st.title("🎓 Workshop Registration Portal")
st.subheader("Register and receive a confirmation email with a QR Code!")

with st.form("registration_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    institution = st.text_input("Institution")
    course = st.text_input("Course")
    workshop = st.selectbox("Select a Workshop", ["","Cloud computing","Artificial Intelligence","Python Basics", "Data Science", "Machine Learning","Data Analysis","Data Visualisation", "Web Development", "Django for backend"])
    referrer = st.text_input("Referral Code (Optional)")
    submit_button = st.form_submit_button("Register for Workshop")

if submit_button:
    if name and email and phone and institution and course and workshop:
        if add_student(name, email, phone, institution, course, workshop, referrer):
            send_email(name, email, workshop)
            qr_buf = generate_qr(f"{name} - {workshop}")
            st.success(f"✅ Registration successful for {name}!")
            st.image(qr_buf, caption="Scan this QR for your registration details")
        else:
            st.error("⚠️ Email already registered!")
    else:
        st.warning("⚠️ Please fill out all fields.")

# ---------------------- Admin Portal ---------------------- #
st.sidebar.title("🔑 Admin Portal")
admin_access = st.sidebar.checkbox("Admin Login")

if admin_access:
    admin_password = st.sidebar.text_input("Enter Admin Password", type="password")
    
    if admin_password == "VICENTIAemuah@2002":  
        st.sidebar.success("✅ Access Granted")

        # Fetch data once at the beginning
        conn = sqlite3.connect("data/workshop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM students")
        data = cursor.fetchall()

        cursor.execute("SELECT name, email, phone, institution, course, workshop, referrer FROM students")
        data_full = cursor.fetchall()
        conn.close()

        if data:
            student_ids = [f"{row[0]} - {row[1]}" for row in data]

            if st.sidebar.button("View Registrations"):
                if data_full:
                    df = pd.DataFrame(data_full, columns=["Name", "Email", "Phone", "Institution", "Course", "Workshop", "Referrer"])
                    st.dataframe(df)

                    df_counts = df["Workshop"].value_counts().reset_index()
                    df_counts.columns = ["workshop", "count"]

                    if not df_counts.empty:
                        fig, ax = plt.subplots(figsize=(6, 4))  
                        ax.bar(df_counts["workshop"], df_counts["count"], color=['blue', 'green', 'orange'])
                        ax.set_xlabel("Workshop")
                        ax.set_ylabel("Number of Registrations")
                        ax.set_title("Workshop Registrations")
                        st.pyplot(fig, clear_figure=True)
                        plt.close(fig)
                    else:
                        st.warning("No registrations yet.")

            # Export data and provide a download button
            if st.button("📥 Export Data to CSV"):
                df = pd.DataFrame(data_full, columns=["Name", "Email", "Phone", "Institution", "Course", "Workshop", "Referrer"])

                # Save CSV to a BytesIO buffer instead of disk
                csv_buffer = io.BytesIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)

                # Provide a download button
                st.download_button(
                    label="📂 Download CSV",
                    data=csv_buffer,
                    file_name="registered_students.csv",
                    mime="text/csv"
                )

                st.success("✅ Data exported successfully!")

            st.subheader("❌ Delete a Student")
            selected_student = st.selectbox("Select Student to Remove", student_ids)
            if st.button("Delete"):
                student_id = selected_student.split(" - ")[0]
                conn = sqlite3.connect("data/workshop.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
                conn.commit()
                conn.close()
                st.success("✅ Student deleted!")
                st.rerun()









# import streamlit as st
# import sqlite3
# import qrcode
# import io
# import smtplib
# import pandas as pd
# import matplotlib.pyplot as plt
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # ---------------------- Database Setup ---------------------- #
# def connect_db():
#     """Ensures the database and required columns exist."""
#     conn = sqlite3.connect("data/workshop.db")
#     cursor = conn.cursor()
    
#     # Create table if not exists
#     cursor.execute('''CREATE TABLE IF NOT EXISTS students (
#                         id INTEGER PRIMARY KEY AUTOINCREMENT,
#                         name TEXT NOT NULL,
#                         email TEXT UNIQUE NOT NULL,
#                         phone TEXT NOT NULL,
#                         institution TEXT NOT NULL,
#                         course TEXT NOT NULL,
#                         workshop TEXT NOT NULL,
#                         referrer TEXT DEFAULT NULL
#                     )''')

#     # Check if "referrer" column exists, if not, add it
#     cursor.execute("PRAGMA table_info(students)")
#     columns = [column[1] for column in cursor.fetchall()]
    
#     if "referrer" not in columns:
#         cursor.execute("ALTER TABLE students ADD COLUMN referrer TEXT DEFAULT NULL")
#         conn.commit()
    
#     conn.close()

# connect_db()  # Ensure database is set up correctly

# # ---------------------- Helper Functions ---------------------- #
# def add_student(name, email, phone, institution, course, workshop, referrer=None):
#     """Adds a student to the database."""
#     try:
#         conn = sqlite3.connect("data/workshop.db")
#         cursor = conn.cursor()
#         cursor.execute("INSERT INTO students (name, email, phone, institution, course, workshop, referrer) VALUES (?, ?, ?, ?, ?, ?, ?)", 
#                        (name, email, phone, institution, course, workshop, referrer))
#         conn.commit()
#         conn.close()
#         return True
#     except sqlite3.IntegrityError:
#         return False  # Email already exists

# def generate_qr(data):
#     """Generates a QR code with the given data."""
#     qr = qrcode.make(data)
#     buf = io.BytesIO()
#     qr.save(buf, format="PNG")
#     buf.seek(0)
#     return buf

# def send_email(name, email, workshop):
#     """Sends a confirmation email (dummy function)."""
#     sender_email = "your_email@gmail.com"
#     sender_password = "your_password"
#     receiver_email = email

#     subject = "Workshop Registration Confirmation"
#     body = f"Hello {name},\n\nYou have successfully registered for the {workshop} workshop.\n\nBest Regards,\nWorkshop Team"

#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = receiver_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.starttls()
#         server.login(sender_email, sender_password)
#         server.sendmail(sender_email, receiver_email, msg.as_string())
#         server.quit()
#     except Exception as e:
#         st.write('sent')
#         # st.warning("⚠️ Could not send email")

# # ---------------------- Streamlit UI ---------------------- #
# st.title("🎓 Workshop Registration Portal")
# st.subheader("Register and receive a confirmation email with a QR Code!")

# with st.form("registration_form"):
#     name = st.text_input("Full Name")
#     email = st.text_input("Email Address")
#     phone = st.text_input("Phone Number")
#     institution = st.text_input("Institution")
#     course = st.text_input("Course")
#     workshop = st.selectbox("Select a Workshop", ["","Cloud computing","Artificial Intelligence","Python Basics", "Data Science", "Machine Learning","Data Analysis","Data Visualisation", "Web Development", "Django for backend"])
#     referrer = st.text_input("Referral Code (Optional)")
#     submit_button = st.form_submit_button("Register for Workshop")

# if submit_button:
#     if name and email and phone and institution and course and workshop:
#         if add_student(name, email, phone, institution, course, workshop, referrer):
#             send_email(name, email, workshop)
#             qr_buf = generate_qr(f"{name} - {workshop}")
#             st.success(f"✅ Registration successful for {name}!")
#             st.image(qr_buf, caption="Scan this QR for your registration details")
#         else:
#             st.error("⚠️ Email already registered!")
#     else:
#         st.warning("⚠️ Please fill out all fields.")

# # ---------------------- Admin Portal ---------------------- #
# st.sidebar.title("🔑 Admin Portal")
# admin_access = st.sidebar.checkbox("Admin Login")

# if admin_access:
#     admin_password = st.sidebar.text_input("Enter Admin Password", type="password")
    
#     if admin_password == "VICENTIAemuah@2002":  
#         st.sidebar.success("✅ Access Granted")

#         # Fetch data once at the beginning
#         conn = sqlite3.connect("data/workshop.db")
#         cursor = conn.cursor()
#         cursor.execute("SELECT id, name FROM students")
#         data = cursor.fetchall()

#         cursor.execute("SELECT name, email, phone, institution, course, workshop, referrer FROM students")
#         data_full = cursor.fetchall()
#         conn.close()

#         if data:
#             student_ids = [f"{row[0]} - {row[1]}" for row in data]

#             if st.sidebar.button("View Registrations"):
#                 if data_full:
#                     df = pd.DataFrame(data_full, columns=["Name", "Email", "Phone", "Institution", "Course", "Workshop", "Referrer"])
#                     st.dataframe(df)

#                     df_counts = df["Workshop"].value_counts().reset_index()
#                     df_counts.columns = ["workshop", "count"]

#                     if not df_counts.empty:
#                         fig, ax = plt.subplots(figsize=(6, 4))  
#                         ax.bar(df_counts["workshop"], df_counts["count"], color=['blue', 'green', 'orange'])
#                         ax.set_xlabel("Workshop")
#                         ax.set_ylabel("Number of Registrations")
#                         ax.set_title("Workshop Registrations")
#                         st.pyplot(fig, clear_figure=True)
#                         plt.close(fig)
#                     else:
#                         st.warning("No registrations yet.")

#             if st.button("📥 Export Data to CSV"):
#                 df = pd.DataFrame(data_full, columns=["Name", "Email", "Phone", "Institution", "Course", "Workshop", "Referrer"])
#                 df.to_csv("data/registered_students.csv", index=False)
#                 st.success("✅ Data exported successfully!")

#             st.subheader("❌ Delete a Student")
#             selected_student = st.selectbox("Select Student to Remove", student_ids)
#             if st.button("Delete"):
#                 student_id = selected_student.split(" - ")[0]
#                 conn = sqlite3.connect("data/workshop.db")
#                 cursor = conn.cursor()
#                 cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
#                 conn.commit()
#                 conn.close()
#                 st.success("✅ Student deleted!")
#                 st.rerun()







