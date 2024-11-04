from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login as auth_login

from django import forms


class MyArticleAdminForm(forms.Form):
    pin = forms.IntegerField(label="Your Pin")


def admin_otp_page(request):
    print("in dummy", request)
    form = MyArticleAdminForm()
    if request.method == "POST":
        form = MyArticleAdminForm(request.POST)
        if form.is_valid():
            print("in form")
            pin = form.cleaned_data["pin"]
            if pin == 1:
                return redirect("/admin/")
            return HttpResponseRedirect(reverse("admin:logout"))

        return HttpResponseRedirect(reverse("admin:logout"))

    return render(request, "admin/admin_otp.html", {"form": form})



