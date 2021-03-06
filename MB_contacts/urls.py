"""MB_contacts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from main.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', home),
    url(r'^del/(?P<contact_id>(\d)+)', del_contact),
    url(r'^mod/(?P<contact_id>(\d)+)', mod_contact),
    url(r'^group/(?P<group_id>(\d)+)', group),
    url(r'^delgroup/(?P<group_id>(\d)+)', del_group),
    url(r'^delfromgroup/(?P<contact_id>(\d)+)/(?P<group_id>(\d)+)', del_from_group),

    url(r'^show/(?P<contact_id>(\d)+)', show_contact),
    url(r'^delmail/(?P<mail_id>(\d)+)', del_mail),
    url(r'^deladdress/(?P<address_id>(\d)+)', del_address),
    url(r'^delphone/(?P<phone_id>(\d)+)', del_phone),
]
