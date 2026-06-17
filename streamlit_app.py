import streamlit as st
import uuid

# --- 1. تهيئة قاعدة البيانات المؤقتة في الذاكرة ---
if "courses" not in st.session_state:
    st.session_state.courses = {}
if "quizzes" not in st.session_state:
    st.session_state.quizzes = {}
if "attempts" not in st.session_state:
    st.session_state.attempts = {}

st.set_page_config(page_title="منصتي التعليمية", layout="wide")

# --- 2. الهيدر الرئيسي للمنصة ---
st.title("🎓 منصة الشرح والامتحانات الذكية")
st.write("أهلاً بك في لوحة التحكم والمشاهدة")
st.markdown("---")

# --- 3. القائمة الجانبية للتنقل (Navigation) ---
choice = st.sidebar.radio("اختر الواجهة:", ["🖥️ واجهة الطالب (مشاهدة وامتحانات)", "⚙️ لوحة تحكم الأدمن (رفع المحتوى)"])

# =========================================================
# ⚙️ واجهة الأدمن (رفع الفيديوهات والامتحانات)
# =========================================================
if choice == "⚙️ لوحة تحكم الأدمن (رفع المحتوى)":
    st.header("🛠️ إدارة الكورسات والامتحانات")
    
    tab1, tab2 = st.tabs(["➕ إضافة كورس وفيديو", "📝 إضافة امتحان للدرس"])
    
    with tab1:
        st.subheader("إنشاء كورس جديد وإضافة درس")
        course_title = st.text_input("اسم الكورس / الدبلومة:")
        lesson_title = st.text_input("اسم الدرس:")
        video_url = st.text_input("رابط الفيديو المشفر (من Bunny.net):", placeholder="https://iframe.mediadelivery.net/embed/...")
        pdf_url = st.text_input("رابط ملف الـ PDF المرفق (إن وجد):")
        
        if st.button("حفظ ونشر الدرس"):
            if course_title and lesson_title and video_url:
                if course_title not in st.session_state.courses:
                    st.session_state.courses[course_title] = []
                
                # حفظ البيانات
                lesson_id = str(uuid.uuid4())
                st.session_state.courses[course_title].append({
                    "id": lesson_id,
                    "title": lesson_title,
                    "video": video_url,
                    "pdf": pdf_url
                })
                st.success(f"✅ تم إضافة درس '{lesson_title}' بنجاح في كورس '{course_title}'!")
            else:
                st.error("❌ من فضلك املأ البيانات الأساسية (اسم الكورس، الدرس، ورابط الفيديو)")

    with tab2:
        st.subheader("ربط امتحان بدرس معين")
        if not st.session_state.courses:
            st.warning("⚠️ يجب إضافة كورس ودرس أولاً قبل وضع امتحان.")
        else:
            all_lessons = {}
            for c_title, lessons in st.session_state.courses.items():
                for les in lessons:
                    all_lessons[f"{c_title} - {les['title']}"] = les['id']
            
            selected_lesson_label = st.selectbox("اختر الدرس المراد وضع امتحان له:", list(all_lessons.keys()))
            selected_lesson_id = all_lessons[selected_lesson_label]
            
            st.markdown("---")
            q_text = st.text_area("نص السؤال:")
            opt1 = st.text_input("الاختيار الأول (A):")
            opt2 = st.text_input("الاختيار الثاني (B):")
            opt3 = st.text_input("الاختيار الثالث (C):")
            opt4 = st.text_input("الاختيار الرابع (D):")
            correct_opt = st.selectbox("الإجابة الصحيحة هي:", ["A", "B", "C", "D"])
            
            if st.button("إضافة هذا السؤال للامتحان"):
                if q_text and opt1 and opt2:
                    if selected_lesson_id not in st.session_state.quizzes:
                        st.session_state.quizzes[selected_lesson_id] = []
                    
                    st.session_state.quizzes[selected_lesson_id].append({
                        "id": str(uuid.uuid4()),
                        "question": q_text,
                        "options": [opt1, opt2, opt3, opt4],
                        "correct": correct_opt
                    })
                    st.success("✅ تم إضافة السؤال بنجاح للامتحان!")
                else:
                    st.error("❌ تأكد من كتابة السؤال والاختيارات.")

# =========================================================
# 🖥️ واجهة الطالب (مشاهدة الفيديوهات وحل الامتحانات)
# =========================================================
elif choice == "🖥️ واجهة الطالب (مشاهدة وامتحانات)":
    st.header("📚 بوابة الطالب التعليمية")
    
    if not st.session_state.courses:
        st.info("👋 المنصة فارغة حالياً. يرجى الدخول للوحة التحكم بالأعلى وإضافة كورسات وفيديوهات لتظهر هنا للطلاب.")
    else:
        # اختيار الكورس والدرس
        chosen_course = st.selectbox("اختر الكورس المتاح لك:", list(st.session_state.courses.keys()))
        lessons_available = st.session_state.courses[chosen_course]
        
        lesson_names = [l['title'] for l in lessons_available]
        chosen_lesson_title = st.selectbox("اختر الدرس المراد شرحه:", lesson_names)
        
        # جلب بيانات الدرس المختار
        current_lesson = next(l for l in lessons_available if l['title'] == chosen_lesson_title)
        
        st.markdown(f"### 📺 فيديو الشرح: {current_lesson['title']}")
        
        # عرض الفيديو (يدعم روابط الأكواد وروابط يوتيوب و Bunny)
        if "iframe" in current_lesson['video']:
            st.components.v1.html(current_lesson['video'], height=450)
        else:
            st.video(current_lesson['video'])
            
        if current_lesson['pdf']:
            st.markdown(f"[📥 اضغط هنا لتحميل ملف الـ PDF الخاص بالدرس]({current_lesson['pdf']})")
            
        st.markdown("---")
        
        # قسم الامتحان التابع للدرس
        st.markdown("### 📝 الامتحان التقييمي للدرس")
        les_id = current_lesson['id']
        
        if les_id not in st.session_state.quizzes or len(st.session_state.quizzes[les_id]) == 0:
            st.info("📩 لا يوجد امتحان متاح لهذا الدرس حالياً.")
        else:
            questions = st.session_state.quizzes[les_id]
            student_answers = {}
            
            # عرض الأسئلة للطالب
            with st.form(key=f"quiz_form_{les_id}"):
                for i, q in enumerate(questions):
                    st.write(f"**سؤال {i+1}: {q['question']}**")
                    # راديو بتن للاختيار
                    student_answers[q['id']] = st.radio(
                        "اختر الإجابة الصحيحة:", 
                        ["A", "B", "C", "D"], 
                        format_func=lambda x: f"{x} - {q['options'][['A','B','C','D'].index(x)]}" if q['options'][['A','B','C','D'].index(x)] else x,
                        key=f"q_{q['id']}"
                    )
                    st.markdown(" ")
                
                submit_button = st.form_submit_with_value("إرسال الإجابات وإنهاء الامتحان")
                
                if submit_button:
                    correct_count = 0
                    total_q = len(questions)
                    
                    for q in questions:
                        if student_answers[q['id']] == q['correct']:
                            correct_count += 1
                    
                    score = int((correct_count / total_q) * 100)
                    
                    st.markdown("### 📊 نتيجتك الفورية:")
                    if score >= 50:
                        st.success(f"🎉 مبروك! لقد نجحت. درجتك هي: {score}%")
                    else:
                        st.error(f"😞 حظ أوفر المرة القادمة. درجتك هي: {score}%. درجة النجاح من 50%")
