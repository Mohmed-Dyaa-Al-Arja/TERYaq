"""
Minimal i18n helper.

Every piece of UI text in the app should be a key here (in BOTH languages)
and be rendered through t(key) — never hard-coded English inside a page.
Keep keys lowercase_with_underscores so they read the same in both languages.
"""

import streamlit as st

TRANSLATIONS = {
    "en": {
        # Navbar
        "nav_home": "Home",
        "nav_detect": "Detect",
        "nav_chat": "AI Chat",
        "nav_features": "Features",
        "nav_developers": "Developers",
        "nav_about": "About",
        "nav_history": "History",
        "brand_name": "Vehicle Vision",
        "brand_suffix": "AI",
        "login": "Login",
        "login_notice": "Login UI is ready. Connect it to your authentication API when the backend is available.",
        "secure_title": "100% Secure",
        "secure_desc": "Your data is encrypted and protected",
        "support_title": "24/7 Support",
        "support_desc": "We are here to help you anytime",
        "login_notice": "Login is ready for the authentication backend.",
        "theme_light": "Light",
        "theme_dark": "Dark",

        # Home
        "hero_badge": "AI-Powered",
        "hero_title_1": "Vehicle Recognition",
        "hero_title_2": "Made Simple",
        "hero_subtitle": "Upload an image of any vehicle and our AI model will detect the make, model and year instantly with high accuracy.",
        "start_detection": "Start Detection",
        "learn_more": "Learn More",
        "how_it_works": "How it works",
        "feat_detect_title": "Vehicle Detection",
        "feat_detect_desc": "Detect vehicles in images with high accuracy.",
        "feat_process_title": "AI Processing",
        "feat_process_desc": "Our AI analyzes the image in seconds.",
        "feat_extract_title": "Extract Features",
        "feat_extract_desc": "Brand, model and year are extracted.",
        "feat_results_title": "Smart Results",
        "feat_results_desc": "Results are displayed instantly.",
        "stat_accuracy": "Accuracy Rate",
        "stat_images": "Images Processed",
        "stat_ai_powered": "AI-Powered",
        "stat_support": "Support",

        # Detect
        "detect_title": "Detect Vehicle",
        "detect_subtitle": "Upload a clear image of the vehicle you want to detect",
        "upload_title": "Drag & drop your image here",
        "upload_subtitle": "or click to browse",
        "browse_files": "Browse Files",
        "upload_label": "Upload",
        "upload_legend_formats": "Supported formats: JPG, PNG, WEBP",
        "upload_legend_max_size": "Max size: 10MB",
        "secure_title": "Your image is secure and private.",
        "secure_desc": "We do not store or share your images.",
        "tips_title": "Tips for best results",
        "tip_1": "Use clear, high-quality images",
        "tip_2": "Ensure the vehicle is fully visible",
        "tip_3": "Good lighting improves accuracy",
        "tip_4": "Avoid blurry or dark images",
        "please_upload_first": "Please upload an image first.",

        # Loading
        "loading_title": "Analyzing Your Vehicle",
        "loading_subtitle": "Please wait while our AI processes the image",
        "step_upload": "Uploading image",
        "step_preprocess": "Preprocessing image",
        "step_extract": "Extracting features",
        "step_vector_db": "Searching vector database (FAISS)",
        "step_kb": "Querying knowledge base (MongoDB)",
        "step_prices": "Checking latest market prices",
        "step_generate": "Generating AI answer",
        "step_finalize": "Finalizing results",
        "backend_unavailable": "Backend unavailable, showing demo data.",
        "no_pending_image": "No image found to analyze. Please start from the Detect page.",
        "back_to_detect": "Back to Detect",

        # Result
        "result_title": "Detection Result",
        "no_result_yet": "No detection result yet.",
        "spec_make": "Make",
        "spec_model": "Model",
        "spec_body_type": "Body Type",
        "spec_color": "Color",
        "ask_ai": "Ask AI Assistant",
        "download_report": "Download Report",
        "analyze_another": "Analyze Another Image",

        # Chat
        "chat_title": "AI Assistant",
        "chat_about_title": "About AI Assistant",
        "chat_about_desc": "Ask me anything about vehicles: specifications, features, comparisons, prices and more.",
        "chat_detected_vehicle": "Detected Vehicle",
        "chat_confidence": "Confidence",
        "chat_suggested": "Suggested Questions",
        "chat_placeholder": "Type your question here...",
        "chat_hello": "Hello! Ask me about any vehicle — specifications, features, comparisons, prices and more.",
        "chat_demo_notice": "(Demo mode — backend unavailable)",
        "sugg_fuel": "Fuel consumption",
        "sugg_hp": "Horsepower",
        "sugg_maintenance": "Maintenance tips",
        "sugg_reliability": "Reliability",
        "sugg_price": "Price",
        "sugg_alternatives": "Alternatives",

        # Features
        "features_title": "Powerful Features",
        "features_subtitle": "Everything you need for accurate vehicle recognition and intelligent analysis",
        "f_detect_t": "AI Vehicle Detection",
        "f_detect_d": "Advanced computer vision model to detect vehicles in images with high accuracy.",
        "f_instant_t": "Instant Recognition",
        "f_instant_d": "Identify make, model and year in seconds with our powerful AI.",
        "f_specs_t": "Detailed Specifications",
        "f_specs_d": "Get comprehensive specs, features, performance and more.",
        "f_assistant_t": "AI Assistant",
        "f_assistant_d": "Ask anything about the detected vehicle and get intelligent answers.",
        "f_market_t": "Market Information",
        "f_market_d": "Current market prices, trends and value estimation.",
        "f_sources_t": "Multiple Sources",
        "f_sources_d": "Information aggregated from reliable automotive sources.",
        "f_export_t": "Export Reports",
        "f_export_d": "Download detailed reports in PDF format.",
        "f_secure_t": "Secure & Private",
        "f_secure_d": "Your data is encrypted and your privacy is our priority.",

        # Developers
        "developers_title": "Our Developers",
        "developers_subtitle": "Meet the team behind Vehicle Vision AI",
        "view_profile": "View Profile",
        "view_team_photo": "View Team Photo",
        "team_tagline_title": "We build intelligent solutions",
        "team_tagline_desc": "Together we are building the future of vehicle recognition with AI",

        # Developer profile
        "profile_title": "Developer Profile",
        "profile_back": "Back to Developers",
        "profile_contact": "Contact",
        "profile_skills": "Skills",
        "profile_phone": "Phone",
        "profile_email": "Email",
        "profile_github": "GitHub",
        "profile_linkedin": "LinkedIn",
        "profile_not_found": "Developer not found.",

        # Team photo
        "team_photo_title": "Team Photo",
        "team_photo_subtitle": "The people building Vehicle Vision AI",
        "team_photo_caption": "Vehicle Vision AI team",

        # About
        "about_badge": "About Us",
        "about_title": "About Vehicle Vision AI",
        "about_desc": "Vehicle Vision AI is an intelligent vehicle recognition platform that uses advanced AI and computer vision to identify vehicles from images with high accuracy and provide detailed information about them.",
        "about_mission_title": "Our Mission",
        "about_mission_desc": "Make vehicle information accessible to everyone through AI technology.",
        "about_vision_title": "Our Vision",
        "about_vision_desc": "Be the leading AI-powered vehicle recognition platform worldwide.",
        "stat_founded": "Founded",
        "stat_users": "Happy Users",
        "stat_analyzed": "Images Analyzed",
        "tech_stack_title": "Technology Stack",

        # History
        "history_title": "Detection History",
        "history_subtitle": "Browse and revisit your previously detected vehicles",
        "history_search": "Search history",
        "history_empty": "No detections yet. Try detecting a vehicle first.",
        "history_view": "View Result",
        "history_report": "Report",
        "history_delete": "Delete",
        "history_deleted": "Detection removed.",

        # PDF Report
        "report_title": "PDF Report",
        "report_subtitle": "Download a shareable PDF summary of this detection",
        "report_no_detection": "No detection selected. Detect a vehicle first to generate a report.",
        "report_preview_title": "Report Preview",
        "report_generate": "Generate & Download PDF",
        "report_generating": "Generating report...",
        "report_ready": "Your report is ready.",
        "report_demo_notice": "Backend unavailable — showing a demo report.",
        "report_field_id": "Detection ID",
        "report_field_date": "Date",
        "report_field_vehicle": "Vehicle",
        "report_field_confidence": "Confidence",
    },
    "ar": {
        # Navbar
        "nav_home": "الرئيسية",
        "nav_detect": "الكشف",
        "nav_chat": "المحادثة الذكية",
        "nav_features": "المميزات",
        "nav_developers": "المطورون",
        "nav_about": "عن المشروع",
        "nav_history": "السجل",
        "brand_name": "فيهيكل فيجن",
        "brand_suffix": "AI",
        "login": "تسجيل الدخول",
        "login_notice": "واجهة تسجيل الدخول جاهزة. اربطها بواجهة المصادقة في الـ backend عند تفعيلها.",
        "secure_title": "آمن 100%",
        "secure_desc": "بياناتك مشفرة ومحمية",
        "support_title": "دعم 24/7",
        "support_desc": "موجودين لمساعدتك في أي وقت",
        "login_notice": "واجهة تسجيل الدخول جاهزة للربط مع نظام المصادقة.",
        "theme_light": "الوضع الفاتح",
        "theme_dark": "الوضع الداكن",

        # Home
        "hero_badge": "مدعوم بالذكاء الاصطناعي",
        "hero_title_1": "التعرف على المركبات",
        "hero_title_2": "بكل سهولة",
        "hero_subtitle": "ارفع صورة لأي مركبة وسيقوم نموذج الذكاء الاصطناعي بتحديد الشركة المصنعة والموديل والسنة فوراً وبدقة عالية.",
        "start_detection": "ابدأ الكشف",
        "learn_more": "اعرف المزيد",
        "how_it_works": "كيف يعمل الموقع",
        "feat_detect_title": "الكشف عن المركبات",
        "feat_detect_desc": "اكتشاف المركبات في الصور بدقة عالية.",
        "feat_process_title": "معالجة بالذكاء الاصطناعي",
        "feat_process_desc": "يقوم الذكاء الاصطناعي بتحليل الصورة في ثوانٍ.",
        "feat_extract_title": "استخراج البيانات",
        "feat_extract_desc": "يتم استخراج الماركة والموديل والسنة.",
        "feat_results_title": "نتائج ذكية",
        "feat_results_desc": "تظهر النتائج فوراً.",
        "stat_accuracy": "نسبة الدقة",
        "stat_images": "صورة تمت معالجتها",
        "stat_ai_powered": "بالذكاء الاصطناعي",
        "stat_support": "دعم فني",

        # Detect
        "detect_title": "كشف المركبة",
        "detect_subtitle": "ارفع صورة واضحة للمركبة التي تريد التعرف عليها",
        "upload_title": "اسحب وأفلت الصورة هنا",
        "upload_subtitle": "أو اضغط للاستعراض",
        "browse_files": "استعراض الملفات",
        "upload_label": "رفع",
        "upload_legend_formats": "الصيغ المدعومة: JPG, PNG, WEBP",
        "upload_legend_max_size": "الحد الأقصى للحجم: 10 ميجابايت",
        "secure_title": "صورتك آمنة وخاصة.",
        "secure_desc": "نحن لا نخزّن أو نشارك صورك.",
        "tips_title": "نصائح للحصول على أفضل النتائج",
        "tip_1": "استخدم صوراً واضحة وعالية الجودة",
        "tip_2": "تأكد من ظهور المركبة بالكامل",
        "tip_3": "الإضاءة الجيدة تحسّن الدقة",
        "tip_4": "تجنب الصور الضبابية أو المظلمة",
        "please_upload_first": "الرجاء رفع صورة أولاً.",

        # Loading
        "loading_title": "جاري تحليل مركبتك",
        "loading_subtitle": "يرجى الانتظار بينما يقوم الذكاء الاصطناعي بمعالجة الصورة",
        "step_upload": "جاري رفع الصورة",
        "step_preprocess": "جاري تجهيز الصورة",
        "step_extract": "جاري استخراج الخصائص",
        "step_vector_db": "جاري البحث في قاعدة البيانات المتجهة (FAISS)",
        "step_kb": "جاري الاستعلام من قاعدة المعرفة (MongoDB)",
        "step_prices": "جاري التحقق من أحدث أسعار السوق",
        "step_generate": "جاري توليد إجابة الذكاء الاصطناعي",
        "step_finalize": "جاري إنهاء النتائج",
        "backend_unavailable": "الخادم غير متاح حالياً، سيتم عرض بيانات تجريبية.",
        "no_pending_image": "لم يتم العثور على صورة للتحليل. الرجاء البدء من صفحة الكشف.",
        "back_to_detect": "الرجوع إلى صفحة الكشف",

        # Result
        "result_title": "نتيجة الكشف",
        "no_result_yet": "لا توجد نتيجة كشف بعد.",
        "spec_make": "الشركة المصنعة",
        "spec_model": "الموديل",
        "spec_body_type": "نوع الهيكل",
        "spec_color": "اللون",
        "ask_ai": "اسأل المساعد الذكي",
        "download_report": "تحميل التقرير",
        "analyze_another": "تحليل صورة أخرى",

        # Chat
        "chat_title": "المساعد الذكي",
        "chat_about_title": "عن المساعد الذكي",
        "chat_about_desc": "اسألني أي شيء عن المركبات: المواصفات، المميزات، المقارنات، الأسعار والمزيد.",
        "chat_detected_vehicle": "المركبة المكتشفة",
        "chat_confidence": "نسبة الثقة",
        "chat_suggested": "أسئلة مقترحة",
        "chat_placeholder": "اكتب سؤالك هنا...",
        "chat_hello": "مرحباً! اسألني عن أي مركبة — المواصفات، المميزات، المقارنات، الأسعار والمزيد.",
        "chat_demo_notice": "(وضع تجريبي — الخادم غير متاح)",
        "sugg_fuel": "استهلاك الوقود",
        "sugg_hp": "قوة المحرك",
        "sugg_maintenance": "نصائح الصيانة",
        "sugg_reliability": "الموثوقية",
        "sugg_price": "السعر",
        "sugg_alternatives": "بدائل مشابهة",

        # Features
        "features_title": "مميزات قوية",
        "features_subtitle": "كل ما تحتاجه للتعرف الدقيق على المركبات والتحليل الذكي",
        "f_detect_t": "كشف المركبات بالذكاء الاصطناعي",
        "f_detect_d": "نموذج رؤية حاسوبية متقدم للكشف عن المركبات في الصور بدقة عالية.",
        "f_instant_t": "تعرف فوري",
        "f_instant_d": "تحديد الشركة المصنعة والموديل والسنة في ثوانٍ.",
        "f_specs_t": "مواصفات تفصيلية",
        "f_specs_d": "احصل على مواصفات ومميزات وأداء شامل والمزيد.",
        "f_assistant_t": "مساعد ذكي",
        "f_assistant_d": "اسأل أي شيء عن المركبة المكتشفة واحصل على إجابات ذكية.",
        "f_market_t": "معلومات السوق",
        "f_market_d": "أسعار السوق الحالية والاتجاهات وتقدير القيمة.",
        "f_sources_t": "مصادر متعددة",
        "f_sources_d": "معلومات مجمّعة من مصادر سيارات موثوقة.",
        "f_export_t": "تصدير التقارير",
        "f_export_d": "تحميل تقارير تفصيلية بصيغة PDF.",
        "f_secure_t": "آمن وخاص",
        "f_secure_d": "بياناتك مشفّرة وخصوصيتك أولويتنا.",

        # Developers
        "developers_title": "المطورون",
        "developers_subtitle": "تعرف على الفريق وراء Vehicle Vision AI",
        "view_profile": "عرض الملف الشخصي",
        "view_team_photo": "عرض صورة الفريق",
        "team_tagline_title": "نبني حلولاً ذكية",
        "team_tagline_desc": "معاً نبني مستقبل التعرف على المركبات بالذكاء الاصطناعي",

        # Developer profile
        "profile_title": "الملف الشخصي للمطور",
        "profile_back": "الرجوع إلى المطورين",
        "profile_contact": "التواصل",
        "profile_skills": "المهارات",
        "profile_phone": "الهاتف",
        "profile_email": "البريد الإلكتروني",
        "profile_github": "جيتهاب",
        "profile_linkedin": "لينكدإن",
        "profile_not_found": "لم يتم العثور على المطور.",

        # Team photo
        "team_photo_title": "صورة الفريق",
        "team_photo_subtitle": "الأشخاص الذين يبنون Vehicle Vision AI",
        "team_photo_caption": "فريق Vehicle Vision AI",

        # About
        "about_badge": "من نحن",
        "about_title": "عن Vehicle Vision AI",
        "about_desc": "Vehicle Vision AI منصة ذكية للتعرف على المركبات تستخدم الذكاء الاصطناعي والرؤية الحاسوبية المتقدمة لتحديد المركبات من الصور بدقة عالية وتقديم معلومات تفصيلية عنها.",
        "about_mission_title": "مهمتنا",
        "about_mission_desc": "إتاحة معلومات المركبات للجميع من خلال تقنية الذكاء الاصطناعي.",
        "about_vision_title": "رؤيتنا",
        "about_vision_desc": "أن نكون المنصة الرائدة عالمياً للتعرف على المركبات بالذكاء الاصطناعي.",
        "stat_founded": "تأسست",
        "stat_users": "مستخدم سعيد",
        "stat_analyzed": "صورة تم تحليلها",
        "tech_stack_title": "التقنيات المستخدمة",

        # History
        "history_title": "سجل الكشف",
        "history_subtitle": "تصفح مركباتك التي تم اكتشافها سابقاً وارجع إليها",
        "history_search": "ابحث في السجل",
        "history_empty": "لا توجد عمليات كشف بعد. جرّب كشف مركبة أولاً.",
        "history_view": "عرض النتيجة",
        "history_report": "التقرير",
        "history_delete": "حذف",
        "history_deleted": "تم حذف عملية الكشف.",

        # PDF Report
        "report_title": "تقرير PDF",
        "report_subtitle": "حمّل ملخصاً بصيغة PDF قابل للمشاركة لهذا الكشف",
        "report_no_detection": "لم يتم اختيار أي كشف. قم بكشف مركبة أولاً لإنشاء تقرير.",
        "report_preview_title": "معاينة التقرير",
        "report_generate": "إنشاء وتحميل PDF",
        "report_generating": "جاري إنشاء التقرير...",
        "report_ready": "تقريرك جاهز.",
        "report_demo_notice": "الخادم غير متاح — سيتم عرض تقرير تجريبي.",
        "report_field_id": "رقم الكشف",
        "report_field_date": "التاريخ",
        "report_field_vehicle": "المركبة",
        "report_field_confidence": "نسبة الثقة",
    },
}


def init_lang() -> None:
    if "lang" not in st.session_state:
        st.session_state.lang = "en"


def toggle_lang() -> None:
    st.session_state.lang = "ar" if st.session_state.lang == "en" else "en"


def t(key: str) -> str:
    """Translate a key using the current session language, falling back to English."""
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS["en"].get(key, key))


def is_rtl() -> bool:
    return st.session_state.get("lang", "en") == "ar"