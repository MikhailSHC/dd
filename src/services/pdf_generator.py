import os
import traceback
import pymupdf as pm
from pathlib import Path
from docx import Document

from src.models.constants import style_css, correct_form_in_class, coordinates


def fill_curr(num, val, kk, datas, doc):
    val[0][0], val[0][1], val[0][2], val[0][3] = (
        val[0][0] + coordinates[num][kk][0],
        val[0][1] + coordinates[num][kk][1],
        val[0][2] + coordinates[num][kk][2],
        val[0][3] + coordinates[num][kk][3],
    )

    if num == 4:
        doc[num].add_redact_annot(val[0], fill=(0.7019, 0.8980, 0.6314))
    else:
        doc[num].add_redact_annot(val[0], fill=(1, 1, 1))

    doc[num].apply_redactions()

    css_text = (
        f".abx {{font-size: {style_css[num][kk]['size']} !important; "
        f"font-weight: {style_css[num][kk]['weight']}; "
        f"text-align: {style_css[num][kk]['align']}; "
        f"font-family: {style_css[num][kk]['family']}; "
        f"padding: {style_css[num][kk]['padding']}; "
        f"margin: {style_css[num][kk]['margin']};}}"
    )

    regen = doc[num].insert_htmlbox(
        val[0],
        f'{correct_form_in_class[num][kk]}<i>{datas[kk]}</i></div>',
        css=css_text
    )
    return regen


def change_coordinates(dict_with_coor, datas, doc):
    for key, value in dict_with_coor.items():
        for sub_key, val in value.items():
            fill_curr(key, val, sub_key, datas, doc)
        datas["УДОСТОВЕРЕНИЕ №"] = str(int(datas["УДОСТОВЕРЕНИЕ №"]) + 1)


def find_coor(args_in_dict, doc):
    for key, value in args_in_dict.items():
        for kk, val in value.items():
            args_in_dict[key][kk] = doc[key].search_for(val)
    return args_in_dict


def change_dt(dict_with_data, doc):
    for order in range(5):
        dict_with_data.setdefault(order, {})
        page = doc[order]
        lst_with_datas = page.get_text().strip().split('\n')

        for val_datas in lst_with_datas:
            if 'Выдано' in val_datas:
                val_datas = val_datas.split()
                coor = ' '.join(val_datas[1:])
                dict_with_data[order].setdefault("Выдано", coor)
            elif 'УДОСТОВЕРЕНИЕ №' in val_datas:
                val_datas = val_datas.split()
                coor = ' '.join(val_datas[2:])
                dict_with_data[order].setdefault("УДОСТОВЕРЕНИЕ №", coor)
            elif 'Место работы:' in val_datas:
                val_datas = val_datas.split()
                coor = ' '.join(val_datas[2:])
                dict_with_data[order].setdefault("Место работы", coor)
            elif 'Должность' in val_datas:
                val_datas = val_datas.split()
                coor = ' '.join(val_datas[1:])
                dict_with_data[order].setdefault("Должность", coor)
            elif "Протокол заседания комиссии №" in val_datas:
                val_datas = val_datas.split()
                coor = val_datas[4]
                dict_with_data[order].setdefault("Протокол заседания комиссии №", coor)
                coor = " ".join(val_datas[6:])
                dict_with_data[order].setdefault("Дата", coor)
            elif "Протокол №" in val_datas:
                val_datas = val_datas.split()
                coor = val_datas[2]
                dict_with_data[order].setdefault("Протокол №", coor)
                coor = " ".join(val_datas[4:])
                dict_with_data[order].setdefault("Дата", coor)

    return dict_with_data


def get_template_path():
    if os.path.exists("Main_data.pdf"):
        return "Main_data.pdf"

    base_dir = Path(__file__).parent.parent.parent
    template_path = base_dir / "Main_data.pdf"
    if os.path.exists(template_path):
        return str(template_path)

    return "Main_data.pdf"


def generate_blanks(user_data, amount_blanks, output_filename="generated_blanks.pdf"):
    datas = {
        'Выдано': user_data['Выдано'],
        'Место работы': user_data['Место работы'],
        'Должность': user_data['Должность'],
        'УДОСТОВЕРЕНИЕ №': user_data['Удост_№'],
        'Протокол заседания комиссии №': user_data['ПРТ_№'],
        'Протокол №': user_data['ПРТ_№'],
        "Дата": user_data['Дата']
    }

    try:
        template_path = get_template_path()

        if not os.path.exists(template_path):
            print(f"Файл шаблона '{template_path}' не найден!")
            print(f"Текущая директория: {os.getcwd()}")
            print(f"Искали в: {template_path}")
            raise FileNotFoundError("Файл шаблона 'Main_data.pdf' не найден!")

        doc = pm.open(template_path)

        dict_change = {}
        dict_with_datas = change_dt(dict_change, doc)
        find_coor(dict_with_datas, doc)
        change_coordinates(dict_with_datas, datas, doc)

        doc_step2 = pm.open()

        margin_on_button = -410
        margin_off_button = 630
        cnt = 0

        for grade, num in amount_blanks.items():
            if grade == "А":
                page_doc = doc[0]
            elif grade == "Б":
                page_doc = doc[1]
            elif grade == "В":
                page_doc = doc[2]
            elif grade == "ПП":
                page_doc = doc[3]
            elif grade == "СИЗ":   # ОТ -> СИЗ
                page_doc = doc[4]
            else:
                continue

            for _ in range(num):
                if cnt % 4 == 0:
                    margin_on_button = -410
                    margin_off_button = 630
                    new_page_step2 = doc_step2.new_page(width=595, height=842)

                page_doc_data = page_doc.get_text("dict")['blocks']
                min_x, min_y = float('inf'), float('inf')
                max_x, max_y = float('-inf'), float('-inf')

                for block in page_doc_data:
                    bbox = block['bbox']
                    min_x = min(min_x, bbox[0])
                    min_y = min(min_y, bbox[1])
                    max_x = max(max_x, bbox[2])
                    max_y = max(max_y, bbox[3])

                correct_form = pm.Rect(
                    min_x - 90,
                    min_y - 1,
                    max_x + 50,
                    max_y - 22,
                )

                top_position_on_page = pm.Rect(
                    0,
                    margin_on_button,
                    600,
                    margin_off_button
                )
                cnt += 1

                matrix = pm.Matrix(3.0, 3.0)
                pix = page_doc.get_pixmap(clip=correct_form, matrix=matrix)
                new_page_step2.insert_image(top_position_on_page, pixmap=pix)
                margin_on_button += 295
                margin_off_button += 125

        # ---- защита от “пустого PDF” ----
        if doc_step2.page_count == 0:
            doc.close()
            doc_step2.close()
            raise ValueError("Не выбрано ни одного PDF-бланка (А/Б/В/ПП/СИЗ).")

        doc_step2.save(
            output_filename,
            garbage=4,
            deflate=True,
            clean=True,
            incremental=False
        )
        doc.close()
        doc_step2.close()

        return output_filename

    except Exception as e:
        print(f"Ошибка в generate_blanks: {str(e)}")
        print(traceback.format_exc())
        raise
