import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json

# ==========================================
# 📝 ضع روابطك وإعدادات الشيت هنا
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/11sa1GDAYCez4b17aI1hDPKJDtfj953ySj8OMYOxbzTI/edit?usp=sharing"

# تحويل الروابط للقراءة المباشرة للأسئلة والدروس
LESSONS_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=lessons")
QUIZZES_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=quizzes")

# دالة الاتصال المباشر بالجوجل شيت للكتابة (بدون سكريبت)
def get_google_sheet():
    try:
        # قراءة مفتاح الأمان من إعدادات جيت هاب السرية
        creds_dict = json.loads(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        # فتح الشيت والوصول لصفحة النتائج
        sheet = client.open_by_url(SHEET_URL).worksheet("student_results")
        return sheet
    except Exception as e:
        return None

# دالة جلب البيانات (الدروس والأسئلة)
def load_data():
    try:
        lessons_df = pd.read_csv(LESSONS_CSV)
        courses = {}
        for _, row in lessons_df.iterrows():
            c_title = row['course_title']
            if c_title not in courses:
                courses[c_title] = []
            courses[c_title].append({
                "title": row['lesson_title'],
                "video": row['video_url'],
                "pdf": row['pdf_url']
            })
    except:
        courses = {}

    try:
        quizzes_df = pd.read_csv(QUIZZES_CSV)
        quizzes = {}
        for _, row in quizzes_df.iterrows():
            q_title = row['quiz_title']
            if q_title not in quizzes:
                quizzes[q_title] = []
            quizzes[q_title].append({
                "question": row['question_text'],
                "options": [row['optA'], row['optB'], row['optC'], row['optD']],
                "correct": row['correct_opt']
            })
    except:
        quizzes = {}

    return courses, quizzes

# تهيئة الصفحة
st.set_page_config(page_title="منصتي التعليمية", layout="wide")
courses_db, quizzes_db = load_data()

# التحكم في واجهة الأدمن عبر الرابط
query_params = st.query_params
if query_params.get("role") == "admin":
    st.sidebar.title("🎛️ لوحة الإدارة مفعّلة")
    choice = st.sidebar.radio("اختر الواجهة الحالية:", ["🖥️ واجهة الطالب", "⚙️ لوحة تحكم الأدمن"])
else:
    choice = "🖥️ واجهة الطالب"

if choice == "⚙️ لوحة تحكم الأدمن":
    st.header("🛠️ لوحة تحكم الإدارة والتعديل")
    st.success("🔓 مرحباً بك يا هندسة. يمكنك التعديل الآن في الشيت مباشرة.")
    st.markdown(f"🔗 [اضغط هنا لفتح وتعديل ملف الـ Google Sheet]({SHEET_URL})")

elif choice == "🖥️ واجهة الطالب":
    st.header("🎓 بوابة الطالب التعليمية")
    
    if "current_view" not in st.session_state:
        st.session_state.current_view = "sharh"
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🎨 تصميم المربعات المتساوية في منتصف الشاشة
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            justify-content: center !important;
            gap: 25px !important;
            max-width: 1000px !important;
            margin: 0 auto !important;
        }
        div[data-testid="stColumn"] {
            flex: 1 !important;
            width: 100% !important;
            max-width: 450px !important;
        }
        div.stButton > button {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            height: 110px !important;
            font-size: 26px !important;
            font-weight: bold !important;
            color: white !important;
            border-radius: 15px !important;
            border: none !important;
            box-shadow: 0px 6px 16px rgba(0,0,0,0.15) !important;
            transition: all 0.25s ease !important;
        }
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
        if not courses_db:
            st.info("👋 جاري رفع الفيديوهات والدروس حالياً...")
        else:
            chosen_course = st.selectbox("اختر الكورس / الدبلومة:", list(courses_db.keys()))
            lessons_available = courses_db[chosen_course]
            lesson_names = [l['title'] for l in lessons_available]
            chosen_lesson = st.selectbox("اختر الدرس المراد مشاهدته:", lesson_names)
            
            current_lesson = next(l for l in lessons_available if l['title'] == chosen_lesson)
            if "iframe" in str(current_lesson['video']):
                st.components.v1.html(current_lesson['video'], height=450)
            else:
                st.video(current_lesson['video'])
            if pd.notna(current_lesson['pdf']) and current_lesson['pdf']:
                st.markdown(f"[📥 تحميل ملف الـ PDF المرفق للدرس]({current_lesson['pdf']})")

    elif st.session_state.current_view == "quiz":
        st.subheader("📝 قسم الامتحانات والتقييمات الذكية")
        
        if not quizzes_db:
            st.info("👋 لا توجد امتحانات مرفوعة في الشيت حالياً...")
        else:
            student_name = st.text_input("✍️ من فضلك أدخل اسمك الثلاثي لبدء الاختبار:")
            
            if not student_name:
                st.warning("⚠️ يجب كتابة اسمك أولاً لتتمكن من حل الامتحان ورصد النتيجة باسمك.")
            else:
                chosen_quiz = st.selectbox("اختر الامتحان المطلوب للدخول:", list(quizzes_db.keys()))
                
                if f"start_prod_{chosen_quiz}" not in st.session_state:
                    st.session_state[f"start_prod_{chosen_quiz}"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                questions = quizzes_db[chosen_quiz]
                student_answers = {}
                
                with st.form(key=f"direct_sheet_form_{chosen_quiz}"):
                    st.markdown(f"### 📋 {chosen_quiz}")
                    st.info(f"👤 الطالب: {student_name} | 🕒 وقت الدخول: {st.session_state[f'start_prod_{chosen_quiz}']}")
                    
                    for i, q in enumerate(questions):
                        st.write(f"**سؤال {i+1}: {q['question']}**")
                        student_answers[i] = st.radio(
                            "اختر الإجابة:", ["A", "B", "C", "D"],
                            format_func=lambda x: f"{x} - {q['options'][['A','B','C','D'].index(x)]}" if pd.notna(q['options'][['A','B','C','D'].index(x)]) else x,
                            key=f"q_{chosen_quiz}_{i}"
                        )
                    
                    submit_button = st.form_submit_with_value("📥 إرسال الإجابات وإنهاء الامتحان")
                    
                    if submit_button:
                        submit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        correct_count = sum(1 for i, q in enumerate(questions) if student_answers[i] == q['correct'])
                        score = int((correct_count / len(questions)) * 100)
                        
                        # 🚀 الكتابة المباشرة في الشيت بدون سيرفر وسيط
                        sheet = get_google_sheet()
                        if sheet is not None:
                            try:
                                sheet.append_row([student_name, chosen_quiz, f"{score}%", st.session_state[f'start_prod_{chosen_quiz}'], submit_time])
                                st.toast("✅ تم تسجيل نتيجتك في شيت الإكسيل بنجاح موثق!")
                            except:
                                st.toast("⚠️ فشل الكتابة؛ تحقق من إعدادات الحساب السرية.")
                        else:
                            st.toast("⚙️ خطأ في الاتصال المباشر بجوجل شيت.")
                        
                        st.markdown("---")
                        if score >= 50:
                            st.success(f"🎉 ممتاز يا {student_name}! درجتك: {score}%")
                        else:
                            st.error(f"😞 درجتك: {score}%. بالتوفيق المرة القادمة.")
                        st.balloons()
