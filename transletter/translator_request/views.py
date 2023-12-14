from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import pgettext_lazy
from django.views.generic import DetailView, ListView, View

from resume.models import Resume, ResumeFile
from translator_request.forms import (
    RejectRequestForm,
    RequestTranslatorForm,
    RequestTranslatorFormDisabled,
)
from translator_request.models import (
    TranslatorRequest,
    TranslatorRequestStatusLog,
)

__all__ = ()

STATUS_CHOICES = {
    "SE": "Sent",
    "UR": "Under review",
    "AC": "Accepted",
    "RJ": "Rejected",
}


class RequestTranslatorView(LoginRequiredMixin, View):
    template_name = "translator_request/request_translator.html"
    success_url = reverse_lazy("translator_request:request_translator")

    def get(self, request):
        initial_languages = request.user.account.languages
        try:
            request_status = request.user.translator_request.status
            resume = request.user.account.resume
        except Exception:
            request_status = "NN"
            resume = None
        if request_status in "SERJACNN":
            form = RequestTranslatorForm(
                instance={
                    "user_form": request.user,
                    "account_form": request.user.account,
                    "resume_form": resume,
                },
                initial={
                    "account_form": {"languages": initial_languages},
                    "resume_form": {
                        "about": resume.about
                        if resume
                        else request.user.account.about or None,
                    },
                },
            )
        else:
            form = RequestTranslatorFormDisabled(
                instance={
                    "user_form": request.user,
                    "account_form": request.user.account,
                    "resume_form": resume or None,
                },
                initial={
                    "account_form": {"languages": initial_languages},
                    "resume_form": {
                        "about": resume.about
                        if resume
                        else request.user.account.about or None,
                    },
                },
            )
        return render(
            request,
            template_name=self.template_name,
            context={
                "form": form,
                "request_status": request_status,
                "resume": resume,
            },
        )

    def post(self, request):
        form = RequestTranslatorForm(request.POST, request.FILES)

        try:
            request_status = request.user.translator_request.status
        except Exception:
            request_status = "NN"

        if form.is_valid() and request_status in "SERJACNN":
            resume = form["resume_form"]
            request.user.first_name = form["user_form"].cleaned_data["first_name"]
            request.user.last_name = form["user_form"].cleaned_data["last_name"]
            request.user.save()
            files = request.FILES.getlist("files_form-file")

            if request.user.account.resume:
                request.user.account.resume.about = resume.cleaned_data[
                    "about"
                ]
                request.user.account.resume.save()
                resume = request.user.account.resume
            else:
                resume = resume.save()

            account_form = form["account_form"]
            request.user.account.resume = resume
            request.user.account.languages = account_form.cleaned_data[
                "languages"
            ]
            request.user.account.native_lang = account_form.cleaned_data[
                "native_lang"
            ]
            request.user.account.save()

            if hasattr(request.user, "translator_request"):
                request.user.translator_request.resume = resume
                if request_status != "AC":
                    request.user.translator_request.status = "SE"
                request.user.translator_request.save()
                messages.success(
                    request,
                    pgettext_lazy(
                        "translator request update success",
                        "Your request to become a translator has been updated",
                    ),
                )
            else:
                TranslatorRequest.objects.create(
                    user=request.user,
                    resume=resume,
                )
                messages.success(
                    request,
                    pgettext_lazy(
                        "translator request create success",
                        "Your request to become a translator has been sent",
                    ),
                )

            for file in files:
                ResumeFile.objects.create(
                    resume=request.user.account.resume,
                    file=file,
                )

            return redirect(reverse("translator_request:request_translator"))

        messages.error(
            request,
            pgettext_lazy(
                "translator request on review error",
                "Your request is currently under review.",
            ),
        )

        return render(
            request,
            template_name=self.template_name,
            context={"form": form},
        )


class TranslatorRequestsView(ListView):
    template_name = "translator_request/translator_requests.html"
    paginate_by = 10
    model = TranslatorRequest

    def get_queryset(self):
        return TranslatorRequest.objects.for_staff().order_by("-id")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm(
            "translator_request.view_translatorrequest",
        ):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class TranslatorRequestView(LoginRequiredMixin, DetailView):
    template_name = "translator_request/translator_request.html"
    model = TranslatorRequest
    context_object_name = "translator_request"

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm(
            "translator_request.view_translatorrequest",
        ):
            raise PermissionDenied()
        item = self.get_object()
        form = RejectRequestForm(request.POST)
        if item.status == "SE":
            item.status = "UR"
            TranslatorRequestStatusLog.objects.create(
                user=request.user,
                translator_request=item,
                from_status="SE",
                to="UR",
            )
            fr_status = STATUS_CHOICES["SE"]
            to_status = STATUS_CHOICES["UR"]
            text = f"""Status was change from '{fr_status}' to '{to_status}'
Your request is currently under review"""
            send_mail(
                "Change Translator Request Status",
                text,
                settings.EMAIL,
                [request.user.email],
                fail_silently=False,
            )
            item.save()
        return render(
            request,
            template_name=self.template_name,
            context={"translator_request": item, "form": form},
        )


class AcceptRequestView(LoginRequiredMixin, DetailView):
    model = TranslatorRequest
    context_object_name = "translator_request"

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm(
            "translator_request.edit_translatorrequest",
        ):
            raise PermissionDenied()
        item = self.get_object()
        TranslatorRequestStatusLog.objects.create(
            user=request.user,
            translator_request=item,
            from_status=item.status,
            to="AC",
        )
        fr_status = STATUS_CHOICES[item.status]
        to_status = STATUS_CHOICES["AC"]
        text = f"""Status was change from '{fr_status}' to '{to_status}'
Your request has been accepted"""
        send_mail(
            "Change Translator Request Status",
            text,
            settings.EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        item.status = "AC"
        item.user.account.is_translator = True
        item.user.account.save()
        item.save()
        return redirect(reverse("translator_request:translator_requests"))


class RejectRequestView(LoginRequiredMixin, DetailView):
    model = TranslatorRequest
    context_object_name = "translator_request"

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm(
            "translator_request.edit_translatorrequest",
        ):
            raise PermissionDenied()
        item = self.get_object()
        blocked = request.GET.get("block", False)
        TranslatorRequestStatusLog.objects.create(
            user=request.user,
            translator_request=item,
            from_status=item.status,
            to="RJ",
        )
        fr_status = STATUS_CHOICES[item.status]
        to_status = STATUS_CHOICES["RJ"]
        text = f"""Status was change from '{fr_status}' to '{to_status}'
Your request was rejected"""
        send_mail(
            "Change Translator Request Status",
            text,
            settings.EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        item.status = "RJ"
        item.user.account.is_translator = False
        if blocked:
            item.user.account.blocked = True
            item.user.account.blocked_reason = "Spam"
        item.user.account.save()
        item.save()
        return redirect(reverse("translator_request:translator_requests"))


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
