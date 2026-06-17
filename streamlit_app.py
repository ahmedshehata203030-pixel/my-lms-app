import streamlit as st
import pandas as pd

# 📝 ضع رابط ملف الـ Google Sheet الخاص بك هنا 
SHEET_URL = "https://docs.google.com/spreadsheets/d/11sa1GDAYCez4b17aI1hDPKJDtfj953ySj8OMYOxbzTI/edit?usp=sharing"

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
# 🖥️ واجهة الطالب (حل مشكلة التباعد المقاسات نهائياً)
# =========================================================
elif choice == "🖥️ واجهة الطالب":
    st.header("🎓 بوابة الطالب التعليمية")
    
    if "current_view" not in st.session_state:
        st.session_state.current_view = "sharh"
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🎨 الـ CSS القاتل للمسافات: بيقرب الأزرار لبعضها جداً ويخليها عريضة وطويلة بنفس الحجم بالملي
    st.markdown("""
        <style>
        /* إلغاء الفراغات الكبيرة بين الأعمدة وجعلهم متقاربين في منتصف الشاشة */
        [data-testid="stHorizontalBlock"] {
            gap: 20px !important;
            max-width: 900px !important; /* يلم المربعين لبعض في نص الشاشة تماماً */
            margin: 0 auto !important;   /* توسيط البلوك بالكامل */
        }
        
        /* إجبار الأزرار على أخذ حجم موحد وعريض وطويل */
        div.stButton > button {
            display: block !important;
            width: 100% !important;
            min-height: 100px !important; /* طول مثالي وموحد */
            padding: 20px !important;
            font-size: 26px !important;   /* تكبير الخط */
            font-weight: bold !important;
            color: white !important;
            border-radius: 15px !important;
            border: none !important;
            box-shadow: 0px 5px 15px rgba(0,0,0,0.15) !important;
            transition: all 0.25s ease !important;
            cursor: pointer !important;
        }
        
        /* زر الشرح: أزرق كحلي */
        div[data-testid="stHorizontalBlock"] > div:nth-of-type(1) div.stButton > button {
            background-color: #1A365D !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-of-type(1) div.stButton > button:hover {
            background-color: #0F172A !important;
            transform: translateY(-2px) !important;
        }
        
        /* زر الامتحانات: أخضر غامق */
        div[data-testid="stHorizontalBlock"] > div:nth-of-type(2) div.stButton > button {
            background-color: #064E3B !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-of-type(2) div.stButton > button:hover {
            background-color: #022C22 !important;
            transform: translateY(-2px) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 🧱 بناء المربعين جنب بعض (ملمومين في نص الشاشة وبعاد عن الأطراف)
    box_sharh, box_quiz = st.columns(2)
    
    with box_sharh:
        if st.button("📺 الشرح والدروس", key="btn_sharh_v4"):
            st.session_state.current_view = "sharh"
            
    with box_quiz:
        if st.button("📝 الامتحانات والاختبارات", key="btn_quiz_v4"):
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

    # 🔴 قسم الامتحانات
    elif st.session_state.current_view == "quiz":
        st.subheader("📝 قسم الامتحانات والتقييمات المستقلة")
        if not quizzes_db:
            st.info("👋 لا توجد امتحانات مرفوعة حالياً في هذا القسم...")
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
