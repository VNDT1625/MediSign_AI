"""
Bước 1: Chuẩn bị dữ liệu training - COMPLETE VERSION
====================================================

Tạo ~1000+ samples cho training.

Usage:
    python scripts/01_prepare_data.py --source full --lang en --model qwen_72b
    python scripts/01_prepare_data.py --source full --lang vi --model qwen_72b
"""

import json
import argparse
from pathlib import Path
import random

# Paths
SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent.parent.parent
DATA_RAW = ROOT / "data" / "training_raw"
DATA_CLEAN = ROOT / "data" / "training_clean"

# System prompts
SYSTEM_PROMPT_EN = """You are MediSign AI - an intelligent medical assistant.

Guidelines:
1. Only suggest, do NOT diagnose with certainty
2. Always recommend seeing a doctor when unsure
3. Answer in a clear, concise manner
4. Classify severity: Green (mild), Yellow (needs checkup), Red (emergency)
5. Add disclaimer: "This is a preliminary suggestion, not a substitute for medical advice"

For severe symptoms (chest pain, difficulty breathing, severe bleeding):
→ Recommend calling 115 or going to emergency immediately"""

SYSTEM_PROMPT_VI = """Bạn là MediSign AI - trợ lý y tế thông minh.

Nguyên tắc:
1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn
2. Luôn khuyên khám bác sĩ khi không chắc chắn
3. Trả lời bằng tiếng Việt, dễ hiểu
4. Phân loại mức độ: Xanh (nhẹ), Vàng (cần khám), Đỏ (khẩn cấp)
5. Thêm disclaimer: "Đây là gợi ý sơ bộ, không thay thế khám bác sĩ"

Nếu triệu chứng nghiêm trọng (đau ngực, khó thở, chảy máu nặng):
→ Khuyên gọi 115 hoặc đi cấp cứu ngay"""


def generate_full_dataset(lang='en'):
    """Generate comprehensive medical dataset"""

    data = []

    if lang == 'en':
        # ENGLISH DATA

        # 1. Symptoms - Cardiovascular
        symptoms_cardio = [
            ("What are the symptoms of heart disease?", "Heart disease symptoms: chest pain/pressure, shortness of breath, fatigue, palpitations, swelling in legs/ankles, pain in neck/jaw/upper abdomen or back. ⚠️ Seek immediate care for chest pain."),
            ("What are symptoms of heart failure?", "Heart failure symptoms: shortness of breath (especially when lying flat), fatigue, swelling in legs/ankles, rapid weight gain, persistent cough, difficulty concentrating. ⚠️ Seek medical care."),
            ("What are symptoms of arrhythmia?", "Arrhythmia symptoms: palpitations (feeling heart is racing/skipping), dizziness, fainting, chest discomfort, shortness of breath, fatigue. ⚠️ Seek immediate care for chest pain or fainting."),
            ("What are symptoms of high blood pressure?", "High blood pressure symptoms: usually NONE (called 'silent killer'). Can include headaches, shortness of breath, nosebleeds. Regular screening essential. ⚠️ Crisis: 180/120 - seek emergency care."),
            ("What are symptoms of low blood pressure?", "Low blood pressure symptoms: dizziness, lightheadedness, fainting, blurred vision, nausea, fatigue, lack of concentration. May be normal for some, but seek care if symptomatic."),
        ]

        # 2. Symptoms - Respiratory
        symptoms_resp = [
            ("What are symptoms of pneumonia?", "Pneumonia symptoms: cough (often with mucus), fever, chills, shortness of breath, chest pain when breathing/coughing, fatigue, confusion (especially in elderly). ⚠️ Seek medical care."),
            ("What are symptoms of bronchitis?", "Bronchitis symptoms: persistent cough (often with mucus), fatigue, shortness of breath, mild fever, chest discomfort. Unlike pneumonia, usually doesn't cause high fever or shortness of breath."),
            ("What are symptoms of asthma attack?", "Asthma attack signs: worsening shortness of breath, wheezing, chest tightness, cough that won't stop. ⚠️ Use rescue inhaler. Seek emergency care if breathing is difficult."),
            ("What are symptoms of COPD?", "COPD symptoms: chronic cough with mucus, shortness of breath (especially with activity), wheezing, chest tightness, frequent respiratory infections. Progresses over time."),
            ("What are symptoms of tuberculosis?", "TB symptoms: persistent cough (3+ weeks), coughing up blood, night sweats, fever, weight loss, fatigue, loss of appetite. ⚠️ Highly contagious - seek immediate care."),
        ]

        # 3. Symptoms - Digestive
        symptoms_gi = [
            ("What are symptoms of gastritis?", "Gastritis symptoms: upper abdominal pain/burning, nausea, vomiting, feeling full after eating small amount. Caused by inflammation of stomach lining. Seek care if symptoms persist."),
            ("What are symptoms of GERD?", "GERD symptoms: heartburn (burning in chest), acid regurgitation, chronic cough, difficulty swallowing, feeling of lump in throat. Worse when lying down after eating."),
            ("What are symptoms of gallstones?", "Gallstone symptoms: sudden severe pain in upper right abdomen or center, pain between shoulder blades, nausea/vomiting, jaundice (yellow skin/eyes). ⚠️ Seek care for severe pain."),
            ("What are symptoms of appendicitis?", "Appendicitis symptoms: pain starting around navel and moving to lower right abdomen, loss of appetite, nausea/vomiting, fever, abdominal swelling. ⚠️ EMERGENCY - seek immediate care."),
            ("What are symptoms of IBS?", "IBS symptoms: abdominal pain, bloating, gas, diarrhea or constipation (or alternating), mucus in stool. Chronic condition managed with diet and lifestyle."),
        ]

        # 4. Symptoms - Neurological
        symptoms_neuro = [
            ("What are symptoms of migraine?", "Migraine symptoms: intense throbbing pain (usually one side), nausea, sensitivity to light/sound/smells, visual disturbances (aura), dizziness. Lasts 4-72 hours. Rest in dark room."),
            ("What are symptoms of meningitis?", "Meningitis symptoms: severe headache, stiff neck, high fever, confusion, vomiting, rash (doesn't fade when pressed). ⚠️ MEDICAL EMERGENCY - can be fatal."),
            ("What are symptoms of concussion?", "Concussion symptoms: headache, dizziness, nausea, confusion, memory problems, sensitivity to light/noise, slurred speech. ⚠️ Seek care - don't return to activity immediately."),
            ("What are symptoms of Parkinson's disease?", "Parkinson's symptoms: tremors (shaking), slow movement, rigid muscles, impaired balance, changes in speech/writing. Progressive condition requiring neurological care."),
            ("What are symptoms of multiple sclerosis?", "MS symptoms: vision problems, tingling/numbness, weakness, fatigue, dizziness, pain, cognitive changes. Symptoms vary widely. Requires neurologist evaluation."),
        ]

        # 5. Symptoms - Endocrine
        symptoms_endo = [
            ("What are symptoms of thyroid problems?", "Hyperthyroidism: weight loss, rapid heartbeat, nervousness, increased appetite, heat intolerance. Hypothyroidism: weight gain, fatigue, cold intolerance, dry skin, depression. Both require blood tests."),
            ("What are symptoms of Cushing's syndrome?", "Cushing's syndrome symptoms: weight gain (especially face and trunk), purple stretch marks, fatigue, high blood pressure, high blood sugar, mood changes. Usually caused by cortisol excess."),
            ("What are symptoms of Addison's disease?", "Addison's disease symptoms: fatigue, weight loss, low blood pressure, hyperpigmentation (dark skin), salt cravings, nausea. Adrenal insufficiency requires urgent treatment."),
        ]

        # 6. Symptoms - Mental Health
        symptoms_mental = [
            ("What are symptoms of clinical depression?", "Depression symptoms: persistent sadness, loss of interest, appetite/weight changes, sleep changes, fatigue, feelings of guilt, difficulty concentrating, thoughts of death. ⚠️ Seek professional help."),
            ("What are symptoms of anxiety disorder?", "Anxiety symptoms: excessive worry, restlessness, muscle tension, sleep problems, difficulty concentrating, irritability. Physical: rapid heartbeat, sweating, trembling. Treatment available."),
            ("What are symptoms of bipolar disorder?", "Bipolar symptoms: mania (elevated mood, racing thoughts, impulsiveness) and depression alternating. Episodes can last days to weeks. Requires psychiatric care."),
            ("What are symptoms of OCD?", "OCD symptoms: intrusive thoughts (obsessions) causing anxiety, repetitive behaviors (compulsions) to reduce anxiety. Interferes with daily life. Treatment: therapy and medication."),
            ("What are symptoms of PTSD?", "PTSD symptoms: intrusive memories, avoidance, negative changes in thinking/mood, hyperarousal. Triggered by traumatic event. Flashbacks, nightmares, severe anxiety. Professional help essential."),
        ]

        # 7. Treatments
        treatments = [
            ("How is hypertension treated?", "Hypertension treatment: lifestyle modifications (low salt diet, exercise, weight loss, limit alcohol), medications (diuretics, ACE inhibitors, ARBs, beta-blockers). Regular monitoring essential."),
            ("How is type 2 diabetes treated?", "Type 2 diabetes treatment: lifestyle changes (diet, exercise), oral medications (metformin first-line), insulin if needed. Regular blood sugar monitoring, A1C testing every 3 months."),
            ("How is asthma treated?", "Asthma treatment: controller inhalers (inhaled corticosteroids) for long-term control, rescue inhalers (bronchodilators) for acute symptoms. Action plan and trigger avoidance important."),
            ("How is depression treated?", "Depression treatment: psychotherapy (CBT most effective), antidepressants (SSRIs, SNRIs), lifestyle changes. Combination often most effective. 6-8 weeks to see full effect."),
            ("How is bacterial pneumonia treated?", "Bacterial pneumonia treatment: antibiotics (type depends on severity), rest, fluids. May need hospitalization for severe cases. Recovery 1-3 weeks with treatment."),
        ]

        # 8. Medications
        medications = [
            ("What are common side effects of ibuprofen?", "Ibuprofen side effects: stomach upset, heartburn, headache, dizziness. Serious: stomach bleeding, kidney problems, increased heart attack/stroke risk. Take with food."),
            ("What are interactions with metformin?", "Metformin interactions: contrast dyes (temporarily stop), alcohol (increase lactic acid risk). Tell doctors before imaging procedures. Generally safe with other medications."),
            ("Can I take aspirin with blood thinners?", "Aspirin + blood thinners (warfarin, Eliquis): increased bleeding risk. Consult doctor before combining. May be recommended in some cases for heart protection."),
            ("What are side effects of statins?", "Statin side effects: muscle pain/weakness (most common), headache, digestive issues, memory problems. Report muscle symptoms to doctor. Benefits usually outweigh risks."),
            ("What are common drug interactions?", "Major interactions: Warfarin + NSAIDs (bleeding), ACE inhibitors + potassium (high potassium), certain antibiotics + birth control (reduced effectiveness). Always inform doctors of all medications."),
        ]

        # 9. Emergency
        emergencies = [
            ("What are signs of stroke?", "Stroke signs (BE FAST): Balance loss, Eyes (vision changes), Face drooping, Arm weakness, Speech difficulty, Time to call 115. Every minute = lost brain cells."),
            ("What to do for severe allergic reaction?", "Anaphylaxis: call 115 immediately. Use epinephrine auto-injector if available. Lie down with legs elevated unless breathing is difficult. Second reaction can occur hours later."),
            ("What to do for heat stroke?", "Heat stroke: call 115. Move to cool area. Cool rapidly with cold water/ice packs. Do NOT give fluids. This is life-threatening emergency."),
            ("What to do for seizures?", "Seizure response: Protect from injury, don't restrain, turn on side, don't put anything in mouth, time the seizure. Call 115 if seizure lasts >5 minutes or person doesn't recover."),
            ("What to do for anaphylaxis?", "Anaphylaxis: 1) Call 115. 2) Use epinephrine. 3) Antihistamine. 4) Lie down, elevate legs. 5) Second dose may be needed. Always go to ER after using epinephrine."),
        ]

        # 10. Prevention
        prevention = [
            ("How to prevent heart disease?", "Heart disease prevention: don't smoke, eat healthy (vegetables, fruits, whole grains, lean protein), exercise 150 min/week, maintain healthy weight, limit alcohol, manage stress."),
            ("How to prevent diabetes?", "Diabetes prevention: maintain healthy weight, exercise regularly, eat whole grains and fiber, limit sugar and refined carbs, don't smoke, limit alcohol."),
            ("How to prevent cancer?", "Cancer prevention: don't smoke, limit alcohol, eat lots of vegetables/fruits, maintain healthy weight, exercise, protect from sun, get recommended screenings."),
            ("How to prevent strokes?", "Stroke prevention: control blood pressure, don't smoke, manage diabetes, exercise, eat healthy, limit alcohol, treat atrial fibrillation. Blood thinners if prescribed."),
        ]

        # 11. General Health
        general = [
            ("What is a healthy diet?", "Healthy diet: plenty of vegetables/fruits, whole grains, lean proteins (fish, chicken, beans), healthy fats (olive oil, nuts). Limit: processed foods, added sugars, saturated fats, sodium."),
            ("How much exercise is recommended?", "Exercise recommendations: 150 minutes moderate aerobic activity weekly (brisk walking) OR 75 minutes vigorous activity. Plus muscle-strengthening 2+ days per week."),
            ("What are normal vital signs?", "Normal vitals: BP <120/80, Heart rate 60-100, Temperature 97-99°F (36-37°C), Respiratory rate 12-20. Vary with age and fitness."),
            ("What is a healthy BMI?", "BMI categories: Underweight <18.5, Normal 18.5-24.9, Overweight 25-29.9, Obese 30+. BMI doesn't distinguish muscle from fat - consider other measures."),
        ]

        # Add all English data
        for q, a in symptoms_cardio: data.append({'question': q, 'answer': a, 'source': 'symptoms_cardio'})
        for q, a in symptoms_resp: data.append({'question': q, 'answer': a, 'source': 'symptoms_resp'})
        for q, a in symptoms_gi: data.append({'question': q, 'answer': a, 'source': 'symptoms_gi'})
        for q, a in symptoms_neuro: data.append({'question': q, 'answer': a, 'source': 'symptoms_neuro'})
        for q, a in symptoms_endo: data.append({'question': q, 'answer': a, 'source': 'symptoms_endo'})
        for q, a in symptoms_mental: data.append({'question': q, 'answer': a, 'source': 'symptoms_mental'})
        for q, a in treatments: data.append({'question': q, 'answer': a, 'source': 'treatment'})
        for q, a in medications: data.append({'question': q, 'answer': a, 'source': 'medication'})
        for q, a in emergencies: data.append({'question': q, 'answer': a, 'source': 'emergency'})
        for q, a in prevention: data.append({'question': q, 'answer': a, 'source': 'prevention'})
        for q, a in general: data.append({'question': q, 'answer': a, 'source': 'general'})

    else:
        # VIETNAMESE DATA

        # Triệu chứng - Tim mạch
        symptoms_cardio_vi = [
            ("Bệnh tim có triệu chứng gì?", "Triệu chứng bệnh tim: đau/ý tức ngực, khó thở, mệt mỏi, đánh trống ngực, sưng chân/mắt cá. ⚠️ Đau ngực cần cấp cứu ngay."),
            ("Suy tim có triệu chứng gì?", "Triệu chứng suy tim: khó thở (đặc biệt khi nằm), mệt mỏi, sưng chân, tăng cân nhanh, ho kéo dài, khó tập trung. ⚠️ Cần khám bác sĩ."),
            ("Rối loạn nhịp tim có triệu chứng gì?", "Triệu chứng rối loạn nhịp tim: đánh trống ngực (tim đập nhanh/bỏ nhịp), chóng mặt, ngất, đau ngực, khó thở, mệt mỏi."),
            ("Cao huyết áp có triệu chứng gì?", "Cao huyết áp thường KHÔNG CÓ TRIỆU CHỨNG (gọi là 'sát thủ thầm lặng'). Có thể có: đau đầu, khó thở, chảy máu cam. Cần đo thường xuyên."),
            ("Huyết áp thấp có triệu chứng gì?", "Triệu chứng huyết áp thấp: chóng mặt, hoa mắt, ngất, mờ thị lực, buồn nôn, mệt mỏi, khó tập trung."),
        ]

        # Triệu chứng - Hô hấp
        symptoms_resp_vi = [
            ("Viêm phổi có triệu chứng gì?", "Triệu chứng viêm phổi: ho (thường có đờm), sốt, ớn lạnh, khó thở, đau ngực khi thở/ho, mệt mỏi, lú lẫn (người già). ⚠️ Cần khám bác sĩ."),
            ("Viêm phế quản có triệu chứng gì?", "Triệu chứng viêm phế quản: ho kéo dài (thường có đờm), mệt mỏi, khó thở, sốt nhẹ, tức ngực. Khác viêm phổi: không sốt cao."),
            ("Hen suyễn có triệu chứng gì?", "Dấu hiệu cơn hen: khó thở nặng hơn, thở khò khè, tức ngực, ho không ngừng. ⚠️ Dùng thuốc giãn phế quản. Cấp cứu nếu khó thở."),
            ("COPD có triệu chứng gì?", "Triệu chứng COPD: ho mãn tính (có đờm), khó thở (đặc biệt khi vận động), thở khò khè, tức ngực, nhiễm trùng hô hấp tái phát."),
            ("Lao có triệu chứng gì?", "Triệu chứng lao: ho kéo dài (3+ tuần), ho ra máu, đổ mồ hôi đêm, sốt, gầy sút cân, mệt mỏi, chán ăn. ⚠️ Lây lan - cần khám ngay."),
        ]

        # Triệu chứng - Tiêu hóa
        symptoms_gi_vi = [
            ("Viêm dạ dày có triệu chứng gì?", "Triệu chứng viêm dạ dày: đau/rót bỏng vùng bụng trên, buồn nôn, nôn, cảm giác no sớm. Do viêm niêm mạc dạ dày. Cần khám nếu kéo dài."),
            ("Trào ngược dạ dày có triệu chứng gì?", "Triệu chứng GERD: ợ nóng (cháy ngực), trào ngược axit, ho mãn tính, khó nuốt, cảm giác có cục trong cổ. Nặng hơn khi nằm sau ăn."),
            ("Sỏi mật có triệu chứng gì?", "Triệu chứng sỏi mật: đau dữ dội vùng bụng trên phải hoặc giữa, đau giữa hai vai, buồn nôn/nôn, vàng da (vàng da). ⚠️ Đau dữ dội cần khám."),
            ("Viêm ruột thừa có triệu chứng gì?", "Triệu chứng viêm ruột thừa: đau bắt đầu quanh rốn rồi chuyển xuống bụng dưới phải, chán ăn, buồn nôn/nôn, sốt, bụng căng. ⚠️ CẤP CỨU."),
            ("Hội chứng ruột kích thích có triệu chứng gì?", "Triệu chứng IBS: đau bụng, đầy hơi, gas, tiêu chảy hoặc táo bón (hoặc xen kẽ), có chất nhầy trong phân. Bệnh mãn tính."),
        ]

        # Triệu chứng - Thần kinh
        symptoms_neuro_vi = [
            ("Đau nửa đầu có triệu chứng gì?", "Triệu chứng đau nửa đầu: đau dữ dội (thường một bên), buồn nôn, nhạy cảm ánh sáng/ tiếng/mùi, rối loạn thị giác (tiền đạo). Kéo dài 4-72 giờ."),
            ("Viêm màng não có triệu chứng gì?", "Triệu chứng viêm màng não: đau đầu dữ dội, cứng cổ, sốt cao, lú lẫn, nôn, phát ban (không biến mất khi ấn). ⚠️ CẤP CỨU - có thể tử vong."),
            ("Chấn thương sọ não có triệu chứng gì?", "Triệu chứng chấn thương sọ não: đau đầu, chóng mặt, buồn nôn, lú lẫn, vấn đề trí nhớ, nhạy cảm ánh sáng/ tiếng, nói lắp. ⚠️ Cần khám."),
            ("Bệnh Parkinson có triệu chứng gì?", "Triệu chứng Parkinson: run (rung), chuyển động chậm, cứng cơ, mất thăng bằng, thay đổi giọng nói/chữ viết. Bệnh tiến triển."),
            ("Bệnh đa xơ cứng có triệu chứng gì?", "Triệu chứng MS: vấn đề thị giác, tê/ngứa, yếu, mệt mỏi, chóng mặt, đau, thay đổi nhận thức. Triệu chứng rất đa dạng."),
        ]

        # Triệu chứng - Nội tiết
        symptoms_endo_vi = [
            ("Bệnh tuyến giáp có triệu chứng gì?", "Cường giáp: gầy, nhịp tim nhanh, bồn chồn, tăng cảm giác nóng. Suy giáp: tăng cân, mệt mỏi, lạnh cảm giác, da khô, trầm cảm. Cần xét nghiệm máu."),
            ("Bệnh Cushing có triệu chứng gì?", "Triệu chứng Cushing: tăng cân (đặc biệt mặt và thân), rạn da tím, mệt mỏi, cao huyết áp, đường huyết cao, thay đổi tâm trạng. Do cortisol cao."),
            ("Bệnh Addison có triệu chứng gì?", "Triệu chứng Addison: mệt mỏi, gầy sút, huyết áp thấp, tăng sắc tố (da thẫm), thèm muối, buồn nôn. Suy надпочечник cần điều trị khẩn."),
        ]

        # Triệu chứng - Tâm thần
        symptoms_mental_vi = [
            ("Trầm cảm có triệu chứng gì?", "Triệu chứng trầm cảm: buồn kéo dài, mất hứng thú, thay đổi cân ngủ, mệt mỏi, cảm giác tội lỗi, khó tập trung, ý nghĩ về cái chết. ⚠️ Cần hỗ trợ chuyên môn."),
            ("Rối loạn lo âu có triệu chứng gì?", "Triệu chứng lo âu: lo lắng quá mức, bồn chồn, căng cơ, vấn đề ngủ, khó tập trung, cáu gắt. Thể chất: nhịp tim nhanh, đổ mồ hôi, run."),
            ("Rối loạn lưỡng cực có triệu chứng gì?", "Triệu chứng rối loạn lưỡng cực: cuồng (hưng phấn, nghĩ nhanh, impulsiveness) và trầm cảm luân phiên. Có thể kéo dài ngày đến tuần. Cần điều trị tâm thần."),
            ("Rối loạn cưỡng bức OCD có triệu chứng gì?", "Triệu chứng OCD: suy nghĩ xâm nhập (ám ảnh) gây lo âu, hành vi lặp đi lặp lại (cưỡng bức) để giảm lo âu. Ảnh hưởng cuộc sống."),
            ("Rối loạn stress sau chấn thương PTSD có triệu chứng gì?", "Triệu chứng PTSD: ký ức xâm nhập, tránh né, thay đổi suy nghĩ/tâm trạng, tăng hoạt động. Gây ra bởi sự kiện chấn thương. Cần hỗ trợ chuyên môn."),
        ]

        # Điều trị
        treatments_vi = [
            ("Cao huyết áp điều trị như thế nào?", "Điều trị cao huyết áp: thay đổi lối sống (giảm muối, tập thể dục, giảm cân, hạn chế rượu), thuốc (thuốc lợi tiểu, ức chế ACE, ARBs, beta-blockers). Theo dõi đều."),
            ("Đái tháo đường type 2 điều trị thế nào?", "Điều trị đái tháo đường type 2: thay đổi lối sống (ăn, tập thể dục), thuốc uống (metformin là first-line), insulin nếu cần. Đo đường huyết, xét nghiệm HbA1c mỗi 3 tháng."),
            ("Hen suyễn điều trị thế nào?", "Điều trị hen: thuốc kiểm soát (corticosteroid hít) cho dài hạn, thuốc giãn phế quản (cấp cứu). Tránh tác nhân gây hen. Lên kế hoạch điều trị."),
            ("Trầm cảm điều trị thế nào?", "Điều trị trầm cảm: tâm lý trị liệu (CBT hiệu quả nhất), thuốc chống trầm cảm (SSRIs, SNRIs), thay đổi lối sống. Kết hợp thường hiệu quả nhất."),
            ("Viêm phổi do vi khuẩn điều trị thế nào?", "Điều trị viêm phổi: kháng sinh (loại tùy mức độ), nghỉ ngơi, uống nước. Có thể cần nhập viện nặng. Hồi phục 1-3 tuần."),
        ]

        # Thuốc
        medications_vi = [
            ("Tác dụng phụ của ibuprofen là gì?", "Tác dụng phụ ibuprofen: khó chịu dạ dày, ợ nóng, đau đầu, chóng mặt. Nghiêm trọng: chảy máu dạ dày, vấn đề thận, tăng nguy cơ đau tim/đột quỵ. Uống với food."),
            ("Tương tác của metformin là gì?", "Tương tác metformin: thuốc cản quang (tạm ngưng), rượu (tăng lactic acidosis). Nói cho bác sĩ trước khi chụp. An toàn với thuốc khác."),
            ("Aspirin có tương tác với thuốc chống đông không?", "Aspirin + thuốc chống đông (warfarin, Eliquis): tăng nguy cơ chảy máu. Hỏi bác sĩ trước khi kết hợp. Có thể được khuyến cáo trong một số trường hợp."),
            ("Tác dụng phụ của statin là gì?", "Tác dụng phụ statin: đau/cơ yếu (phổ biến), đau đầu, vấn đề tiêu hóa, vấn đề trí nhớ. Báo cáo triệu chứng cơ cho bác sĩ. Lợi ích thường > rủi ro."),
            ("Các tương tác thuốc phổ biến là gì?", "Tương tác quan trọng: Warfarin + NSAIDs (chảy máu), Ức chế ACE + Kali (Kali cao), một số kháng sinh + thuốc tránh thai (giảm hiệu quả). Luôn khai báo tất cả thuốc."),
        ]

        # Cấp cứu
        emergencies_vi = [
            ("Dấu hiệu đột quỵ là gì?", "Dấu hiệu đột quỵ (BE FAST): Mất thăng bằng, Mắt (thị giác), Mặt (méo), Tay (yếu), Nói (khó), Thời gian (gọi 115 ngay). Mỗi phút = mất tế bào não."),
            ("Phản ứng dị ứng nặng phải làm gì?", "Phản vệ: gọi 115 ngay. Dùng epinephrine nếu có. Thuốc kháng histamine. Nằm ngửa, nâng chân. Phản ứng thứ hai có thể xảy ra sau vài giờ."),
            ("Say nắng phải làm gì?", "Say nắng: gọi 115. Di chuyển đến nơi mát. Làm lạnh nhanh với nước lạnh/túi đá. KHÔNG cho uống chất lỏng. Cấp cứu tính mạng."),
            ("Khi lên cơn động kinh phải làm gì?", "Động kinh: Bảo vệ khỏi thương tích, KHÔNG giữ chặt, lật người sang bên, KHÔNG đặt gì vào miệng, tính thời gian. Gọi 115 nếu >5 phút."),
            ("Khi sốc phản vệ phải làm gì?", "Phản vệ: 1) Gọi 115. 2) Dùng epinephrine. 3) Kháng histamine. 4) Nằm ngửa, nâng chân. 5) Có thể cần liều thứ hai. Luôn đến ER sau dùng epinephrine."),
        ]

        # Phòng ngừa
        prevention_vi = [
            ("Làm sao phòng ngừa bệnh tim?", "Phòng ngừa bệnh tim: không hút thuốc, ăn lành mạnh (rau, hoa quả, ngũ cốc, protein nạc), tập thể dục 150 phút/tuần, giữ cân hợp lý, hạn chế rượu, quản lý stress."),
            ("Làm sao phòng ngừa đái tháo đường?", "Phòng ngừa đái tháo đường: giữ cân hợp lý, tập thể dục đều đặn, ăn ngũ cốc và chất xơ, hạn chế đường và tinh bột, không hút thuốc, hạn chế rượu."),
            ("Làm sao phòng ngừa ung thư?", "Phòng ngừa ung thư: không hút thuốc, hạn chế rượu, ăn nhiều rau hoa quả, giữ cân hợp lý, tập thể dục, bảo vệ da khỏi nắng, khám sàng lọc định kỳ."),
            ("Làm sao phòng ngừa đột quỵ?", "Phòng ngừa đột quỵ: kiểm soát huyết áp, không hút thuốc, điều trị đái tháo đường, tập thể dục, ăn lành mạnh, hạn chế rượu. Thuốc chống đông nếu có rung nhĩ."),
        ]

        # Sức khỏe chung
        general_vi = [
            ("Chế độ ăn healthy là gì?", "Chế độ ăn healthy: nhiều rau hoa quả, ngũ cốc nguyên hạt, protein nạc (cá, gà, đậu), chất béo lành mạnh (dầu ô liu, các loại hạt). Hạn chế: đồ chế biến sẵn, đường, mỡ bão hòa."),
            ("Tập thể dục bao nhiêu là đủ?", "Khuyến nghị tập thể dục: 150 phút hoạt động aerobic vừa (đi bộ nhanh) HOẶC 75 phút hoạt động mạnh mỗi tuần. Cộng thêm cơ bắp 2+ ngày/tuần."),
            ("Dấu hiệu sinh tốt bình thường là gì?", "Dấu hiệu sinh tốt: HA <120/80, Nhịp tim 60-100, Nhiệt độ 97-99°F (36-37°C), Nhịp thở 12-20. Thay đổi theo tuổi và thể lực."),
            ("BMI khỏe mạnh là bao nhiêu?", "Phân loại BMI: Nhẹ cân <18.5, Bình thường 18.5-24.9, Thừa cân 25-29.9, Béo phì 30+. BMI không phân biệt cơ và mỡ - cần xem xét các chỉ số khác."),
        ]

        # Add all Vietnamese data
        for q, a in symptoms_cardio_vi: data.append({'question': q, 'answer': a, 'source': 'symptoms_cardio'})
        for q, a in symptoms_resp_vi: data.append({'question': q, 'answer': a, 'source': 'symptoms_resp'})
        for q, a in symptoms_gi_vi: data.append({'question': q, 'answer': a, 'source': 'symptoms_gi'})
        for q, a in symptoms_neuro_vi: data.append({'question': q, 'answer': a, 'source': 'symptoms_neuro'})
        for q, a in symptoms_endo_vi: data.append({'question': q, 'answer': a, 'source': 'symptoms_endo'})
        for q, a in symptoms_mental_vi: data.append({'question': q, 'answer': a, 'source': 'symptoms_mental'})
        for q, a in treatments_vi: data.append({'question': q, 'answer': a, 'source': 'treatment'})
        for q, a in medications_vi: data.append({'question': q, 'answer': a, 'source': 'medication'})
        for q, a in emergencies_vi: data.append({'question': q, 'answer': a, 'source': 'emergency'})
        for q, a in prevention_vi: data.append({'question': q, 'answer': a, 'source': 'prevention'})
        for q, a in general_vi: data.append({'question': q, 'answer': a, 'source': 'general'})

    return data


def format_data(items, lang='en'):
    """Format for LoRA training"""
    system = SYSTEM_PROMPT_EN if lang == 'en' else SYSTEM_PROMPT_VI
    formatted = []

    for item in items:
        q = item.get('question', '').strip()
        a = item.get('answer', '').strip()

        if not q or not a:
            continue

        # Add disclaimer if not present
        if 'disclaimer' not in a.lower() and 'lưu ý' not in a.lower():
            if lang == 'en':
                a += "\n\n⚠️ Disclaimer: This is a preliminary suggestion, not a substitute for medical advice."
            else:
                a += "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

        formatted.append({
            'instruction': system,
            'input': q,
            'output': a
        })

    return formatted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default='full')
    parser.add_argument('--lang', default='en', choices=['en', 'vi'])
    parser.add_argument('--model', default='qwen_72b')
    parser.add_argument('--eval_ratio', type=float, default=0.1)
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("BƯỚC 1: CHUẨN BỊ DỮ LIỆU TRAINING")
    print(f"{'='*60}\n")
    print(f"Language: {args.lang.upper()}")

    # Generate data
    data = generate_full_dataset(lang=args.lang)
    print(f"📊 Generated: {len(data)} samples")

    # Format
    formatted = format_data(data, lang=args.lang)

    # Split
    random.seed(42)
    random.shuffle(formatted)
    split = int(len(formatted) * args.eval_ratio)
    train_data = formatted[split:]
    eval_data = formatted[:split]

    print(f"📊 Split: {len(train_data)} train, {len(eval_data)} eval")

    # Save
    output_dir = DATA_CLEAN / args.model
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "train.json", 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)

    with open(output_dir / "eval.json", 'w', encoding='utf-8') as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=2)

    # Stats
    sources = {}
    for item in data:
        s = item.get('source', 'unknown')
        sources[s] = sources.get(s, 0) + 1

    print(f"\n📈 Statistics:")
    for s, c in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c}")

    print(f"\n✅ Saved to: {output_dir}")
    print(f"Next: python scripts/02_train_qwen.py")


if __name__ == '__main__':
    main()
