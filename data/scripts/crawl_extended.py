# -*- coding: utf-8 -*-
"""Crawl mở rộng từ nhiều nguồn - Tránh trùng lặp."""
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

INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[[a-z]\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_drug_name(url):
    """Extract drug name from Wikipedia URL."""
    # Remove base URL and get slug
    name = url.replace("https://vi.wikipedia.org/wiki/", "")
    name = name.replace("_", " ")
    return name

# Extended drug list - more variations
DRUG_LIST = [
    # Pain/Fever
    "Paracetamol", "Ibuprofen", "Aspirin", "Naproxen", "Diclofenac", "Meloxicam",
    "Celecoxib", "Tramadol", "Codeine", "Morphine", "Pethidine",

    # Antibiotics
    "Amoxicillin", "Azithromycin", "Ciprofloxacin", "Metronidazole", "Tetracycline",
    "Doxycycline", "Clarithromycin", "Cefuroxime", "Cefaclor", "Cefotaxime",
    "Ceftriaxone", "Cefazolin", "Ampicillin", "Piperacillin", "Vancomycin",
    "Gentamicin", "Amikacin", "Streptomycin", "Rifampicin", "Isoniazid",
    "Ethambutol", "Pyrazinamide", "Levofloxacin", "Moxifloxacin",

    # GI
    "Omeprazole", "Pantoprazole", "Lansoprazole", "Esomeprazole", "Rabeprazole",
    "Domperidone", "Metoclopramide", "Ondansetron", "Granisetron", "Phloroglucinol",
    "Alverine", "Mebeverine", "Loperamide", "Smecta", "Bacillus_clausii",

    # Cardiovascular
    "Amlodipine", "Losartan", "Bisoprolol", "Atorvastatin", "Rosuvastatin",
    "Simvastatin", "Metoprolol", "Enalapril", "Lisinopril", "Perindopril",
    "Ramipril", "Captopril", "Nifedipine", "Diltiazem", "Verapamil",
    "Digoxin", "Warfarin", "Apixaban", "Rivaroxaban", "Clopidogrel",
    "Aspirin", "Heparin", "Furosemide", "Spironolactone", "Hydrochlorothiazide",

    # Diabetes
    "Metformin", "Gliclazide", "Glibenclamid", "Sitagliptin", "Empagliflozin",
    "Linagliptin", "Vildagliptin", "Repaglinide", "Acarbose", "Pioglitazone",

    # CNS
    "Diazepam", "Alprazolam", "Sertraline", "Fluoxetine", "Amitriptyline",
    "Duloxetine", "Pregabalin", "Carbamazepine", "Phenytoin", "Levetiracetam",
    "Valproic_acid", "Topiramate", "Zolpidem", "Phenobarbital", "Clonazepam",

    # Allergy
    "Cetirizine", "Loratadine", "Fexofenadine", "Hydroxyzine", "Chlorpheniramine",
    "Dexchlorpheniramine", "Loratadine", "Desloratadine",

    # Respiratory
    "Salbutamol", "Montelukast", "Fluticasone", "Budesonide", "Theophylline",
    "Ambroxol", "Acetylcysteine", "Carbocisteine", "Erdosteine",

    # Steroids
    "Prednisone", "Prednisolone", "Methylprednisolone", "Hydrocortisone",
    "Dexamethasone", "Betamethasone",

    # Other
    "Allopurinol", "Colchicine", "Sildenafil", "Tadalafil", "Finasteride",
    "Dutasteride", "Mebendazole", "Albendazole", "Praziquantel",

    # Vietnamese common drugs
    "Berberin", "Cảo", "Tamiflu", "Oseltamivir", "Aciclovir", "Valacyclovir",
    "Ribavirin", "Interferon", "Tetracycline", "Neomycin", "Polymyxin",
]

def crawl_wikipedia_extended():
    """Crawl extended drug list."""
    print("Crawling extended Wikipedia drug list...")

    base_url = "https://vi.wikipedia.org/wiki/"
    drugs = []
    errors = []
    seen = set()

    for i, drug in enumerate(DRUG_LIST):
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

            # Skip if too similar to existing
            title_lower = title.lower()
            skip = False
            for seen_title in seen:
                if title_lower in seen_title or seen_title in title_lower:
                    skip = True
                    break
            if skip:
                continue
            seen.add(title_lower)

            # Get content
            content = soup.select_one('#mw-content-text')
            if not content:
                continue

            paragraphs = content.select('p')
            full_text = ""

            for p in paragraphs[:8]:
                text = clean_text(p.get_text())
                if len(text) > 50:
                    full_text += text + " "

            if len(full_text) < 100:
                continue

            full_text = full_text[:800]

            # Create Q&A for each drug - multiple questions
            qa_list = [
                {
                    "question": f"{title} là thuốc gì? Công dụng và cách dùng?",
                    "answer": f"{full_text} {D}",
                    "source": "wikipedia_extended"
                },
                {
                    "question": f"Thuốc {title} có tác dụng phụ gì?",
                    "answer": f"Về tác dụng phụ của {title}: {full_text[:400]} {D}",
                    "source": "wikipedia_extended"
                },
                {
                    "question": f"Cách sử dụng {title} như thế nào? Liều lượng?",
                    "answer": f"Thông tin về cách dùng {title}: {full_text[:400]} {D}",
                    "source": "wikipedia_extended"
                },
            ]

            for qa in qa_list:
                drugs.append(qa)

            print(f"  ✓ {title} ({len(qa_list)} Q&A)")

            time.sleep(DELAY + random.random())

        except Exception as e:
            errors.append(f"{drug}: {str(e)[:30]}")

        if i > 0 and i % 20 == 0:
            print(f"  Progress: {i}/{len(DRUG_LIST)}")

    print(f"\nCrawled: {len(drugs)} Q&A from {len(DRUG_LIST)} drugs")
    if errors:
        print(f"Errors: {len(errors)}")

    return drugs

def crawl_disease_list():
    """Crawl diseases from Wikipedia."""
    print("\nCrawling disease list...")

    base_url = "https://vi.wikipedia.org/wiki/"

    diseases = [
        "Đái_tháo_đường_loại_2", "Đái_tháo_đường_loại_1", "Tiểu_đường",
        "Tăng_huyết_áp", "Nhồi_máu_cơ_tim", "Đột_quỵ",
        "Viêm_khớp", "Viêm_khớp_dạng_thấp", "Gout",
        "Viêm_gan_B", "Viêm_gan_C", "Xơ_gan",
        "Ung_thư_phổi", "Ung_thư_vú", "Ung_thư_gan",
        "Hen_suyễn", "Bệnh_phổi_tắc_nghẽn_mãn_tính",
        "Trầm_cảm", "Rối_loạn_lo_ân", "Rối_loạn_giấc_ngủ",
        "Viêm_loét_dạ_dày", "Trào_ngược_dạ_dày_thực_quản",
        "Viêm_tụy", "Viêm_ruột",
    ]

    result = []

    for disease in diseases:
        try:
            url = base_url + disease
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.select_one('#firstHeading')
            if not title:
                continue

            title = clean_text(title.get_text())

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

            result.append({
                "question": f"Bệnh {title} là gì? Triệu chứng và điều trị?",
                "answer": f"{full_text} {D}",
                "source": "wikipedia_diseases"
            })

            print(f"  ✓ {title}")
            time.sleep(DELAY)

        except Exception as e:
            pass

    print(f"Crawled: {len(result)} disease Q&A")
    return result

def main():
    print("=" * 60)
    print("CRAWL MỞ RỘNG - TRÁNH TRÙNG LẶP")
    print("=" * 60)

    all_data = []

    # Crawl drugs
    drugs = crawl_wikipedia_extended()
    all_data.extend(drugs)

    # Crawl diseases
    diseases = crawl_disease_list()
    all_data.extend(diseases)

    # Save
    if all_data:
        output_path = r"C:\NDT\PJ\MediSign_AI\data\training_raw\crawled_extended.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Saved {len(all_data)} records to: {output_path}")

if __name__ == "__main__":
    main()
