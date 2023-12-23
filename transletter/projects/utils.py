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

    existing_rows = TranslationRow.objects.filter(
        translation_file=language_file,
    )
    existing_rows_dict = {
        (row.msg_id, row.msg_context): row for row in existing_rows
    }

    added = 0
    updated = 0
    deleted = 0

    with file_path.open() as file:
        if file_path.suffix == ".po":
            po = polib.pofile(file_path)
            metadata_keys = [
                "Project-Id-Version",
                "Report-Msgid-Bugs-To",
                "POT-Creation-Date",
                "PO-Revision-Date",
                "Last-Translator",
                "Language-Team",
                "Language",
                "MIME-Version",
                "Content-Type",
                "Content-Transfer-Encoding",
                "Plural-Forms",
            ]
            metadata = {
                key: po.metadata.get(key)
                for key in metadata_keys
                if po.metadata.get(key)
            }
            language_file.metadata = metadata
            language_file.save()
            for entry in po:
                key_tuple = (entry.msgid, entry.msgctxt)
                existing_row = existing_rows_dict.get(key_tuple)

                if existing_row:
                    existing_row.msg_context = entry.msgctxt
                    existing_row.occurrences = entry.occurrences
                    existing_row.save()
                    updated += 1
                else:
                    TranslationRow.objects.create(
                        msg_id=entry.msgid,
                        msg_str=entry.msgstr,
                        msg_context=entry.msgctxt,
                        translation_file=language_file,
                        occurrences=entry.occurrences,
                    )
                    added += 1
            deleted_rows = existing_rows.exclude(
                msg_id__in=[entry.msgid for entry in po],
            )
            deleted = deleted_rows.count()
            deleted_rows.delete()

        elif file_path.suffix == ".json":
            data = json.load(file)
            for msg_id, msg_str in data.items():
                key_tuple = (msg_id, None)
                existing_row = existing_rows_dict.get(key_tuple)

                if existing_row:
                    existing_row.msg_str = msg_str
                    existing_row.save()
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


def export_po_file(rows, file_object, project_slug):
    project_id = projects.models.Project.objects.get(slug=project_slug).id

    po = polib.POFile()
    if file_object.metadata:
        po.metadata = file_object.metadata

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

    filename = file_object.filename()

    for row in rows:
        entry = polib.POEntry(
            msgid=row[0],
            msgstr=row[2],
            msgctxt=row[1],
            occurrences=row[3],
        )
        po.append(entry)

    po.save(export_filepath / filename)
    return export_filepath / filename


def export_json_file(rows, file_object, project_slug):
    project_id = projects.models.Project.objects.get(slug=project_slug).id
    seed = uuid.uuid4()

    export_filepath = (
        settings.MEDIA_ROOT / f"projects/{str(project_id)}/export/{str(seed)}/"
    )

    try:
        export_filepath.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass

    rows_data = {row.msg_id: row.msg_str for row in rows}

    filename = file_object.filename()

    with Path(export_filepath / filename).open(
        "w",
        encoding="utf-8",
    ) as json_file:
        json.dump(rows_data, json_file, indent=2, ensure_ascii=False)

    return export_filepath / filename
