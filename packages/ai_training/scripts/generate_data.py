"""
Generate comprehensive medical dataset
"""
import json
import os

data = []

# 1. CARDIOVASCULAR (20)
cardio = [
    ("What are symptoms of heart disease?", "Heart disease symptoms: chest pain/pressure, shortness of breath, fatigue, palpitations, swelling in legs/ankles. Seek immediate care for chest pain."),
    ("What are symptoms of heart attack in women?", "Women heart attack symptoms: unusual fatigue, sleep disturbance, indigestion, anxiety. Classic chest pain may be absent. Call 115 immediately."),
    ("What are symptoms of heart failure?", "Heart failure: shortness of breath (lying flat), fatigue, swelling in legs/ankles, rapid weight gain, persistent cough, difficulty concentrating."),
    ("What are symptoms of arrhythmia?", "Arrhythmia: palpitations (heart racing/skipping), dizziness, fainting, chest discomfort, shortness of breath, fatigue."),
    ("What are symptoms of high blood pressure?", "High BP usually has NO symptoms. Called silent killer. Regular screening essential. Crisis (180/120) = emergency."),
    ("What are symptoms of low blood pressure?", "Low BP: dizziness, lightheadedness, fainting, blurred vision, nausea, fatigue, lack of concentration."),
    ("What are symptoms of deep vein thrombosis?", "DVT symptoms: leg swelling, leg pain/tenderness, red/discolored skin, warm leg. EMERGENCY if piece breaks off (pulmonary embolism)."),
    ("What are symptoms of pulmonary embolism?", "PE symptoms: sudden shortness of breath, chest pain worsening with breathing, rapid heart rate, coughing up blood. EMERGENCY."),
    ("What are symptoms of peripheral artery disease?", "PAD symptoms: leg pain when walking (claudication), leg numbness, cold legs, hair loss on legs, slow-healing wounds."),
    ("What are symptoms of atrial fibrillation?", "AFib symptoms: heart palpitations, fatigue, shortness of breath, dizziness, chest pain. Increases stroke risk 5x."),
    ("What are symptoms of myocarditis?", "Myocarditis: chest pain, fatigue, shortness of breath, flu-like symptoms, palpitations. Can be caused by viral infection."),
    ("What are symptoms of pericarditis?", "Pericarditis: sharp chest pain (worse when lying down), shortness of breath, dry cough, fatigue."),
    ("What are symptoms of heart valve problems?", "Valve disease: shortness of breath, fatigue, dizziness, fainting, chest pain, palpitations, swollen ankles."),
    ("What are warning signs of cardiac arrest?", "Cardiac arrest: sudden collapse, no pulse, no breathing, loss of consciousness. IMMEDIATE CPR and call 115."),
    ("What are symptoms of cardiomyopathy?", "Cardiomyopathy: shortness of breath, fatigue, swelling in legs, irregular heartbeat, dizziness, fainting."),
    ("What are symptoms of angina?", "Angina: chest pain/pressure triggered by activity/exercise, goes away with rest. Warning sign of heart disease."),
    ("What are symptoms of congenital heart disease?", "Congenital heart disease signs: cyanosis (blue skin), shortness of breath, fatigue, heart murmur. Present from birth."),
    ("What are symptoms of endocarditis?", "Endocarditis: fever, chills, night sweats, fatigue, muscle aches, shortness of breath, swelling in legs."),
    ("What are symptoms of myocarditis in children?", "Pediatric myocarditis: fatigue, rapid breathing, chest pain, fainting, flu-like symptoms. Can follow viral illness."),
    ("What are symptoms of hypertensive crisis?", "Hypertensive crisis: severe headache, chest pain, vision problems, confusion, shortness of breath, nosebleed. EMERGENCY."),
]
for q, a in cardio:
    data.append({'question': q, 'answer': a, 'source': 'cardio'})

# 2. RESPIRATORY (20)
respiratory = [
    ("What are symptoms of pneumonia?", "Pneumonia: cough (often with mucus), fever, chills, shortness of breath, chest pain, fatigue, confusion (elderly)."),
    ("What are symptoms of COVID-19?", "COVID-19: fever, cough, shortness of breath, fatigue, loss of taste/smell, sore throat, body aches."),
    ("What are symptoms of bronchitis?", "Bronchitis: persistent cough (with mucus), fatigue, shortness of breath, mild fever, chest discomfort."),
    ("What are symptoms of asthma?", "Asthma: wheezing, shortness of breath, chest tightness, coughing (especially at night). Use rescue inhaler."),
    ("What are symptoms of COPD?", "COPD: chronic cough with mucus, shortness of breath (worsens with activity), wheezing, chest tightness."),
    ("What are symptoms of tuberculosis?", "TB: persistent cough (3+ weeks), coughing up blood, night sweats, fever, weight loss, fatigue, loss of appetite."),
    ("What are symptoms of lung cancer?", "Lung cancer: persistent cough, coughing up blood, chest pain, shortness of breath, unexplained weight loss, fatigue."),
    ("What are symptoms of pulmonary fibrosis?", "Pulmonary fibrosis: progressive shortness of breath, dry cough, fatigue, finger clubbing."),
    ("What are symptoms of pleurisy?", "Pleurisy: sharp chest pain worse with breathing, shortness of breath, cough, fever."),
    ("What are symptoms of sarcoidosis?", "Sarcoidosis: cough, shortness of breath, fatigue, skin rashes, swollen lymph nodes, eye problems."),
    ("What are symptoms of sleep apnea?", "Sleep apnea: loud snoring, gasping during sleep, morning headaches, excessive daytime sleepiness, difficulty concentrating."),
    ("What are symptoms of asthma attack in children?", "Childhood asthma attack: wheezing, coughing, chest tightness, rapid breathing, retractions (skin pulling in around ribs/neck)."),
    ("What are symptoms of whooping cough?", "Whooping cough: severe coughing fits, whooping sound when breathing in, vomiting after coughing, exhaustion."),
    ("What are symptoms of bronchitis in children?", "Child bronchitis: cough, runny nose, congestion, low fever, wheezing, fatigue."),
    ("What are symptoms of croup?", "Croup: barking cough, stridor (noisy breathing), hoarseness, symptoms worse at night."),
    ("What are symptoms of pneumonia in elderly?", "Elderly pneumonia: confusion, weakness, falls, low appetite, less fever than younger patients."),
    ("What are symptoms of chronic bronchitis?", "Chronic bronchitis: daily productive cough for 3+ months, mucus production, shortness of breath."),
    ("What are symptoms of emphysema?", "Emphysema: progressive shortness of breath, barrel chest, chronic cough, weight loss."),
    ("What are symptoms of bronchiectasis?", "Bronchiectasis: chronic productive cough, frequent lung infections, shortness of breath, fatigue, coughing up blood."),
    ("What are symptoms of respiratory failure?", "Respiratory failure: severe shortness of breath, bluish skin, confusion, rapid breathing. EMERGENCY."),
]
for q, a in respiratory:
    data.append({'question': q, 'answer': a, 'source': 'respiratory'})

# 3. DIGESTIVE (20)
digestive = [
    ("What are symptoms of gastritis?", "Gastritis: upper abdominal pain/burning, nausea, vomiting, feeling full after eating small amount."),
    ("What are symptoms of GERD?", "GERD: heartburn, acid regurgitation, chronic cough, difficulty swallowing, feeling of lump in throat."),
    ("What are symptoms of gallstones?", "Gallstones: sudden severe upper right abdomen pain, pain between shoulder blades, nausea/vomiting, jaundice."),
    ("What are symptoms of appendicitis?", "Appendicitis: pain starting around navel moving to lower right abdomen, loss of appetite, nausea/vomiting, fever."),
    ("What are symptoms of IBS?", "IBS: abdominal pain, bloating, gas, diarrhea or constipation (or alternating), mucus in stool."),
    ("What are symptoms of Crohn disease?", "Crohn disease: persistent diarrhea, abdominal pain, fatigue, weight loss, blood in stool, reduced appetite."),
    ("What are symptoms of ulcerative colitis?", "Ulcerative colitis: bloody diarrhea, rectal pain/bleeding, urgency to defecate, abdominal pain, weight loss."),
    ("What are symptoms of hepatitis?", "Hepatitis: fatigue, nausea, abdominal pain, jaundice (yellow skin/eyes), dark urine, loss of appetite."),
    ("What are symptoms of cirrhosis?", "Cirrhosis: fatigue, weakness, easy bruising, jaundice, abdominal swelling, confusion."),
    ("What are symptoms of pancreatitis?", "Pancreatitis: severe upper abdominal pain radiating to back, nausea, vomiting, fever, rapid pulse."),
    ("What are symptoms of ulcers?", "Stomach ulcer: burning stomach pain, feeling full, nausea, heartburn. Pain may improve with eating."),
    ("What are symptoms of food poisoning?", "Food poisoning: nausea, vomiting, diarrhea, abdominal cramps, fever. Usually resolves in 24-48 hours."),
    ("What are symptoms of constipation?", "Constipation: fewer than 3 bowel movements per week, hard/dry stools, straining, incomplete evacuation."),
    ("What are symptoms of diarrhea?", "Diarrhea: loose/watery stools, abdominal cramps, urgency, bloating, nausea."),
    ("What are symptoms of celiac disease?", "Celiac disease: diarrhea, bloating, gas, fatigue, weight loss, anemia, skin rash (dermatitis herpetiformis)."),
    ("What are symptoms of lactose intolerance?", "Lactose intolerance: bloating, diarrhea, gas, stomach cramps after consuming dairy. Not dangerous."),
    ("What are symptoms of colon cancer?", "Colon cancer: change in bowel habits, blood in stool, unexplained weight loss, fatigue, persistent abdominal discomfort."),
    ("What are symptoms of hemorrhoids?", "Hemorrhoids: itching/pain around anus, bleeding during bowel movements, swollen lumps near anus."),
    ("What are symptoms of acid reflux in infants?", "Infant GERD: vomiting, fussiness during feeding, refusal to eat, poor weight gain, breathing problems."),
    ("What are symptoms of liver failure?", "Liver failure: jaundice, confusion, bleeding, swollen abdomen, coma. EMERGENCY."),
]
for q, a in digestive:
    data.append({'question': q, 'answer': a, 'source': 'digestive'})

# 4. NEUROLOGICAL (15)
neurological = [
    ("What are symptoms of migraine?", "Migraine: intense throbbing one-sided headache, nausea, light/sound sensitivity, visual aura. Rest in dark room."),
    ("What are symptoms of meningitis?", "Meningitis: severe headache, stiff neck, high fever, confusion, vomiting, rash. MEDICAL EMERGENCY."),
    ("What are symptoms of concussion?", "Concussion: headache, dizziness, nausea, confusion, memory problems, sensitivity to light/noise. Seek care."),
    ("What are symptoms of Parkinson disease?", "Parkinson: tremors (shaking), slow movement, rigid muscles, impaired balance, changes in speech/writing."),
    ("What are symptoms of MS?", "MS: vision problems, tingling/numbness, weakness, fatigue, dizziness, pain, cognitive changes."),
    ("What are symptoms of epilepsy?", "Epilepsy: seizures (uncontrolled shaking), loss of consciousness, confusion, temporary confusion."),
    ("What are symptoms of stroke?", "Stroke (BE FAST): Balance loss, Eyes vision changes, Face drooping, Arm weakness, Speech difficulty, Time = call 115."),
    ("What are symptoms of Alzheimer?", "Alzheimer: memory loss, difficulty completing familiar tasks, confusion with time/place, trouble with images."),
    ("What are symptoms of brain tumor?", "Brain tumor: persistent headaches, seizures, nausea/vomiting, vision problems, personality changes, difficulty with speech."),
    ("What are symptoms of ALS?", "ALS: muscle twitches, muscle weakness, difficulty speaking, difficulty swallowing, fatigue."),
    ("What are symptoms of neuropathy?", "Neuropathy: numbness/tingling in hands/feet, burning pain, muscle weakness, sensitivity to touch."),
    ("What are symptoms of restless leg syndrome?", "RLS: irresistible urge to move legs, uncomfortable sensations worse at rest, improves with movement."),
    ("What are symptoms of vertigo?", "Vertigo: spinning sensation, nausea, vomiting, balance problems. Can be from inner ear (BPPV) or other causes."),
    ("What are symptoms of tension headache?", "Tension headache: dull ache, pressure on forehead/sides, tender scalp/neck/shoulder muscles."),
    ("What are symptoms of cluster headache?", "Cluster headache: severe one-sided pain around eye, red/watery eye, nasal congestion. Short but extremely painful."),
]
for q, a in neurological:
    data.append({'question': q, 'answer': a, 'source': 'neurological'})

# 5. MENTAL HEALTH (15)
mental = [
    ("What are symptoms of clinical depression?", "Depression: persistent sadness, loss of interest, appetite/weight changes, sleep changes, fatigue, guilt, difficulty concentrating."),
    ("What are symptoms of anxiety disorder?", "Anxiety: excessive worry, restlessness, muscle tension, sleep problems, difficulty concentrating, irritability."),
    ("What are symptoms of bipolar disorder?", "Bipolar: alternating mania (elevated mood) and depression. Episodes last days to weeks. Needs psychiatric care."),
    ("What are symptoms of OCD?", "OCD: intrusive thoughts causing anxiety, repetitive behaviors to reduce anxiety. Interferes with daily life."),
    ("What are symptoms of PTSD?", "PTSD: intrusive memories, avoidance, negative mood changes, hyperarousal after trauma. Professional help needed."),
    ("What are symptoms of social anxiety?", "Social anxiety: fear of judgment, avoidance of social situations, rapid heartbeat, sweating, shaking in social settings."),
    ("What are symptoms of panic disorder?", "Panic disorder: sudden intense fear with racing heart, sweating, trembling, shortness of breath, sense of doom."),
    ("What are symptoms of eating disorder?", "Eating disorders: obsession with weight/food, skipping meals, excessive exercise, vomiting after eating, withdrawn behavior."),
    ("What are symptoms of ADHD in adults?", "Adult ADHD: difficulty focusing, restlessness, disorganization, forgetfulness, impulsivity, mood swings."),
    ("What are symptoms of personality disorder?", "Personality disorders: rigid patterns of thinking/behaving, difficulty relating to others, problems at work/in relationships."),
    ("What are symptoms of schizophrenia?", "Schizophrenia: hallucinations, delusions, disorganized thinking, reduced emotional expression, social withdrawal."),
    ("What are symptoms of postpartum depression?", "Postpartum depression: intense sadness, anxiety, exhaustion after childbirth, difficulty bonding with baby."),
    ("What are symptoms of seasonal affective disorder?", "SAD: low energy, oversleeping, weight gain, irritability, difficulty concentrating during winter months."),
    ("What are symptoms of burnout?", "Burnout: chronic stress exhaustion, feeling drained, reduced accomplishment, cynicism about work."),
    ("What are symptoms of grief vs depression?", "Grief: waves of sadness, centered on loss. Depression: persistent sadness, anhedonia, global impairment."),
]
for q, a in mental:
    data.append({'question': q, 'answer': a, 'source': 'mental_health'})

# 6. TREATMENTS (15)
treatments = [
    ("How is hypertension treated?", "Hypertension treatment: lifestyle (low salt, exercise, weight loss, limit alcohol), medications (diuretics, ACE inhibitors, ARBs)."),
    ("How is type 2 diabetes treated?", "Type 2 diabetes: lifestyle changes, oral meds (metformin first-line), insulin if needed, regular blood sugar monitoring."),
    ("How is asthma treated?", "Asthma: controller inhalers (ICS) daily, rescue inhalers (SABA) as needed, action plan, trigger avoidance."),
    ("How is depression treated?", "Depression: psychotherapy (CBT), antidepressants (SSRIs/SNRIs), lifestyle changes. Combination often most effective."),
    ("How is bacterial pneumonia treated?", "Pneumonia: antibiotics, rest, fluids. Hospitalization may be needed. Recovery 1-3 weeks."),
    ("How is COPD treated?", "COPD: bronchodilators (short and long-acting), inhaled corticosteroids, pulmonary rehab, oxygen therapy."),
    ("How is heart failure treated?", "Heart failure: lifestyle changes, medications (diuretics, ACE inhibitors, beta-blockers, MRAs), devices, transplant."),
    ("How is thyroid disease treated?", "Thyroid: hyperthyroidism - medications/radioiodine/surgery. Hypothyroidism - levothyroxine daily."),
    ("How is arthritis treated?", "Arthritis: medications (NSAIDs, DMARDs), physical therapy, exercise, weight loss, joint replacement surgery."),
    ("How is back pain treated?", "Back pain: heat/ice, NSAIDs, physical therapy, exercise, posture correction. Surgery rarely needed."),
    ("How is insomnia treated?", "Insomnia: sleep hygiene, cognitive behavioral therapy, medications (short-term). Address underlying causes."),
    ("How is anxiety treated?", "Anxiety: therapy (CBT), medications (SSRIs, benzodiazepines short-term), lifestyle changes, relaxation techniques."),
    ("How is acid reflux treated?", "GERD: lifestyle changes, avoid trigger foods, lose weight, elevate head of bed. Medications: PPIs, H2 blockers."),
    ("How is cholesterol treated?", "High cholesterol: diet changes, exercise, statins. Goal depends on risk factors."),
    ("How is chronic pain treated?", "Chronic pain: multimodal approach - medications, physical therapy, psychological support, lifestyle changes."),
]
for q, a in treatments:
    data.append({'question': q, 'answer': a, 'source': 'treatment'})

# 7. MEDICATIONS (10)
medications = [
    ("What are side effects of ibuprofen?", "Ibuprofen side effects: stomach upset, heartburn, headache, dizziness. Serious: bleeding, kidney problems. Take with food."),
    ("What are interactions with metformin?", "Metformin interactions: contrast dyes (stop temporarily), alcohol (avoid excess). Generally safe with other meds."),
    ("Can I take aspirin with blood thinners?", "Aspirin + blood thinners: increased bleeding risk. Consult doctor. May be recommended for some cardiac patients."),
    ("What are side effects of statins?", "Statin side effects: muscle pain (most common), headache, digestive issues. Report muscle symptoms. Benefits > risks."),
    ("What are common drug interactions?", "Major interactions: Warfarin+NSAIDs (bleeding), ACEi+potassium (high K), antibiotics+birth control (reduced effect)."),
    ("What are side effects of antibiotics?", "Antibiotic side effects: nausea, diarrhea, yeast infections, allergic reactions. Antibiotic resistance with overuse."),
    ("What are side effects of birth control pills?", "Birth control side effects: nausea, breast tenderness, mood changes, breakthrough bleeding. Usually improve over time."),
    ("What are interactions with warfarin?", "Warfarin interactions: many drugs, foods high in vitamin K affect INR. Regular monitoring essential."),
    ("What are side effects of corticosteroids?", "Steroid side effects: weight gain, mood changes, insomnia, increased appetite. Long-term: bone loss, diabetes risk."),
    ("What are side effects of antidepressants?", "Antidepressant side effects: nausea, weight changes, sexual problems, drowsiness, dry mouth. Usually improve in weeks."),
]
for q, a in medications:
    data.append({'question': q, 'answer': a, 'source': 'medication'})

# 8. EMERGENCY (10)
emergencies = [
    ("What are signs of stroke?", "Stroke (BE FAST): Balance loss, Eyes vision changes, Face drooping, Arm weakness, Speech difficulty, Time - call 115."),
    ("What to do for severe allergic reaction?", "Anaphylaxis: call 115, use epinephrine, lie down with legs elevated, second reaction can occur hours later."),
    ("What to do for heat stroke?", "Heat stroke: call 115, move to cool area, cool rapidly with cold water, do NOT give fluids. Life-threatening."),
    ("What to do for seizures?", "Seizure: protect from injury, do not restrain, turn on side, time the seizure. Call 115 if >5 minutes."),
    ("What to do for heart attack?", "Heart attack: call 115, chew aspirin if not allergic, sit/lie down, wait for ambulance. Every minute counts."),
    ("What to do for severe bleeding?", "Bleeding control: apply direct pressure, elevate, do not remove objects, call 115 for severe bleeding."),
    ("What to do for choking?", "Choking: back blows, Heimlich maneuver (abdominal thrusts), repeat, call 115 if not dislodged."),
    ("What to do for burns?", "Burns: cool 10-20 minutes, do not apply ice/butter, cover with clean bandage, seek medical help for severe burns."),
    ("What to do for drowning?", "Drowning: remove from water, call 115, begin CPR if not breathing, keep warm until help arrives."),
    ("What to do for poisoning?", "Poisoning: call poison control, do not induce vomiting unless told, save container."),
]
for q, a in emergencies:
    data.append({'question': q, 'answer': a, 'source': 'emergency'})

# 9. PREVENTION (10)
prevention = [
    ("How to prevent heart disease?", "Heart disease prevention: no smoking, healthy diet, exercise 150 min/week, healthy weight, limit alcohol, manage stress."),
    ("How to prevent diabetes?", "Diabetes prevention: healthy weight, regular exercise, whole grains/fiber, limit sugar/refined carbs, no smoking."),
    ("How to prevent cancer?", "Cancer prevention: no smoking, limit alcohol, vegetables/fruits, healthy weight, exercise, sun protection, screenings."),
    ("How to prevent strokes?", "Stroke prevention: control BP, no smoking, treat AFib, exercise, healthy diet, limit alcohol. Blood thinners if prescribed."),
    ("How to prevent flu?", "Flu prevention: annual vaccine, hand washing, avoid sick people, do not touch face, healthy lifestyle."),
    ("How to prevent pneumonia?", "Pneumonia prevention: flu vaccine, pneumococcal vaccine, good hygiene, quit smoking, manage chronic conditions."),
    ("How to prevent osteoporosis?", "Osteoporosis prevention: adequate calcium/vitamin D, weight-bearing exercise, no smoking, limit alcohol."),
    ("How to prevent depression?", "Depression prevention: regular exercise, sleep, social connections, stress management, seek help early."),
    ("How to prevent Alzheimer?", "Alzheimer prevention: exercise, healthy diet, social engagement, mental stimulation, control cardiovascular risk factors."),
    ("How to prevent infections?", "Infection prevention: hand washing, vaccines, safe food/water, protected sex, avoid sharing items."),
]
for q, a in prevention:
    data.append({'question': q, 'answer': a, 'source': 'prevention'})

# 10. GENERAL HEALTH (10)
general = [
    ("What is a healthy diet?", "Healthy diet: vegetables, fruits, whole grains, lean proteins, healthy fats. Limit: processed foods, added sugars, sodium."),
    ("How much exercise is recommended?", "Exercise: 150 min moderate or 75 min vigorous weekly, plus muscle strengthening 2+ days/week."),
    ("What are normal vital signs?", "Normal vitals: BP <120/80, HR 60-100, Temp 97-99F, Resp rate 12-20."),
    ("What is a healthy BMI?", "BMI: Underweight <18.5, Normal 18.5-24.9, Overweight 25-29.9, Obese 30+."),
    ("How much water should I drink?", "Water: men ~3.7L daily, women ~2.7L. Includes water from food. Adjust for exercise, weather."),
    ("How much sleep do I need?", "Sleep: adults 7-9 hours, teens 8-10, children 9-11. Quality matters. Consistent schedule helps."),
    ("What are warning signs of cancer?", "Cancer warning signs: unexplained weight loss, fever, fatigue, pain, changes in bowel/bladder, lumps, bleeding."),
    ("When should I see a doctor?", "See doctor: persistent symptoms, unexplained changes, preventive care, screenings based on age/risk."),
    ("What are preventive health screenings?", "Screenings: blood pressure, cholesterol, diabetes, cancer (breast, colon, cervical, prostate), bone density."),
    ("How do I check my own health?", "Self-check: weight, BP, heart rate, skin changes, breast/testicle exams, dental checkups."),
]
for q, a in general:
    data.append({'question': q, 'answer': a, 'source': 'general'})

print(f"Total: {len(data)} samples")

# Add disclaimer
for item in data:
    if 'disclaimer' not in item['answer'].lower():
        item['answer'] += "\n\n⚠️ Disclaimer: This is a preliminary suggestion, not a substitute for medical advice."

# Save
output_path = "C:/NDT/PJ/MediSign_AI/data/training_raw/full_medical_en.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Saved to: {output_path}")
