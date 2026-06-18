import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import re

# 🔗 [1] ضع رابط الجوجل شيت الخاص بك هنا
SHEET_URL = "https://docs.google.com/spreadsheets/d/11sa1GDAYCez4b17aI1hDPKJDtfj953ySj8OMYOxbzTI/edit?usp=sharing"

LESSONS_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=lessons")
QUIZZES_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=quizzes")

def clean_date_string(date_str):
    if not date_str or pd.isna(date_str) or str(date_str).lower() == 'nan':
        return None
    s = str(date_str).strip()
    # تنظيف الحروف العربية وتحويل الفواصل لشرطات بشكل سليم
    s = s.replace('م', '').replace('ص', '').replace('/', '-')
    s = re.sub(r'\s+', ' ', s).strip()
    
    # محاولة قراءة التاريخ بأكثر من صيغة مشهورة
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %I:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except: pass
    return None

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
            
            # قراءة وتنظيف أوقات البداية والنهاية
            start_val = row['start_at'] if 'start_at' in quizzes_df.columns else None
            end_val = row['end_at'] if 'end_at' in quizzes_df.columns else None
            
            # تنظيف وتجهيز حرف الإجابة الصحيحة
            raw_correct = str(row['correct_opt']).strip().upper()
            correct_letter = raw_correct[-1] if raw_correct.startswith('OPT') else raw_correct
            
            quizzes[q_title].append({
                "question": row['question_text'],
                "options": [row['optA'], row['optB'], row['optC'], row['optD']],
                "correct": correct_letter,
                "start_at": start_val,
                "end_at": end_val
            })
    except: quizzes = {}
    return courses, quizzes

st.set_page_config(page_title="منصتي التعليمية", layout="wide")
courses_db, quizzes_db = load_data()

st.header("🎓 بوابة الطالب التعليمية")
if "current_view" not in st.session_state: st.session_state.current_view = "sharh"

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

elif st.session_state.current_view == "quiz":
    st.subheader("📝 قسم الامتحانات والتقييمات الذكية")
    if not quizzes_db:
        st.info("👋 لا توجد امتحانات مرفوعة في الشيت حالياً...")
    else:
        chosen_quiz = st.selectbox("اختر الامتحان المطلوب للدخول:", list(quizzes_db.keys()))
        
        # ⏰ جلب وقت مصر الحالي الحقيقي بالظبط
        cairo_tz = pytz.timezone('Africa/Cairo')
        now = datetime.now(cairo_tz).replace(tzinfo=None)
        
        first_q = quizzes_db[chosen_quiz][0]
        quiz_allowed = True
        error_msg = ""
        
        start_dt = clean_date_string(first_q["start_at"])
        end_dt = clean_date_string(first_q["end_at"])
        
        # المقارنة المضمونة بعد توحيد التوقيت المصري
        if start_dt and now < start_dt:
            quiz_allowed = False
            error_msg = f"⏳ عذراً، هذا الامتحان لم يبدأ بعد. ميعاد البدء المحدد بتوقيت مصر: {first_q['start_at']}"
            
        if end_dt and quiz_allowed and now > end_dt:
            quiz_allowed = False
            error_msg = f"🚫 عذراً، انتهى الوقت المحدد لحل هذا الامتحان. كان آخر ميعاد بتوقيت مصر: {first_q['end_at']}"

        if not quiz_allowed:
            st.error(error_msg)
        else:
            student_name = st.text_input("✍️ من فضلك أدخل اسمك الثلاثي لبدء الاختبار:")
            if not student_name:
                st.warning("⚠️ يجب كتابة اسمك أولاً لتتمكن من حل الامتحان ورصد النتيجة.")
            else:
                questions = quizzes_db[chosen_quiz]
                if f"start_{chosen_quiz}" not in st.session_state:
                    st.session_state[f"start_{chosen_quiz}"] = datetime.now(cairo_tz).strftime("%Y-%m-%d %H:%M:%S")
                    
                with st.form(key=f"quiz_form_{chosen_quiz}"):
                    st.markdown(f"### 📋 {chosen_quiz}")
                    st.info(f"👤 الطالب: {student_name} | 🕒 وقت الدخول: {st.session_state[f'start_{chosen_quiz}']}")
                    
                    student_answers = {}
                    for i, q in enumerate(questions):
                        st.write(f"**سؤال {i+1}: {q['question']}**")
                        options_letters = ["A", "B", "C", "D"]
                        student_answers[i] = st.radio(
                            "اختر الإجابة:", options_letters, 
                            format_func=lambda x: f"{x} - {q['options'][options_letters.index(x)]}" if pd.notna(q['options'][options_letters.index(x)]) else x,
                            key=f"q_{chosen_quiz}_{i}"
                        )
                    
                    if st.form_submit_button("📥 إرسال الإجابات وإنهاء الامتحان"):
                        submit_time = datetime.now(cairo_tz).strftime("%Y-%m-%d %H:%M:%S")
                        
                        correct_count = 0
                        for i, q in enumerate(questions):
                            if str(student_answers[i]).strip().upper() == str(q['correct']).strip().upper():
                                correct_count += 1
                                
                        score = int((correct_count / len(questions)) * 100)
                        
                        # 🔗 [2] ضع هنا رابط تطبيق الويب الخاص بك (الذي ينتهي بـ exec)
                        WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxB72pq4-UUV_N9NOUdZgaCqBYj6x3p2RcPXoY1CDPmCgvo_4yFMEdirZ_nK_c_S8fcPw/exec"
                        
                        payload = {
                            "student_name": student_name, "quiz_title": chosen_quiz, "score": score,
                            "start_time": st.session_state[f'start_{chosen_quiz}'], "submit_time": submit_time
                        }
                        try: requests.post(WEB_APP_URL, json=payload)
                        except: pass
                        
                        st.markdown("---")
                        if score >= 50: st.success(f"🎉 ممتاز يا {student_name}! درجتك: {score}%")
                        else: st.error(f"😞 للأسف يا {student_name} درجتك: {score}%.")
                        st.balloons()
