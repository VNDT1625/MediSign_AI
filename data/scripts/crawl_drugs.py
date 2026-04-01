# -*- coding: utf-8 -*-
"""Crawl dữ liệu thuốc từ Wikipedia tiếng Việt."""
import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
DELAY = 1.5
D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

def clean_text(text):
    """Làm sạch text."""
    if not text:
        return ""
    # Remove references like [1], [2]
    text = re.sub(r'\[\d+\]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def crawl_wikipedia_drugs():
    """Crawl danh sách thuốc từ Wikipedia."""
    print("Crawling Wikipedia...")

    base_url = "https://vi.wikipedia.org/wiki/"

    # Danh sách bài về thuốc/phân loại thuốc
    drug_pages = [
        # Thuốc giảm đau, hạ sốt
        "Paracetamol",
        "Ibuprofen",
        "Aspirin",
        "Naproxen",
        "Diclofenac",

        # Kháng sinh
        "Amoxicillin",
        "Azithromycin",
        "Ciprofloxacin",
        "Metronidazole",
        "Tetracycline",
        "Doxycycline",
        "Clarithromycin",
        "Cefuroxime",

        # Tiêu hóa
        "Omeprazole",
        "Pantoprazole",
        "Lansoprazole",
        "Domperidone",
        "Metoclopramide",
        "Esomeprazole",

        # Tim mạch
        "Amlodipine",
        "Losartan",
        "Bisoprolol",
        "Atorvastatin",
        "Rosuvastatin",
        "Simvastatin",
        "Metoprolol",
        "Enalapril",
        "Lisinopril",
        "Nifedipine",
        "Digoxin",
        "Warfarin",
        "Clopidogrel",
        "Aspirin",

        # Đái tháo đường
        "Metformin",
        "Gliclazide",
        "Glibenclamid",
        "Sitagliptin",
        "Empagliflozin",

        # Thần kinh
        "Diazepam",
        "Alprazolam",
        "Sertraline",
        "Fluoxetine",
        "Amitriptyline",
        "Duloxetine",
        "Pregabalin",
        "Carbamazepine",
        "Phenytoin",

        # Dị ứng
        "Cetirizine",
        "Loratadine",
        "Fexofenadine",
        "Hydroxyzine",
        "Chlorpheniramine",

        # Hô hấp
        "Salbutamol",
        "Montelukast",
        "Fluticasone",
        "Budesonide",
        "Theophylline",

        # Corticosteroid
        "Prednisone",
        "Prednisolone",
        "Methylprednisolone",
        "Hydrocortisone",

        # Other
        "Lithium_(dược_phẩm)",
        "Allopurinol",
        "Colchicine",
        "Sildenafil",
        "Tadalafil",
    ]

    drugs = []
    errors = []

    for i, page in enumerate(drug_pages):
        try:
            url = base_url + page
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                errors.append(f"{page}: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Get title
            title_elem = soup.select_one('#firstHeading')
            if not title_elem:
                errors.append(f"{page}: No title")
                continue

            title = clean_text(title_elem.get_text())

            # Get content
            content = soup.select_one('#mw-content-text')
            if not content:
                continue

            # Get first few paragraphs
            paragraphs = content.select('p')
            full_text = ""

            for p in paragraphs[:8]:
                text = clean_text(p.get_text())
                if len(text) > 50:  # Skip very short paragraphs
                    full_text += text + " "

            if len(full_text) < 100:
                errors.append(f"{page}: Too little content")
                continue

            # Limit text length
            full_text = full_text[:800]

            # Generate Q&A
            qa = {
                "question": f"{title} là thuốc gì? Công dụng và cách dùng?",
                "answer": f"{full_text} {D}",
                "source": "wikipedia"
            }
            drugs.append(qa)

            print(f"  ✓ {title}")

            time.sleep(DELAY + random.random())

        except Exception as e:
            errors.append(f"{page}: {str(e)[:50]}")

    print(f"\nCrawled: {len(drugs)} drugs")
    if errors:
        print(f"Errors: {len(errors)}")

    return drugs

def crawl_wikipedia_categories():
    """Crawl từ category pages."""
    print("\nCrawling Wikipedia categories...")

    base_url = "https://vi.wikipedia.org/wiki/Category:"

    categories = [
        "Dược_phẩm",
        "Thuốc",
        "Kháng_sinh",
        "Thuốc_kháng_viêm",
    ]

    # Chỉ crawl một số category chính
    # Category pages thường có cấu trúc phức tạp hơn
    return []

def main():
    print("=" * 60)
    print("CRAWL DỮ LIỆU THUỐC TỪ WIKIPEDIA")
    print("=" * 60)
    print()

    drugs = crawl_wikipedia_drugs()

    if drugs:
        # Save
        output_path = r"C:\NDT\PJ\MediSign_AI\data\training_raw\wikipedia_drugs.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(drugs, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Saved {len(drugs)} records to: {output_path}")
    else:
        print("\n✗ No data crawled")

if __name__ == "__main__":
    main()
