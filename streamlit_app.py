import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# روابط الشيت
SHEET_URL = "https://docs.google.com/spreadsheets/d/11sa1GDAYCez4b17aI1hDPKJDtfj953ySj8OMYOxbzTI/edit?usp=sharing"
LESSONS_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=lessons")
QUIZZES_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=quizzes")

def load_data():
    try:
        lessons_df = pd.read_csv(LESSONS_CSV)
        courses = {}
        for _, row in lessons_df.iterrows():
            c_title = row['course_title']
            if c_title not in courses: courses[c_title] = []
            courses[c_title].append({"title": row['lesson_title'], "video": row['video_url'], "pdf": row['pdf_url']})
    except: courses = {}

    try:
        quizzes_df = pd.read_csv(QUIZZES_CSV)
        quizzes = {}
        for _, row in quizzes_df.iterrows():
            q_title = row['quiz_title']
            if q_title not in quizzes: quizzes[q_title] = []
            quizzes[q_title].append({"question": row['question_text'], "options": [row['optA'], row['optB'], row['optC'], row['optD']], "correct": row['correct_opt']})
    except: quizzes = {}
    return courses, quizzes

st.set_page_config(page_title="منصتي التعليمية", layout="wide")
courses_db, quizzes_db = load_data()

# تشغيل واجهة الطالب
st.header("🎓 بوابة الطالب التعليمية")
if "current_view" not in st.session_state: st.session_state.current_view = "sharh"

# أزرار التحكم بالتصميم المربع
st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] { display: flex !important; justify-content: center !important; gap: 25px !important; margin: 0 auto !important; }
    div.stButton > button { width: 100% !important; height: 110px !important; font-size: 26px !important; font-weight: bold !important; color: white !important; border-radius: 15px !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(1) div.stButton > button { background-color: #1A365D !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-of-type(2) div.stButton > button { background-color: #064E3B !important; }
    </style>
""", unsafe_allow_html=True)

box_sharh, box_quiz = st.columns(2)
with box_sharh:
    if st.button("📺 الشرح والدروس", key="btn_sharh"): st.session_state.current_view = "sharh"
with box_quiz:
    if st.button("📝 الامتحانات والاختبارات", key="btn_quiz"): st.session_state.current_view = "quiz"
st.markdown("---")

if st.session_state.current_view == "sharh":
    st.subheader("📺 قسم المحاضرات")
    if courses_db:
        chosen_course = st.selectbox("اختر الكورس:", list(courses_db.keys()))
        current_lesson = courses_db[chosen_course][0]
        st.video(current_lesson['video'])

elif st.session_state.current_view == "quiz":
    st.subheader("📝 قسم الامتحانات")
    if quizzes_db:
        student_name = st.text_input("✍️ أدخل اسمك الثلاثي:")
        if student_name:
            chosen_quiz = st.selectbox("اختر الامتحان:", list(quizzes_db.keys()))
            questions = quizzes_db[chosen_quiz]
            
            if f"start_{chosen_quiz}" not in st.session_state:
                st.session_state[f"start_{chosen_quiz}"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with st.form(key="quiz_form"):
                student_answers = {}
                for i, q in enumerate(questions):
                    st.write(f"**سؤال {i+1}: {q['question']}**")
                    student_answers[i] = st.radio("الخيارات:", ["A", "B", "C", "D"], key=f"q_{i}")
                
                if st.form_submit_button("📥 إرسال الإجابات"):
                    submit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    correct = sum(1 for i, q in enumerate(questions) if student_answers[i] == q['correct'])
                    score = int((correct / len(questions)) * 100)
                    
                    # 🚀 الربط السحري المباشر والمجاني بالكتابة جوة الشيت
                    try:
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        existing_data = conn.read(spreadsheet=SHEET_URL, worksheet="student_results")
                        new_row = pd.DataFrame([{
                            "student_name": student_name, "quiz_title": chosen_quiz,
                            "score": f"{score}%", "start_time": st.session_state[f"start_{chosen_quiz}"], "submit_time": submit_time
                        }])
                        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                        conn.update(spreadsheet=SHEET_URL, worksheet="student_results", data=updated_df)
                        st.success("🎉 تم حفظ النتيجة في الشيت بنجاح مجاني ومباشر!")
                    except Exception as e:
                        st.error(f"خطأ في الاتصال: {e}")
