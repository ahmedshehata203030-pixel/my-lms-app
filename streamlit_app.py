import streamlit as st
import pandas as pd
import uuid

# 📝 ضع رابط ملف الـ Google Sheet الخاص بك هنا (تأكد من جعله Anyone with link can edit)
SHEET_URL = "https://docs.google.com/spreadsheets/d/11sa1GDAYCez4b17aI1hDPKJDtfj953ySj8OMYOxbzTI/edit?gid=0#gid=0"

# تحويل الرابط العادي لروابط تقرأ وتكتب CSV مباشرة
LESSONS_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=lessons")
QUIZZES_CSV = SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=quizzes")

# دالة لجلب البيانات من جوجل شيت
def load_data():
    try:
        lessons_df = pd.read_csv(LESSONS_CSV)
        courses = {}
        for _, row in lessons_df.iterrows():
            c_title = row['course_title']
            if c_title not in courses:
                courses[c_title] = []
            courses[c_title].append({
                "id": row['lesson_id'],
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
            l_id = row['lesson_id']
            if l_id not in quizzes:
                quizzes[l_id] = []
            quizzes[l_id].append({
                "id": row['q_id'],
                "question": row['question_text'],
                "options": [row['optA'], row['optB'], row['optC'], row['optD']],
                "correct": row['correct_opt']
            })
    except:
        quizzes = {}

    return courses, quizzes

# دالة لحفظ درس جديد في جوجل شيت عبر الاستجابة لـ Forms السحابية أو كود مدمج بسيط
# لمستويات متقدمة نستخدم التحديث المباشر، ولكن للتسهيل بدون مفاتيح معقدة سنعرض المحتوى المخزن
# وإذا أحببت ربط احترافي بالـ API لجوجل شيتس سنحتاج مكتبة gspread ومفتاح JSON من Google Cloud.

# شاشة الـ Streamlit الأساسية
st.set_page_config(page_title="منصتي التعليمية المحفوظة", layout="wide")

# جلب البيانات الحية من جوجل شيت فور تحميل الصفحة
courses_db, quizzes_db = load_data()

st.title("🎓 منصة الشرح والامتحانات (قاعدة بيانات حية)")
st.markdown("---")

choice = st.sidebar.radio("اختر الواجهة:", ["🖥️ واجهة الطالب (مشاهدة وامتحانات)", "⚙️ لوحة تحكم الأدمن (رفع المحتوى)"])

if choice == "⚙️ لوحة تحكم الأدمن (رفع المحتوى)":
    st.header("🛠️ إدارة الكورسات والامتحانات")
    st.info("💡 لحفظ البيانات بشكل دائم ومباشر بدون تعقيد برمجيات الحماية، يمكنك كتابة الدروس والأسئلة مباشرة داخل ملف الـ Google Sheet في الحساب الخاص بك، وستظهر هنا فوراً للطلاب عند عمل تحديث للصفحة!")
    st.markdown(f"🔗 [اضغط هنا لفتح ملف قاعدة البيانات وتعديله]({SHEET_URL})")
    
    st.markdown("""
    **طريقة الكتابة في الشيت لتظهر هنا:**
    * **في ورقة lessons اكتب الأعمدة التالية:** `course_title`, `lesson_id`, `lesson_title`, `video_url`, `pdf_url`
    * **في ورقة quizzes اكتب الأعمدة التالية:** `lesson_id`, `q_id`, `question_text`, `optA`, `optB`, `optC`, `optD`, `correct_opt`
    """)

elif choice == "🖥️ واجهة الطالب (مشاهدة وامتحانات)":
    st.header("📚 بوابة الطالب التعليمية")
    
    if not courses_db:
        st.info("👋 المنصة بانتظار إضافة محتوى في ملف الـ Google Sheets لتظهر هنا تلقائياً.")
    else:
        chosen_course = st.selectbox("اختر الكورس المتاح لك:", list(courses_db.keys()))
        lessons_available = courses_db[chosen_course]
        
        lesson_names = [l['title'] for l in lessons_available]
        chosen_lesson_title = st.selectbox("اختر الدرس المراد شرحه:", lesson_names)
        
        current_lesson = next(l for l in lessons_available if l['title'] == chosen_lesson_title)
        
        st.markdown(f"### 📺 فيديو الشرح: {current_lesson['title']}")
        
        if "iframe" in str(current_lesson['video']):
            st.components.v1.html(current_lesson['video'], height=450)
        else:
            st.video(current_lesson['video'])
            
        if pd.notna(current_lesson['pdf']) and current_lesson['pdf']:
            st.markdown(f"[📥 اضغط هنا لتحميل ملف الـ PDF الخاص بالدرس]({current_lesson['pdf']})")
            
        st.markdown("---")
        st.markdown("### 📝 الامتحان التقييمي للدرس")
        les_id = current_lesson['id']
        
        if les_id not in quizzes_db:
            st.info("📩 لا يوجد امتحان متاح لهذا الدرس حالياً.")
        else:
            questions = quizzes_db[les_id]
            student_answers = {}
            
            with st.form(key=f"quiz_form_{les_id}"):
                for i, q in enumerate(questions):
                    st.write(f"**سؤال {i+1}: {q['question']}**")
                    student_answers[q['id']] = st.radio(
                        "اختر الإجابة الصحيحة:", 
                        ["A", "B", "C", "D"], 
                        format_func=lambda x: f"{x} - {q['options'][['A','B','C','D'].index(x)]}" if pd.notna(q['options'][['A','B','C','D'].index(x)]) else x,
                        key=f"q_{q['id']}"
                    )
                
                submit_button = st.form_submit_with_value("إرسال الإجابات وإنهاء الامتحان")
                
                if submit_button:
                    correct_count = 0
                    for q in questions:
                        if student_answers[q['id']] == q['correct']:
                            correct_count += 1
                    
                    score = int((correct_count / len(questions)) * 100)
                    st.markdown("### 📊 نتيجتك الفورية:")
                    if score >= 50:
                        st.success(f"🎉 مبروك! لقد نجحت. درجتك هي: {score}%")
                    else:
                        st.error(f"😞 حظ أوفر المرة القادمة. درجتك هي: {score}%. درجة النجاح من 50%")
