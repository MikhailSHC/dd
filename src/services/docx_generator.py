import os
import tempfile
import time
import traceback
import copy
import pathlib

from docx import Document
from docx.shared import Pt, Mm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def replace_in_runs(paragraph, datas):
    """Заменяет плейсхолдеры в параграфе, сохраняя форматирование (и не падает)."""
    if not datas or not isinstance(datas, dict):
        return
    if paragraph is None or not getattr(paragraph, "runs", None):
        return

    full_text = "".join((run.text or "") for run in paragraph.runs)
    if not full_text:
        return
    if not any(ph in full_text for ph in datas.keys()):
        return

    new_text = full_text
    for ph, val in datas.items():
        new_text = new_text.replace(ph, "" if val is None else str(val))

    runs = paragraph.runs
    text_pos = 0
    for run in runs:
        old_len = len(run.text or "")
        run.text = new_text[text_pos:text_pos + old_len]
        text_pos += old_len

    if runs and text_pos < len(new_text):
        runs[-1].text = (runs[-1].text or "") + new_text[text_pos:]


def get_template_path_docx():
    """Ищет test.docx независимо от cwd (как у тебя в main.txt)."""
    here = pathlib.Path(__file__).resolve().parent
    project_root = here.parent.parent  # .../src/services -> .../

    candidates = [
        pathlib.Path("test.docx"),            # cwd
        here / "test.docx",                   # рядом с файлом
        project_root / "test.docx",           # корень проекта
        project_root / "src" / "test.docx",   # запасной
    ]

    for p in candidates:
        if p.exists():
            print(f"✅ Найден шаблон DOCX: {p}")
            return str(p)

    print("❌ Файл test.docx не найден! Ищу в:")
    for p in candidates:
        print("   -", p)
    return None


def _clear_body_keep_sectpr(doc: Document):
    """
    Очищает тело документа, но оставляет sectPr (разметка страницы/поля),
    чтобы у результата были настройки шаблона.
    """
    body = doc.element.body
    sectpr = None
    for child in list(body):
        if child.tag.endswith("}sectPr"):
            sectpr = child
        body.remove(child)
    if sectpr is not None:
        body.append(sectpr)


def _one_empty_line(doc: Document, gap_mm: int = 3):
    """
    Надёжный отступ между бланками: не “пустая строка”, а space_after.
    Word это не схлопывает, в отличие от пустых абзацев. [file:118]
    """
    p = doc.add_paragraph("")
    pf = p.paragraph_format
    pf.space_before = 0
    pf.space_after = Mm(gap_mm)   # <-- вот он, реальный зазор
    pf.line_spacing = 1
    return p


def _anchor_paragraph(doc: Document):
    """Якорь перед таблицей — без добавочного вертикального зазора."""
    p = doc.add_paragraph("")
    pf = p.paragraph_format
    pf.space_before = 0
    pf.space_after = 0
    pf.line_spacing = 1
    return p


def _compact_paragraphs(doc: Document):
    """Прибивает интервалы у всех параграфов (уменьшает “пухлость”)."""
    for p in doc.paragraphs:
        pf = p.paragraph_format
        if pf is None:
            continue
        pf.space_before = 0
        pf.space_after = 0
        pf.line_spacing = 1
        for r in p.runs:
            if (r.text or "") == "":
                pass


def _table_to_inline(table):
    """Убираем признаки 'плавающего' поведения таблицы (если есть)."""
    tbl = table._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        return

    for child in list(tblPr):
        if child.tag in (qn("w:tblpPr"), qn("w:tblOverlap")):
            tblPr.remove(child)


def _set_tbl_fixed_layout(table):
    """Фиксированный layout таблицы — Word меньше “пересчитывает” ширины."""
    tbl = table._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        return

    tblLayout = tblPr.find(qn("w:tblLayout"))
    if tblLayout is None:
        tblLayout = OxmlElement("w:tblLayout")
        tblPr.append(tblLayout)
    tblLayout.set(qn("w:type"), "fixed")


def _shift_content_left_by_right_margin(doc: Document, mm: int = 7):
    """
    Сейчас у тебя поля уже норм, оставляем mm=0 в вызове.
    """
    for section in doc.sections:
        section.right_margin = section.right_margin + Mm(mm)


def _get_count(blanks_count: dict, *keys):
    """Поддержка С/Т (кириллица) и C/T (латиница)."""
    mx = 0
    for k in keys:
        try:
            mx = max(mx, int(blanks_count.get(k, 0) or 0))
        except Exception:
            pass
    return mx


def fill_docx_template(dt):
    print("\n" + "=" * 50)
    print("🚀 DOCX (MODE=COMPACT_INLINE + IMPROVEMENTS)")
    print("=" * 50)

    if not dt:
        print("❌ Ошибка: dt пустой")
        return None

    try:
        # --------- ДАННЫЕ ----------
        full_name = dt.get("Выдано", "")
        name_parts = full_name.split() if full_name else []

        placeholders_base = {
            "{blank_№}": str(dt.get("Удост_№", "")),
            "{surname}": name_parts[0] if len(name_parts) > 0 else "",
            "{name}": name_parts[1] if len(name_parts) > 1 else "",
            "{father_name}": name_parts[2] if len(name_parts) > 2 else "",
            "{work_feat}": dt.get("Должность", ""),
            "{organization_name}": dt.get("Место работы", ""),
            "{protocol_№}": str(dt.get("ПРТ_№", "")),
            "{data}": dt.get("Дата", ""),
            "{data_start}": "12.10.2025",
            "{data_end}": "12.10.2028",
        }

        blanks_count = dt.get("blanks_count", {}) or {}

        # --------- ПЛАН (индексы таблиц из test.docx) ----------
        # 0-С1, 1-С2, 2-С3, 3-Т1, 4-Т2, 5-Т3
        plan = []
        plan += [0] * _get_count(blanks_count, "С1", "C1")
        plan += [1] * _get_count(blanks_count, "С2", "C2")
        plan += [2] * _get_count(blanks_count, "С3", "C3")
        plan += [3] * _get_count(blanks_count, "Т1", "T1")
        plan += [4] * _get_count(blanks_count, "Т2", "T2")
        plan += [5] * _get_count(blanks_count, "Т3", "T3")

        print("📋 План:", plan)
        if not plan:
            print("ℹ️ Нет бланков для генерации")
            return None

        # --------- ШАБЛОН ----------
        template_path = get_template_path_docx()
        if not template_path:
            return None

        template_doc = Document(template_path)
        if len(template_doc.tables) < 6:
            print(f"❌ В шаблоне таблиц: {len(template_doc.tables)} (ожидалось минимум 6)")
            return None

        # --------- НОВЫЙ ДОКУМЕНТ НА ОСНОВЕ ШАБЛОНА ----------
        out_doc = Document(template_path)
        _clear_body_keep_sectpr(out_doc)

        # --------- ВСТАВКА БЛАНКОВ ----------
        for idx, src_table_index in enumerate(plan):
            if idx > 0:
                _one_empty_line(out_doc, gap_mm=3)  # <-- тут регулируешь отступ

            _anchor_paragraph(out_doc)

            src_table = template_doc.tables[src_table_index]
            out_doc.element.body.append(copy.deepcopy(src_table._tbl))

            inserted_table = out_doc.tables[-1]
            _table_to_inline(inserted_table)
            _set_tbl_fixed_layout(inserted_table)

        # --------- ЗАМЕНА ПЛЕЙСХОЛДЕРОВ ----------
        for i, table in enumerate(out_doc.tables):
            original_table_index = plan[i]
            if original_table_index in (0, 3):
                group_text = "1 (первая)"
            elif original_table_index in (1, 4):
                group_text = "2 (вторая)"
            elif original_table_index in (2, 5):
                group_text = "3 (третья)"
            else:
                group_text = "2 (вторая)"

            ph = dict(placeholders_base)
            ph["{rang_group}"] = group_text

            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_in_runs(paragraph, ph)

        # --------- КОМПАКТИЗАЦИЯ + СДВИГ ВЛЕВО ----------
        _compact_paragraphs(out_doc)
        _shift_content_left_by_right_margin(out_doc, mm=0)

        # --------- СОХРАНЕНИЕ ----------
        temp_dir = tempfile.gettempdir()
        ts = int(time.time())
        out_path = os.path.join(temp_dir, f"document_compact_{ts}.docx")
        out_doc.save(out_path)

        print("✅ Создан:", out_path)
        return out_path

    except Exception as e:
        print("💥 ОШИБКА:", type(e).__name__, str(e))
        traceback.print_exc()
        return None


def filldocxtemplate(dt):
    return fill_docx_template(dt)
