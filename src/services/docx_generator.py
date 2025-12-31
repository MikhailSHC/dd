import os
import tempfile
import time
import traceback
from docx import Document
from docx.shared import Inches, Pt
import pathlib


def replace_in_runs(paragraph, datas):
    """Заменяет плейсхолдеры в параграфе, сохраняя форматирование."""
    full_text = "".join(run.text for run in paragraph.runs)
    if not full_text or not any(ph in full_text for ph in datas):
        return

    for ph, val in datas.items():
        full_text = full_text.replace(ph, str(val))

    runs = paragraph.runs
    text_pos = 0
    for run in runs:
        length = len(run.text)
        run.text = full_text[text_pos:text_pos + length]
        text_pos += length

    if text_pos < len(full_text) and runs:
        runs[-1].text += full_text[text_pos:]


def get_template_path_docx():
    """Находит путь к шаблону DOCX."""
    possible_paths = [
        "test.docx",
        "../test.docx",
        "./test.docx",
    ]

    base_dir = pathlib.Path(__file__).parent.parent.parent
    possible_paths.extend([
        str(base_dir / "test.docx"),
        str(base_dir / "src" / "test.docx"),
    ])

    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Найден шаблон DOCX: {path}")
            return path

    print("❌ Файл test.docx не найден!")
    return None


def fill_docx_template(dt):
    """
    БЛАНКИ ДРУГ ЗА ДРУГОМ БЕЗ ОТСТУПОВ:
    - Новый документ
    - Копируем только нужные таблицы
    - 0 отступов между ними
    """
    print("\n" + "=" * 60)
    print("🚀 БЛАНКИ ДРУГ ЗА ДРУГОМ (0 ОТСТУПОВ)")
    print("=" * 60)

    if not dt:
        print("❌ Ошибка: dt пустой")
        return None

    try:
        # Данные пользователя
        full_name = dt.get('Выдано', '')
        name_parts = full_name.split() if full_name else []

        PLACEHOLDERS = {
            "{blank_№}": str(dt.get('Удост_№', '')),
            "{surname}": name_parts[0] if len(name_parts) > 0 else '',
            "{name}": name_parts[1] if len(name_parts) > 1 else '',
            "{father_name}": name_parts[2] if len(name_parts) > 2 else '',
            "{work_feat}": dt.get("Должность", ""),
            "{organization_name}": dt.get('Место работы', ''),
            "{protocol_№}": str(dt.get('ПРТ_№', '')),
            "{data}": dt.get('Дата', ''),
            "{data_start}": "12.10.2025",
            "{data_end}": "12.10.2028",
        }

        print(f"📊 Данные: {PLACEHOLDERS}")

        template_path = get_template_path_docx()
        if not template_path:
            return None

        # 1. Загружаем шаблон только для чтения
        template_doc = Document(template_path)
        blanks_count = dt.get('blanks_count', {})

        # Карта бланков -> индексы
        table_mapping = {'С1': 0, 'С2': 1, 'С3': 2, 'Т1': 3, 'Т2': 4, 'Т3': 5}
        needed_tables = [table_mapping[blank] for blank in blanks_count
                         if blank in table_mapping and blanks_count[blank] > 0]

        print(f"📋 Нужные таблицы: {needed_tables}")
        if not needed_tables:
            return None

        # 2. СОЗДАЁМ НОВЫЙ ДОКУМЕНТ С МИНИМАЛЬНЫМИ ПОЛЯМИ
        new_doc = Document()
        section = new_doc.sections[0]
        section.top_margin = Inches(0.1)  # 2.5мм
        section.bottom_margin = Inches(0.1)  # 2.5мм
        section.left_margin = Inches(0.2)  # 5мм
        section.right_margin = Inches(0.2)  # 5мм

        # Группы по безопасности
        group_map = {0: "1 (первая)", 1: "2 (вторая)", 2: "3 (третья)",
                     3: "1 (первая)", 4: "2 (вторая)", 5: "3 (третья)"}

        # 3. КОПИРУЕМ ТОЛЬКО НУЖНЫЕ ТАБЛИЦЫ БЕЗ ОТСТУПОВ
        for i, orig_index in enumerate(needed_tables):
            source_table = template_doc.tables[orig_index]

            # ✅ 0 ОТСТУП ПЕРЕД ПЕРВОЙ ТАБЛИЦЕЙ
            if i == 0:
                spacer = new_doc.add_paragraph()
                spacer.paragraph_format.space_before = Pt(0)
                spacer.paragraph_format.space_after = Pt(0)

            # ✅ 6pt ОТСТУП МЕЖДУ ТАБЛИЦАМИ (МИНИМУМ)
            else:
                spacer = new_doc.add_paragraph()
                spacer.paragraph_format.space_before = Pt(6)  # ~2мм
                spacer.paragraph_format.space_after = Pt(0)

            # Копируем таблицу ПОЛНОСТЬЮ
            table = new_doc.add_table(rows=len(source_table.rows), cols=len(source_table.columns))

            # Копируем ширину колонок
            for col_idx, source_col in enumerate(source_table.columns):
                table.columns[col_idx].width = source_col.width

            # Заменяем плейсхолдеры
            group_text = group_map.get(orig_index, "2 (вторая)")
            current_placeholders = PLACEHOLDERS.copy()
            current_placeholders["{rang_group}"] = group_text

            for row_idx, row in enumerate(source_table.rows):
                for col_idx, cell in enumerate(row.cells):
                    target_cell = table.cell(row_idx, col_idx)

                    # Копируем ВСЕ параграфы с форматированием
                    for source_para in cell.paragraphs:
                        target_para = target_cell.add_paragraph()

                        # Копируем текст с заменой плейсхолдеров
                        replace_in_runs(target_para, current_placeholders)

            print(f"✅ Добавлена таблица {i + 1}/{len(needed_tables)} (индекс {orig_index})")

        # 4. СОХРАНЯЕМ СУПЕР-КОМПАКТНЫЙ ДОКУМЕНТ
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        output_filename = f"document_zero_space_{timestamp}.docx"
        output_path = os.path.join(temp_dir, output_filename)

        new_doc.save(output_path)

        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ СУПЕР-КОМПАКТНЫЙ: {output_path}")
            print(f"📄 {len(needed_tables)} бланков ДРУГ ЗА ДРУГОМ")
            print(f"💰 Поля: 0.1-0.2\", отступы: 6pt МАКСИМУМ")
            print("=" * 60)
            return output_path

    except Exception as e:
        print(f"💥 ОШИБКА: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return None
