import warnings
from urllib.parse import urlparse, urlunparse

from django.conf import settings

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.deprecation import RemovedInDjango50Warning
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect, reverse

from utils.custom.admin.admin_otp_view import admin_otp_page

UserModel = get_user_model()


class RedirectURLMixin:
    next_page = None
    redirect_field_name = REDIRECT_FIELD_NAME
    success_url_allowed_hosts = set()

    def get_success_url(self):
        print("in get_success_url")
        return self.get_redirect_url() or self.get_default_redirect_url()

    def get_redirect_url(self):
        print("in get_redirect_url")
        print(self.redirect_field_name)
        """Return the user-originating redirect URL if it's safe."""
        print(self.request.POST.get(
            self.redirect_field_name, self.request.GET.get(self.redirect_field_name)
        )
        )
        redirect_to = self.request.POST.get(
            self.redirect_field_name, self.request.GET.get(self.redirect_field_name)
        )
        # redirect_to = "/admin/otp-page/"

        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ""

    def get_success_url_allowed_hosts(self):
        print("in get_success_url_allowed_hosts")
        return {self.request.get_host(), *self.success_url_allowed_hosts}

    def get_default_redirect_url(self):
        print("in get_default_redirect_url")
        """Return the default redirect URL."""
        print(self.next_page)
        if self.next_page:
            return resolve_url(self.next_page)
        raise ImproperlyConfigured("No URL to redirect to. Provide a next_page.")


class LoginView(RedirectURLMixin, FormView):
    """
    Display the login form and handle the login action.
    """

    form_class = AuthenticationForm
    authentication_form = None
    template_name = "registration/login.html"
    redirect_authenticated_user = False
    extra_context = None

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        print("in dispatch", self.redirect_authenticated_user, request.user)
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get_default_redirect_url(self):
        print("in get_default_redirect_url")
        """Return the default redirect URL."""
        print(self.next_page)
        if self.next_page:
            return resolve_url(self.next_page)
        else:
            return resolve_url(settings.LOGIN_REDIRECT_URL)

    def get_form_class(self):
        print("in get_form_class")
        return self.authentication_form or self.form_class

    def get_form_kwargs(self):
        print("in get_form_kwargs")
        kwargs = super().get_form_kwargs()
        print(kwargs)
        kwargs["request"] = self.request
        return kwargs

    def admin_otp(self, form):
        print("in otp")
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        print("in form_valid")
        """Security check complete. Log the user in."""
        # return HttpResponseRedirect(reverse(admin_otp_page, kwargs={"app_label": "auth"}))
        # self.admin_otp()
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())
        #

        # return

    def get_context_data(self, **kwargs):
        print("in get_context_data")
        context = super().get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        context.update(
            {
                self.redirect_field_name: self.get_redirect_url(),
                "site": current_site,
                "site_name": current_site.name,
                **(self.extra_context or {}),
            }
        )
        return context

