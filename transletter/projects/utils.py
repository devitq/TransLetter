import json
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
import polib

from projects.models import TranslationRow


__all__ = ()


def parse_file_and_create_translations(language_file, file_path):
    file_path = settings.MEDIA_ROOT / file_path
    file_path = str(file_path)
    try:
        existing_rows = TranslationRow.objects.filter(
            translation_file=language_file,
        )
        existing_rows_dict = {row.row_id: row for row in existing_rows}

        with Path(file_path).open() as file:
            if file_path.endswith(".po"):
                po = polib.pofile(file_path)
                for entry in po:
                    row_id = entry.msgid
                    row_str = entry.msgstr

                    if row_id in existing_rows_dict:
                        existing_rows_dict[row_id].row_str = row_str
                        existing_rows_dict[row_id].save()
                    else:
                        TranslationRow.objects.create(
                            row_id=row_id,
                            row_str=row_str,
                            translation_file=language_file,
                        )

                existing_rows.exclude(
                    row_id__in=[entry.msgid for entry in po],
                ).delete()

            elif file_path.endswith(".json"):
                data = json.load(file)
                for row_id, row_str in data.items():
                    if row_id in existing_rows_dict:
                        existing_rows_dict[row_id].row_str = row_str
                        existing_rows_dict[row_id].save()
                    else:
                        TranslationRow.objects.create(
                            row_id=row_id,
                            row_str=row_str,
                            translation_file=language_file,
                        )

                existing_rows.exclude(row_id__in=data.keys()).delete()
    except Exception as e:
        raise ValidationError(f"Error parsing file: {str(e)}")
