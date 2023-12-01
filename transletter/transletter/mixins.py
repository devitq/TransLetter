__all__ = ("BaseFormMixin",)


class BaseFormMixin:
    def set_field_attributes(self):
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"
            if self.is_bound:
                if len(field.errors) == 0:
                    field.field.widget.attrs["class"] = "form-control is-valid"
                else:
                    field.field.widget.attrs[
                        "class"
                    ] = "form-control is-invalid"
