from functools import wraps

from django.core.exceptions import PermissionDenied

from projects.models import ProjectMembership


__all__ = ()


def can_access_project_decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        slug = kwargs.get("slug")
        has_access = ProjectMembership.objects.filter(
            project__slug=slug,
            user=request.user,
        ).exists()

        if not has_access:
            raise PermissionDenied()

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def project_admin_decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        slug = kwargs.get("slug")
        has_access = ProjectMembership.objects.filter(
            project__slug=slug,
            user=request.user,
            role__in=("owner", "admin"),
        ).exists()
        if not has_access:
            raise PermissionDenied()

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def project_owner_decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        slug = kwargs.get("slug")
        has_access = ProjectMembership.objects.filter(
            project__slug=slug,
            user=request.user,
            role__in=("owner",),
        ).exists()

        if not has_access:
            raise PermissionDenied()

        return view_func(request, *args, **kwargs)

    return _wrapped_view
