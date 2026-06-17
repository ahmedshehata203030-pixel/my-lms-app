import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ==========================================
# 📝 ضع روابطك الخاصة هنا لتفعيل الربط بالكامل
# ==========================================
SHEET_URL = "ضع_رابط_ملف_جوجل_شيت_الخاص_بك_هنا"
WEB_APP_URL = "ضع_رابط_الـ_Web_App_الذي_نسخته_من_الـ_Apps_Script_هنا"

# تحويل الرابط لروابط تقرأ من الشيت مباشرة
LESSONS_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=lessons")
QUIZZES_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=quizzes")

# دالة جلب البيانات من الشيت
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

# تهيئة الصفحة الإعدادية للـ Web App
st.set_page_config(page_title="منصتي التعليمية", layout="wide")
courses_db, quizzes_db = load_data()

# --- قراءة الرابط السري للأدمن عبر الـ URL ---
query_params = st.query_params
if query_params.get("role") == "admin":
    st.sidebar.title("🎛️ لوحة الإدارة مفعّلة")
    choice = st.sidebar.radio("اختر الواجهة الحالية:", ["🖥️ واجهة الطالب", "⚙️ لوحة تحكم الأدمن"])
else:
    choice = "🖥️ واجهة الطالب"

# =========================================================
# ⚙️ لوحة الأدمن (المخفية)
# =========================================================
if choice == "⚙️ لوحة تحكم الأدمن":
    st.header("🛠️ لوحة تحكم الإدارة والتعديل")
    st.success("🔓 مرحباً بك يا هندسة. يمكنك التعديل والرفع الآن من الشيت.")
    st.markdown(f"🔗 [اضغط هنا لفتح وتعديل ملف الـ Google Sheet]({SHEET_URL})")

# =========================================================
# 🖥️ واجهة الطالب (الضبط الرياضي الموحد للمربعات)
# =========================================================
elif choice == "🖥️ واجهة الطالب":
    st.header("🎓 بوابة الطالب التعليمية")
    
    if "current_view" not in st.session_state:
        st.session_state.current_view = "sharh"
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🎨 الـ CSS الهندسي النهائي: تصفير المسافات والتحكم بالبكسل لتطابق وتساوي الصناديق 100% في منتصف الشاشة
    st.markdown("""
        <style>
        /* توسيط وتجميع المربعات في منتصف الصفحة وبمسافة قريبة */
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            justify-content: center !important;
            gap: 25px !important;
            max-width: 1000px !important;
            margin: 0 auto !important;
        }
        
        /* ضبط حجم الأعمدة ليكون متساوياً */
        div[data-testid="stColumn"] {
            flex: 1 !important;
            width: 100% !important;
            max-width: 450px !important;
        }
        
        /* إجبار الأزرار على التساوي التام في الطول والعرض */
        div.stButton > button {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            height: 110px !important; /* طول موحد للمربعين بالملي */
            font-size: 26px !important; /* حجم خط عريض وموحد */
            font-weight: bold !important;
            color: white !important;
            border-radius: 15px !important;
            border: none !important;
            box-shadow: 0px 6px 16px rgba(0,0,0,0.15) !important;
            transition: all 0.25s ease !important;
            white-space: nowrap !important;
        }
        
        /* تخصيص المربع الأول (الشرح): أزرق كحلي */
        div[data-testid="stHorizontalBlock"] > div:nth-of-type(1) div.stButton > button {
            background-color: #1A365D !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-of-type(1) div.stButton > button:hover {
            background-color: #0F172A !important;
            transform: translateY(-3px) !important;
        }
        
        /* تخصيص المربع الثاني (الامتحانات): أخضر داكن ومساوي للمربع الأول تماماً */
        div[data-testid="stHorizontalBlock"] > div:nth-of-type(2) div.stButton > button {
            background-color: #064E3B !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-of-type(2) div.stButton > button:hover {
            background-color: #022C22 !important;
            transform: translateY(-3px) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 🧱 بناء المربعين المتساويين والمتقاربين تماماً جنب بعض
    box_sharh, box_quiz = st.columns(2)
    
    with box_sharh:
        if st.button("📺 الشرح والدروس", key="btn_sharh_final_prod"):
            st.session_state.current_view = "sharh"
            
    with box_quiz:
        if st.button("📝 الامتحانات والاختبارات", key="btn_quiz_final_prod"):
            st.session_state.current_view = "quiz"
            
    st.markdown("---")

    # 🟢 قسم الشرح
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

    # 🔴 قسم الامتحانات (مربوط بقراءة الامتحان
