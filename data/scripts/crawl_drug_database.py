# -*- coding: utf-8 -*-
"""Crawl drug database from multiple sources to get 200-500 drugs."""
import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
DELAY = 1.5

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[[a-z]\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Comprehensive drug list - 500+ drugs
DRUG_COMPREHENSIVE = [
    # === GIẢM ĐAU, HẠ SỐT, KHÁNG VIÊM ===
    "Paracetamol", "Acetaminophen", "Ibuprofen", "Naproxen", "Diclofenac",
    "Meloxicam", "Celecoxib", "Etoricoxib", "Piroxicam", "Ketoprofen",
    "Aspirin", "Mefenamic_acid", "Tramadol", "Codeine", "Morphine",
    "Fentanyl", "Buprenorphine", "Oxycodone", "Hydrocodone", "Pethidine",

    # === KHÁNG SINH - PENICILLIN ===
    "Amoxicillin", "Ampicillin", "Piperacillin", "Cloxacillin", "Dicloxacillin",
    "Oxacillin", "Nafcillin", "Penicillin_G", "Penicillin_V",

    # === KHÁNG SINH - MACROLIDE ===
    "Azithromycin", "Clarithromycin", "Erythromycin", "Roxithromycin", "Josamycin",

    # === KHÁNG SINH - QUINOLONE ===
    "Ciprofloxacin", "Levofloxacin", "Moxifloxacin", "Ofloxacin", "Norloxacin",
    "Lomefloxacin", "Sparfloxacin",

    # === KHÁNG SINH - CEPHALOSPORIN ===
    "Cefuroxime", "Cefaclor", "Cefotaxime", "Ceftriaxone", "Cefazolin",
    "Cefepime", "Cefdinir", "Cefixime", "Ceftazidime", "Cefoperazone",

    # === KHÁNG SINH - KHÁC ===
    "Metronidazole", "Tinidazole", "Doxycycline", "Tetracycline", "Minocycline",
    "Gentamicin", "Amikacin", "Streptomycin", "Neomycin", "Polymyxin_B",
    "Rifampicin", "Isoniazid", "Ethambutol", "Pyrazinamide", "Ciprofloxacin",

    # === THUỐC TIÊU HÓA - PPI ===
    "Omeprazole", "Pantoprazole", "Lansoprazole", "Esomeprazole", "Rabeprazole",
    "Dexlansoprazole", "Vonoprazan",

    # === THUỐC TIÊU HÓA - KHÁC ===
    "Domperidone", "Metoclopramide", "Ondansetron", "Granisetron", "Palonosetron",
    "Phloroglucinol", "Alverine", "Mebeverine", "Loperamide", "Racecadotril",
    "Smecta", "Bacillus_clausii", "Saccharomyces_boulardii",
    "Lactulose", "Macrogol", "Glycerin", "Bisacodyl", "Sodium_picosulfate",

    # === TIM MẠCH - CHẸN KÊNH CALCI ===
    "Amlodipine", "Nifedipine", "Diltiazem", "Verapamil", "Felodipine",
    "Lercanidipine", "Nicardipine", "Clevidipine", "Isradipine",

    # === TIM MẠCH - ARB ===
    "Losartan", "Valsartan", "Irbesartan", "Candesartan", "Telmisartan",
    "Olmesartan", "Eprosartan",

    # === TIM MẠCH - ACEI ===
    "Enalapril", "Lisinopril", "Perindopril", "Ramipril", "Captopril",
    "Fosinopril", "Trandolapril", "Quinapril", "Benazepril",

    # === TIM MẠCH - BETA-BLOCKER ===
    "Metoprolol", "Bisoprolol", "Atenolol", "Carvedilol", "Propranolol",
    "Nebivolol", "Labetalol", "Esmolol", "Sotalol", "Pindolol",

    # === TIM MẠCH - STATIN ===
    "Atorvastatin", "Rosuvastatin", "Simvastatin", "Pitavastatin", "Fluvastatin",
    "Pravastatin",

    # === TIM MẠCH - KHÁC ===
    "Digoxin", "Amiodarone", "Flecainide", "Propafenone", "Sotalol",
    "Warfarin", "Apixaban", "Rivaroxaban", "Dabigatran", "Heparin",
    "Enoxaparin", "Clopidogrel", "Aspirin", "Dipyridamole",
    "Furosemide", "Spironolactone", "Hydrochlorothiazide", "Chlorthalidone",
    "Indapamide", "Torasemide", "Bumetanide",

    # === ĐÁI THÁO ĐƯỜNG ===
    "Metformin", "Gliclazide", "Glipizide", "Glibenclamide", "Glimepiride",
    "Sitagliptin", "Vildagliptin", "Linagliptin", "Saxagliptin",
    "Empagliflozin", "Dapagliflozin", "Canagliflozin",
    "Repaglinide", "Acarbose", "Miglitol", "Pioglitazone",
    "Insulin", "Lantus", "Novorapid", "Humalog", "Apidra",

    # === THẦN KINH - BENZODIAZEPINE ===
    "Diazepam", "Alprazolam", "Lorazepam", "Clonazepam", "Midazolam",
    "Nitrazepam", "Flurazepam", "Temazepam", "Zolpidem", "Zopiclone",

    # === THẦN KINH - CHỐNG TRẦM CẢM ===
    "Sertraline", "Fluoxetine", "Paroxetine", "Citalopram", "Escitalopram",
    "Venlafaxine", "Duloxetine", "Milnacipran", "Mirtazapine",
    "Amitriptyline", "Imipramine", "Clomipramine", "Doxepin",

    # === THẦN KINH - CHỐNG ĐỘNG KINH ===
    "Carbamazepine", "Phenytoin", "Valproic_acid", "Levetiracetam",
    "Topiramate", "Lamotrigine", "Gabapentin", "Pregabalin",
    "Phenobarbital", "Primidone", "Oxcarbazepine", "Lacosamide",

    # === THẦN KINH - KHÁC ===
    "Levodopa", "Pramipexole", "Ropinirole", "Selegiline", "Entacapone",
    "Trihexyphenidyl", "Bromocriptine", "Cabergoline",

    # === DỊ ỨNG ===
    "Cetirizine", "Loratadine", "Fexofenadine", "Desloratadine",
    "Hydroxyzine", "Chlorpheniramine", "Dexchlorpheniramine", "Diphenhydramine",
    "Promethazine", "Mebhydrolin", "Alimemazine",

    # === HÔ HẤP - GIÃN PHẾ QUẢN ===
    "Salbutamol", "Terbutaline", "Formoterol", "Salmeterol", "Indacaterol",
    "Vilanterol", "Olodaterol",

    # === HÔ HẤP - CORTICOID ===
    "Fluticasone", "Budesonide", "Beclomethasone", "Ciclesonide",
    "Mometasone", "Prednisone", "Prednisolone", "Methylprednisolone",
    "Hydrocortisone", "Dexamethasone", "Betamethasone",

    # === HÔ HẤP - KHÁC ===
    "Montelukast", "Zafirlukast", "Zileuton",
    "Theophylline", "Aminophylline",
    "Ambroxol", "Acetylcysteine", "Carbocisteine", "Erdosteine",
    "Bromhexine", "Dextromethorphan", "Pholcodine",

    # === CƠ XƯƠNG KHỚP ===
    "Allopurinol", "Febuxostat", "Colchicine", "Probenecid", "Sulfinpyrazone",
    "Methotrexate", "Leflunomide", "Sulfasalazine", "Hydroxychloroquine",
    "Adalimumab", "Etanercept", "Infliximab", "Rituximab", "Tocilizumab",

    # === MẮT ===
    "Timolol", "Latanoprost", "Bimatoprost", "Travoprost", "Dorzolamide",
    "Brinzolamide", "Cromolyn", "Olopatadine", "Ketotifen",

    # === DA LIỄU ===
    "Clindamycin", "Erythromycin", "Mupirocin", "Fusidic_acid",
    "Betamethasone", "Clobetasol", "Triamcinolone", "Hydrocortisone",
    "Tacrolimus", "Pimecrolimus", "Coal_tar", "Salicylic_acid",
    "Benzoyl_peroxide", "Adapalene", "Tretinoin", "Isotretinoin",

    # === THUỐC BỔ ===
    "Vitamin_C", "Vitamin_D", "Vitamin_E", "Vitamin_K", "Vitamin_A",
    "Vitamin_B1", "Vitamin_B6", "Vitamin_B12", "Folic_acid",
    "Iron", "Calcium", "Zinc", "Magnesium", "Potassium",

    # === THUỐC KHÁC ===
    "Sildenafil", "Tadalafil", "Vardenafil", "Avanafil",
    "Finasteride", "Dutasteride",
    "Mebendazole", "Albendazole", "Praziquantel", "Levamisole",
    "Aciclovir", "Valacyclovir", "Ganciclovir", "Ribavirin",
    "Oseltamivir", "Zanamivir", "Amantadine", "Remdesivir",
    "Methylene_blue", "Activated_charcoal",

    # === THUỐC VIỆT NAM PHỔ BIẾN ===
    "Berberin", "Cảo", "Tamiflu", "Tiffy", "Decolgen",
    "Panadol", "Efferalgan", "Hapacol", "Mebiphar", "Medi",
    "Tần_lai", "Bạc_hà", "Khuynh_diệp", "Húng_chanh", "Cỏ_mực",

    # === THUỐC TIÊM ===
    "Vaccine", "Immunoglobulin", "Anti_tetanus", "Anti_rabies",
]

def crawl_comprehensive():
    """Crawl comprehensive drug list from Wikipedia."""
    print("Crawling comprehensive drug database...")

    base_url = "https://vi.wikipedia.org/wiki/"
    drugs = []
    errors = []
    seen = set()

    for i, drug in enumerate(DRUG_COMPREHENSIVE):
        try:
            url = base_url + drug.replace(" ", "_")
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                errors.append(f"{drug}: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Get title
            title_elem = soup.select_one('#firstHeading')
            if not title_elem:
                continue

            title = clean_text(title_elem.get_text())

            # Skip duplicates
            title_lower = title.lower()
            if title_lower in seen:
                continue
            seen.add(title_lower)

            # Get content
            content = soup.select_one('#mw-content-text')
            if not content:
                continue

            paragraphs = content.select('p')
            full_text = ""
            for p in paragraphs[:6]:
                text = clean_text(p.get_text())
                if len(text) > 50:
                    full_text += text + " "

            if len(full_text) < 100:
                continue

            full_text = full_text[:600]

            drugs.append({
                "name": title,
                "description": full_text,
                "source": "wikipedia"
            })

            print(f"  ✓ {title}")

            if i > 0 and i % 50 == 0:
                print(f"  Progress: {i}/{len(DRUG_COMPREHENSIVE)}")

            time.sleep(DELAY + random.random())

        except Exception as e:
            errors.append(f"{drug}: {str(e)[:30]}")

    print(f"\nCrawled: {len(drugs)} drugs")
    if errors:
        print(f"Errors: {len(errors)}")

    return drugs

def main():
    print("=" * 60)
    print("CRAWL DRUG DATABASE - 200-500 DRUGS")
    print("=" * 60)

    drugs = crawl_comprehensive()

    if drugs:
        # Save raw
        output_raw = r"C:\NDT\PJ\MediSign_AI\data\training_raw\crawled_drugs_comprehensive.json"
        with open(output_raw, "w", encoding="utf-8") as f:
            json.dump(drugs, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Saved {len(drugs)} drugs to: {output_raw}")

if __name__ == "__main__":
    main()
