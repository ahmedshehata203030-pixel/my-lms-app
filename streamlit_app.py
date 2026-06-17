import streamlit as st
import pandas as pd

# 📝 ضع رابط ملف الـ Google Sheet الخاص بك هنا 
SHEET_URL = "https://docs.google.com/spreadsheets/d/11sa1GDAYCez4b17aI1hDPKJDtfj953ySj8OMYOxbzTI/edit?usp=sharing"

# تحويل الرابط لروابط تقرأ من الشيت مباشرة
LESSONS_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=lessons")
QUIZZES_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=quizzes")

# دالة جلب البيانات
def load_data():
    # جلب الدروس
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

    # جلب الامتحانات المستقلة
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
# ⚙️ لوحة الأدمن (تظهر لك عند الدخول بالرابط السري)
# =========================================================
if choice == "⚙️ لوحة تحكم الأدمن":
    st.header("🛠️ لوحة تحكم الإدارة والتعديل")
    st.success("🔓 مرحباً بك يا هندسة. يمكنك التعديل والرفع الآن من الشيت.")
    st.markdown(f"🔗 [اضغط هنا لفتح وتعديل ملف الـ Google Sheet]({SHEET_URL})")
    
    st.markdown("""
    ### 📂 طريقة تنظيم البيانات في الشيت الجديد:
    
    **1. في ورقة `lessons` (خاص بالشرح):**
    اكتب العناوين التالية في الصف الأول:
    `course_title` | `lesson_title` | `video_url` | `pdf_url`
    *(مثال: اكتب اسم الكورس، اسم الدرس، ورابط الفيديو، وسيظهر في خانة الشرح).*
    
    **2. في ورقة `quizzes` (خاص بالامتحانات المستقلة):**
    اكتب العناوين التالية في الصف الأول:
    `quiz_title` | `question_text` | `optA` | `optB` | `optC` | `optD` | `correct_opt`
    *(مثال: اكتب في خانة quiz_title اسم الامتحان مثل "امتحان الشهر الأول" أو "مراجعة شاملة"، وحط أسئلتك براحتك).*
    """)

# =========================================================
# 🖥️ واجهة الطالب (مربعين كبار: خانة للشرح وخانة للامتحانات)
# =========================================================
elif choice == "🖥️ واجهة الطالب":
    st.header("🎓 بوابة الطالب التعليمية")
    
    # تهيئة الحالة الافتراضية للزرار
    if "current_view" not in st.session_state:
        st.session_state.current_view = "sharh"
        
    # 🧱 تصميم المربعين الكبار في رأس الصفحة 🧱
    box_sharh, box_quiz = st.columns(2)
    
    with box_sharh:
        st.markdown("""
            <div style="background-color:#1E3A8A; padding:15px; border-radius:10px; text-align:center; color:white;">
                <h3 style="color:white; margin:0;">📺 الشرح والدروس</h3>
            </div>
        """, unsafe_allow_html=True)
        if st.button("👇 دخول قسم الشرح والفيديوهات", use_container_width=True, type="primary"):
            st.session_state.current_view = "sharh"
            
    with box_quiz:
        st.markdown("""
            <div style="background-color:#065F46; padding:15px; border-radius:10px; text-align:center; color:white;">
                <h3 style="color:white; margin:0;">📝 الامتحانات والاختبارات</h3>
            </div>
        """, unsafe_allow_html=True)
        if st.button("👇 دخول قسم الامتحانات الحرة", use_container_width=True, type="primary"):
            st.session_state.current_view = "quiz"
            
    st.markdown("---")

    # 🟢 عرض محتوى "خانة الشرح"
    if st.session_state.current_view == "sharh":
        st.subheader("📺 قسم المحاضرات وفيديوهات الشرح")
        if not courses_db:
            st.info("👋 جاري رفع الفيديوهات والدروس حالياً...")
        else:
            chosen_course = st.selectbox("اختر الوحدة:", list(courses_db.keys()))
            lessons_available = courses_db[chosen_course]
            lesson_names = [l['title'] for l in lessons_available]
            chosen_lesson = st.selectbox("اختر الدرس المراد مشاهدته:", lesson_names)
            
            current_lesson = next(l for l in lessons_available if l['title'] == chosen_lesson)
            
            # عرض الفيديو والـ PDF
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
            st.info("👋 لا توجد امتحانات مرفوعة حالياً في هذا القسم...")
        else:
            # الطالب يختار اسم الامتحان مباشرة (اللي أنت بتكتبه في عمود quiz_title)
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
                        st.error(f"😞 درجتك: {score}%. درجة النجاح من 50%، يمكنك المحاولة مجدداً بعد المذاكرة.")
