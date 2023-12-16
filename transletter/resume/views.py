from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import pgettext_lazy
from django.views.generic import View

from resume.models import Resume, ResumeFile


__all__ = ()


class DownloadView(LoginRequiredMixin, View):
    def dispatch(self, request, pk, file_id, *args, **kwargs):
        resume_author = get_object_or_404(
            Resume.objects.all(),
            pk=pk,
        ).account.user
        if (
            not request.user.has_perm(
                "translator_request.view_translatorrequest",
            )
            and request.user != resume_author
            and not resume_author.account.is_translator
        ):
            raise PermissionDenied()
        return super().dispatch(request, pk, file_id, *args, **kwargs)

    def get(self, request, pk, file_id):
        file_object = get_object_or_404(ResumeFile, pk=file_id, resume_id=pk)
        path = file_object.file.path

        if settings.STORAGE_NAME == "aws":
            return self.serve_from_s3(path)
        return self.serve_from_local(path)

    def serve_from_s3(self, path):
        import boto3

        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        try:
            s3_response = s3.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=settings.AWS_LOCATION + path,
            )
        except Exception as e:
            return HttpResponseNotFound(f"File not found: {e}")

        response = FileResponse(
            s3_response["Body"],
            content_type="application/octet-stream",
        )
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{path.split("/")[-1]}"'
        return response

    def serve_from_local(self, path):
        file_path = settings.MEDIA_ROOT / path
        if file_path.exists():
            return FileResponse(open(file_path, "rb"), as_attachment=True)
        return HttpResponseNotFound()


class DeleteView(LoginRequiredMixin, View):
    def dispatch(self, request, pk, file_id, *args, **kwargs):
        resume_author = get_object_or_404(
            Resume.objects.all(),
            pk=pk,
        ).account.user
        if request.user != resume_author:
            raise PermissionDenied()
        return super().dispatch(request, pk, file_id, *args, **kwargs)

    def get(self, request, pk, file_id):
        file_object = get_object_or_404(ResumeFile, pk=file_id, resume_id=pk)
        file_object.delete()
        messages.success(
            request,
            pgettext_lazy(
                "success message in views",
                "Your resume file was successfully deleted",
            ),
        )
        return redirect("translator_request:request_translator")
