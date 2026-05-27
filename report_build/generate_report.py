# -*- coding: utf-8 -*-
"""Main script - assemble the final report."""
import sys
sys.path.insert(0, r"C:\NDT\PJ\MediSign_AI - Copy\report_build")

from report_helpers import *
import content_part1 as p1
import content_part2 as p2
import content_part3 as p3
import content_part4 as p4
import content_part5 as p5
import content_extension as ext
import content_extension2 as ext2

OUT = Path(r"C:\NDT\PJ\MediSign_AI - Copy") / "BaoCao_NCKH_MediSignAI_NguyenDuyThuan_2311555799.docx"


def main():
    doc = Document()
    style_default(doc)

    section = doc.sections[0]
    configure_section(section, page_num_format="lowerRoman")
    add_page_number(doc, section)

    p1.build_cover(doc)
    p1.build_inner_cover(doc)
    p1.build_acknowledgement(doc)
    p1.build_advisor_review(doc)
    p1.build_abstract(doc)
    p1.build_toc(doc)
    p1.build_abbreviations(doc)
    p1.build_list_of_tables(doc)
    p1.build_list_of_figures(doc)

    new_section = doc.add_section(WD_SECTION_START.NEW_PAGE)
    configure_section(new_section, page_num_format="decimal")
    new_section.header.is_linked_to_previous = False
    add_page_number(doc, new_section)

    p2.build_chapter_1(doc)
    ext.extend_chapter_1(doc)
    page_break(doc)

    p2.build_chapter_2(doc)
    ext.extend_chapter_2(doc)
    ext2.extend_chapter_2_more(doc)
    page_break(doc)

    p3.build_chapter_3(doc)
    ext.extend_chapter_3(doc)
    page_break(doc)

    p4.build_chapter_4(doc)
    ext.extend_chapter_4(doc)
    ext2.extend_chapter_4_cases(doc)
    page_break(doc)

    p5.build_chapter_5(doc)
    ext.extend_chapter_5(doc)
    page_break(doc)

    p5.build_references(doc)
    p5.build_appendices(doc)

    doc.save(OUT)
    size_kb = OUT.stat().st_size / 1024
    print(f"OK: saved {OUT} ({size_kb:,.0f} KB)")


if __name__ == "__main__":
    main()
