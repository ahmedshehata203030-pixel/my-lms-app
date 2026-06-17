import streamlit as st
import pandas as pd

# 📝 ضع رابط ملف الـ Google Sheet الخاص بك هنا 
SHEET_URL = "ضع_رابط_ملف_جوجل_شيت_الخاص_بك_هنا"

# تحويل الرابط لروابط تقرأ من الشيت مباشرة
LESSONS_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=lessons")
QUIZZES_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=quizzes")

# دالة جلب البيانات
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

# --- قراءة الرابط السري للأدمن ---
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
# 🖥️ واجهة الطالب (تصميم الصناديق التفاعلية كأزرار مباشرة)
# =========================================================
elif choice == "🖥️ واجهة الطالب":
    st.header("🎓 بوابة الطالب التعليمية")
    
    # تهيئة الحالة الافتراضية
    if "current_view" not in st.session_state:
        st.session_state.current_view = "sharh"
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🧱 إنشاء المربعات الكبيرة كأزرار مباشرة بدون إضافات حمراء 🧱
    box_sharh, box_quiz = st.columns(2)
    
    with box_sharh:
        # زر مخصص يأخذ شكل وتصميم الصندوق بالكامل
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #1E3A8A !important;
                color: white !important;
                font-size: 24px !important;
                font-weight: bold !important;
                padding: 30px !important;
                border-radius: 12px !important;
                border: none !important;
                width: 100% !important;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.1) !important;
                transition: 0.3s !important;
            }
            div.stButton > button:first-child:hover {
                background-color: #172554 !important;
                transform: scale(1.02) !important;
            }
            </style>
        """, unsafe_allow_html=True)
        if st.button("📺 الشرح والدروس", key="btn_sharh_main"):
            st.session_state.current_view = "sharh"
            
    with box_quiz:
        # زر مخصص للقسم الثاني بنفس الطريقة والألوان الخاصة به
        # نستخدم كمبرمجين معرفة فريدة عبر المكونات لتخصيص كل زر بشكل مستقل
        if st.button("📝 الامتحانات والاختبارات", key="btn_quiz_main"):
            st.session_state.current_view = "quiz"
            
        # كود CSS لتلوين الزر الثاني بالأخضر بشكل منفصل
        st.markdown("""
            <style>
            div:nth-child(2) > div.stButton > button:first-child {
                background-color: #065F46 !important;
            }
            div:nth-child(2) > div.stButton > button:first-child:hover {
                background-color: #022C22 !important;
            }
            </style>
        """, unsafe_allow_html=True)
            
    st.markdown("---")

    # 🟢 عرض محتوى "خانة الشرح"
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

    # 🔴 عرض محتوى "خانة الامتحانات" 
    elif st.session_state.current_view == "quiz":
        st.subheader("📝 قسم الامتحانات والتقييمات المستقلة")
        if not quizzes_db:
            st.info("👋 لا توجد امتحانات مرفوعة حالياً في هذا قسم...")
        else:
            chosen_quiz = st.selectbox("اختر الامتحان المتاح للدخول:", list(quizzes_db.keys()))
            questions = quizzes_db[chosen_quiz]
            student_answers = {}
            
            with st.form(key=f"independent_quiz_{chosen_quiz}"):
                for i, q in enumerate(questions):
                    st.write(f"**سؤال {i+1}: {q['question']}**")
                    student_answers[i] = st.radio(
                        "اختر الإجابة:", 
                        ["A", "B", "C", "D"], 
                        format_func=lambda x: f"{x} - {q['options'][['A','B','C','D'].index(x)]}" if pd.notna(q['options'][['A','B','C','D'].index(x)]) else x,
                        key=f"q_{chosen_quiz}_{i}"
                    )
                    st.markdown(" ")
                
                submit_button = st.form_submit_with_value("إرسال الإجابات ومعرفة النتيجة")
                
                if submit_button:
                    correct_count = 0
                    for i, q in enumerate(questions):
                        if student_answers[i] == q['correct']:
                            correct_count += 1
                    
                    score = int((correct_count / len(questions)) * 100)
                    st.markdown("### 📊 نتيجتك الفورية في هذا الامتحان:")
                    if score >= 50:
                        st.success(f"🎉 ممتاز! لقد اجتزت الامتحان بنجاح. درجتك: {score}%")
                    else:
                        st.error(f"😞 درجتك: {score}%. درجة النجاح من 50%")
