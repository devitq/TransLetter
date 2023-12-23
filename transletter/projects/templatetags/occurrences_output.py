from django import template


__all__ = ()

register = template.Library()


@register.filter(name="pretty_occurrences")
def pretty_occurrences(occurrences):
    try:
        pretty_output = ""
        for file_path, line_number in occurrences:
            pretty_output += f"File: {file_path}, Line: {line_number};\n"

        return pretty_output.rstrip("\n")
    except Exception:
        return "N/A"
