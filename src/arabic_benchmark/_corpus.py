# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Built-in Arabic sentence corpus for the benchmark.

30 clean logical-order Arabic sentences spanning news/formal, everyday
conversation, mixed Arabic-Latin-digit content, and longer complex sentences.
No external download required.  All sentences are Modern Standard Arabic.
"""
from __future__ import annotations

SENTENCES: list[str] = [
    # News / formal
    "أعلنت الحكومة عن خطة جديدة للتنمية الاقتصادية",
    "تشهد المنطقة تحولات سياسية واجتماعية كبيرة",
    "وقعت الدول الأعضاء على الاتفاقية الدولية للتعاون",
    "أفادت التقارير بارتفاع معدلات النمو الاقتصادي هذا العام",
    "عقد المسؤولون اجتماعاً طارئاً لمناقشة الأزمة",

    # Everyday conversation
    "مرحبا كيف حالك اليوم",
    "هل يمكنك مساعدتي في هذا الأمر",
    "أريد أن أتعلم اللغة العربية بشكل صحيح",
    "الطقس جميل اليوم والشمس مشرقة",
    "أحب القراءة والتعلم في أوقات الفراغ",

    # Mixed Arabic + digits / Latin
    "تأسست الشركة عام 1995 وتضم أكثر من 500 موظف",
    "يبلغ عدد سكان المدينة حوالي 2 مليون نسمة",
    "أرسل البريد الإلكتروني إلى info@example.com للتواصل",
    "يعمل النظام على الإصدار 3.14 من البرنامج",
    "حقق الفريق نتيجة 3 مقابل 1 في المباراة",

    # Religion / culture
    "بسم الله الرحمن الرحيم",
    "السلام عليكم ورحمة الله وبركاته",
    "الحمد لله رب العالمين",
    "إن الله على كل شيء قدير",
    "ونسأل الله التوفيق والسداد",

    # Longer / complex
    "تعتبر اللغة العربية من أقدم اللغات في العالم وأكثرها انتشاراً",
    "يسعى العلماء إلى فهم أسرار الكون والوصول إلى المعرفة الحقيقية",
    "تلعب التكنولوجيا دوراً محورياً في تشكيل مستقبل البشرية",
    "يحتاج الذكاء الاصطناعي إلى بيانات عربية عالية الجودة لتحسين أدائه",
    "الثقافة العربية غنية بالتراث الأدبي والشعري عبر العصور",

    # Short / single word
    "الكتاب",
    "مرحبا",
    "شكراً",

    # Technical / NLP relevant
    "معالجة اللغة الطبيعية تتطلب نصوصاً عربية نظيفة",
    "تحتاج نماذج اللغة الكبيرة إلى بيانات تدريب عالية الجودة",
]
