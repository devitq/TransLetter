__all__ = ("BaseFormMixin",)


class BaseFormMixin:
    def set_field_attributes(self):
        for field in self.visible_fields():
            if field.field.widget.attrs.get("class") is None:
                field.field.widget.attrs["class"] = "form-control"
            else:
                field.field.widget.attrs["class"] += " form-control"
            if self.is_bound:
                if len(field.errors) == 0:
                    field.field.widget.attrs["class"] += " is-valid"
                else:
                    field.field.widget.attrs["class"] += " is-invalid"
