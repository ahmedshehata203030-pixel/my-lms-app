import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 🔗 1️⃣ حط رابط الشيت العادي بتاعك هنا
SHEET_URL = "ضع_رابط_ملف_جوجل_شيت_الخاص_بك_هنا"

# تحويل تلقائي للرابط عشان يقرا الأسئلة والدروس في ثانية ومن غير سيرفرات
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

st.header("🎓 بوابة الطالب التعليمية")
if "current_view" not in st.session_state: st.session_state.current_view = "sharh"

# تصميم الأزرار المربع النظيف
st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] { display: flex !important; justify-content: center !important; gap: 25px !important; }
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
    st.subheader("📺 قسم المحاضرات وفيديوهات الشرح")
    if courses_db:
        chosen_course = st.selectbox("اختر الكورس / الدبلومة:", list(courses_db.keys()))
        lessons_available = courses_db[chosen_course]
        chosen_lesson = st.selectbox("اختر الدرس المراد مشاهدته:", [l['title'] for l in lessons_available])
        current_lesson = next(l for l in lessons_available if l['title'] == chosen_lesson)
        st.video(current_lesson['video'])
        if pd.notna(current_lesson['pdf']) and current_lesson['pdf']:
            st.markdown(f"[📥 تحميل ملف الـ PDF المرفق للدرس]({current_lesson['pdf']})")

elif st.session_state.current_view == "quiz":
    st.subheader("📝 قسم الامتحانات والتقييمات")
    if quizzes_db:
        student_name = st.text_input("✍️ من فضلك أدخل اسمك الثلاثي لبدء الاختبار:")
        if student_name:
            chosen_quiz = st.selectbox("اختر الامتحان المطلوب للدخول:", list(quizzes_db.keys()))
            questions = quizzes_db[chosen_quiz]
            
            if f"start_{chosen_quiz}" not in st.session_state:
                st.session_state[f"start_{chosen_quiz}"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            with st.form(key="simple_quiz_form"):
                student_answers = {}
                for i, q in enumerate(questions):
                    st.write(f"**سؤال {i+1}: {q['question']}**")
                    student_answers[i] = st.radio("اختر الإجابة:", ["A", "B", "C", "D"], key=f"q_{i}")
                
                if st.form_submit_button("📥 إرسال الإجابات وإنهاء الامتحان"):
                    submit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    correct = sum(1 for i, q in enumerate(questions) if student_answers[i] == q['correct'])
                    score = int((correct / len(questions)) * 100)
                    
                    # 🔗 2️⃣ الربط العادي للكتابة: بيبعت النتيجة كـ Form عادي للشيت
                    # عشان يشتغل، تأكد إنك عامل الشيت "Anyone with the link is Editor"
                    try:
                        form_url = SHEET_URL.replace("/edit?usp=sharing", "/formResponse")
                        # إرسال البيانات بشكل مخفي وسريع للشيت
                        requests.post(form_url, data={
                            "submit": "Submit",
                            "student_name": student_name,
                            "quiz_title": chosen_quiz,
                            "score": f"{score}%",
                            "start_time": st.session_state[f"start_{chosen_quiz}"],
                            "submit_time": submit_time
                        })
                    except:
                        pass
                    
                    st.markdown("---")
                    if score >= 50:
                        st.success(f"🎉 ممتاز يا {student_name}! درجتك الفورية هي: {score}%")
                    else:
                        st.error(f"😞 للأسف يا {student_name} درجتك: {score}%. درجة النجاح من 50%.")
                    st.balloons()
