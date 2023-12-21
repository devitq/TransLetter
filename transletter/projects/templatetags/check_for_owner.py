from django import template


__all__ = ()

register = template.Library()


@register.filter
def is_owner(project, user):
    return project.projectmembership_set.filter(
        user=user,
        role="owner",
    ).exists()
