from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView
)

from . import views
from .forms import LoginForm, ResetPasswordForm, ConfirmResetPasswordForm, ChangePasswordForm


app_name = 'main_site'

urlpatterns = [
    path('', views.index, name='index'),
    path('faq/', views.faq, name='faq'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/registered/', views.registered, name='registered'),
    path('accounts/login/', LoginView.as_view(
        template_name='main_site/login.html',
        authentication_form=LoginForm), name='login'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/logout/', LogoutView.as_view(
        template_name='main_site/logged_out.html'), name='logout'),
    path('accounts/password_reset/', PasswordResetView.as_view(
        template_name='main_site/reset_password.html',
        email_template_name='main_site/password_reset_email.html',
        form_class=ResetPasswordForm,
        success_url=reverse_lazy('main_site:password_reset_done')), name='password_reset'),
    path('accounts/password_reset/done/', PasswordResetDoneView.as_view(
        template_name='main_site/reset_password_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='main_site/reset_password_confirm.html',
        form_class=ConfirmResetPasswordForm,
        success_url=reverse_lazy('main_site:password_reset_complete')), name='password_reset_confirm'),
    path('accounts/done/', PasswordResetCompleteView.as_view(
        template_name='main_site/reset_password_complete.html'), name='password_reset_complete'),
    path('accounts/password_change/', PasswordChangeView.as_view(
        template_name='main_site/change_password.html',
        form_class=ChangePasswordForm,
        success_url=reverse_lazy('main_site:password_change_done')), name='password_change'),
    path('accounts/password_change/done/', PasswordChangeDoneView.as_view(
        template_name='main_site/change_password_done.html'), name='password_change_done'),
]
