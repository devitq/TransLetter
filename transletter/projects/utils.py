import json
from pathlib import Path
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
import polib

import projects.models
from projects.models import TranslationRow

__all__ = ()


def parse_file_and_create_translations(language_file, file_path):
    file_path = settings.MEDIA_ROOT / file_path
    file_path = str(file_path)
    try:
        existing_rows = TranslationRow.objects.filter(
            translation_file=language_file,
        )
        existing_rows_dict = {row.msg_id: row for row in existing_rows}

        with Path(file_path).open() as file:
            if file_path.endswith(".po"):
                po = polib.pofile(file_path)
                for entry in po:
                    msg_id = entry.msgid
                    msg_str = entry.msgstr
                    msg_context = entry.msgctxt
                    occurrences = entry.occurrences

                    if msg_id in existing_rows_dict:
                        existing_rows_dict[msg_id].msg_str = msg_str
                        existing_rows_dict[msg_id].msg_context = msg_context
                        existing_rows_dict[msg_id].occurrences = occurrences
                        existing_rows_dict[msg_id].save()
                    else:
                        TranslationRow.objects.create(
                            msg_id=msg_id,
                            msg_str=msg_str,
                            msg_context=msg_context,
                            translation_file=language_file,
                            occurrences=occurrences,
                        )

                existing_rows.exclude(
                    msg_id__in=[entry.msgid for entry in po],
                ).delete()

            elif file_path.endswith(".json"):
                data = json.load(file)
                for msg_id, msg_data in data.items():
                    msg_str = msg_data.get("msg_str")
                    msg_context = msg_data.get("msg_context")

                    if msg_id in existing_rows_dict:
                        existing_rows_dict[msg_id].msg_str = msg_str
                        existing_rows_dict[msg_id].msg_context = msg_context
                        existing_rows_dict[msg_id].save()
                    else:
                        TranslationRow.objects.create(
                            msg_id=msg_id,
                            msg_str=msg_str,
                            msg_context=msg_context,
                            translation_file=language_file,
                        )

                existing_rows.exclude(msg_id__in=data.keys()).delete()
    except Exception as e:
        raise ValidationError(f"Error parsing file: {str(e)}")


def export_po_file(rows, file_path, project_slug, filename):
    file_path = settings.MEDIA_ROOT / file_path
    project_id = projects.models.Project.objects.get(slug=project_slug).id
    file_path = str(file_path)
    po = polib.pofile(file_path)

    seed = uuid.uuid4()
    export_filepath = (
        f"media\\projects\\{str(project_id)}\\export\\{str(seed)}\\"
    )
    try:
        Path(export_filepath).mkdir()
    except FileExistsError:
        pass
    rows = [
        (row.msg_id, row.msg_context, row.msg_str, row.occurrences)
        for row in rows
    ]

    filename = str(filename).rsplit("/")[-1]
    file = Path(export_filepath + filename).open(encoding="utf8", mode="w")
    file.write("# Translated using TransLetter <3\n\n")
    file.write('msgid ""\nmsgstr ""\n')
    for i, j in po.metadata.items():
        file.write(f'"{i}: {j}"\n')
    for row in rows:
        occur = ""
        for i in row[3]:
            occur += i[0] + " "
        file.write(f"#: {occur}\n")
        file.write(f'msgctxt "{row[1]}"\n')
        file.write(f'msgid "{row[0]}"\n')
        file.write(f'msgstr "{row[2]}"\n\n')

    return export_filepath + filename
