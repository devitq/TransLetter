from django.contrib.auth import views
from django.urls import path

import accounts.forms
import accounts.views

app_name = "accounts"

urlpatterns = [
    path("signup/", accounts.views.UserSignupView.as_view(), name="signup"),
    path(
        "login/",
        views.LoginView.as_view(
            template_name="accounts/login.html",
            form_class=accounts.forms.MyLoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        views.LogoutView.as_view(template_name="accounts/logout.html"),
        name="logout",
    ),
    path(
        "password_change/",
        views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            form_class=accounts.forms.MyPasswordChangeForm,
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html",
        ),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            form_class=accounts.forms.MyPasswordResetForm,
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            form_class=accounts.forms.MyPasswordConfirmForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path(
        "activate/<str:token>/",
        accounts.views.ActivateAccountView.as_view(),
        name="activate_account",
    ),
    path(
        "request_activation/",
        accounts.views.AccountActivationRequestView.as_view(),
        name="request_activation",
    ),
    path(
        "account/edit/",
        accounts.views.AccountEditView.as_view(),
        name="edit_account",
    ),
]
