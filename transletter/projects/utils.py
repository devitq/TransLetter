import json
from pathlib import Path
import uuid

from django.conf import settings
import polib

import projects.models
from projects.models import TranslationRow

__all__ = ()


def parse_file_and_create_translations(language_file, file_path):
    file_path = settings.MEDIA_ROOT / file_path
    file_path = str(file_path)
    existing_rows = TranslationRow.objects.filter(
        translation_file=language_file,
    )
    existing_rows_dict = {row.msg_id: row for row in existing_rows}
    added = 0
    updated = 0
    deleted = 0

    with Path(file_path).open() as file:
        if file_path.endswith(".po"):
            po = polib.pofile(file_path)
            for entry in po:
                msg_id = entry.msgid
                msg_str = entry.msgstr
                msg_context = entry.msgctxt
                occurrences = entry.occurrences

                if msg_id in existing_rows_dict:
                    existing_rows_dict[msg_id].msg_context = msg_context
                    existing_rows_dict[msg_id].occurrences = occurrences
                    existing_rows_dict[msg_id].save()
                    updated += 1
                else:
                    TranslationRow.objects.create(
                        msg_id=msg_id,
                        msg_str=msg_str,
                        msg_context=msg_context,
                        translation_file=language_file,
                        occurrences=occurrences,
                    )
                    added += 1

            deleted_rows = existing_rows.exclude(
                msg_id__in=[entry.msgid for entry in po],
            )
            deleted = deleted_rows.count()
            deleted_rows.delete()

        elif file_path.endswith(".json"):
            data = json.load(file)
            for msg_id, msg_str in data.items():
                if msg_id in existing_rows_dict:
                    updated += 1
                else:
                    TranslationRow.objects.create(
                        msg_id=msg_id,
                        msg_str=msg_str,
                        translation_file=language_file,
                    )
                    added += 1

            deleted_rows = existing_rows.exclude(msg_id__in=data.keys())
            deleted = deleted_rows.count()
            deleted_rows.delete()

    return added, updated, deleted


def export_po_file(rows, file_path, project_slug):
    file_path = settings.MEDIA_ROOT / file_path
    project_id = projects.models.Project.objects.get(slug=project_slug).id
    file_path = str(file_path)
    filename = file_path.rsplit("/")[-1]

    po = polib.pofile(file_path)
    seed = uuid.uuid4()
    export_filepath = (
        settings.MEDIA_ROOT / f"projects/{str(project_id)}/export/{str(seed)}/"
    )

    try:
        export_filepath.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass

    rows = [
        (row.msg_id, row.msg_context, row.msg_str, row.occurrences)
        for row in rows
    ]

    filename = str(filename).rsplit("/")[-1]

    for row in rows:
        entry = polib.POEntry(
            msgid=row[0],
            msgstr=str(row[2]),
            msgctxt=row[1],
            occurrences=row[3],
        )
        po.append(entry)

    po.save(export_filepath / filename)
    return export_filepath / filename


def export_json_file(rows, file_path, project_slug):
    file_path = settings.MEDIA_ROOT / file_path
    project_id = projects.models.Project.objects.get(slug=project_slug).id
    file_path = str(file_path)
    filename = file_path.rsplit("/")[-1]
    seed = uuid.uuid4()

    export_filepath = (
        settings.MEDIA_ROOT / f"projects/{str(project_id)}/export/{str(seed)}/"
    )

    try:
        export_filepath.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass

    rows_data = {row.msg_id: row.msg_str for row in rows}

    filename = str(filename).rsplit("/")[-1]

    with Path(export_filepath / filename).open(
        "w",
        encoding="utf-8",
    ) as json_file:
        json.dump(rows_data, json_file, indent=2, ensure_ascii=False)

    return export_filepath / filename
