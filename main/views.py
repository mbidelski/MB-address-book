from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views import View
from main.models import *
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils.decorators import method_decorator
import re

# Create your views here.
container_html = """
<html>
<body>
<div style="width:40%; margin:auto;">
{}
</div>
</body>
</html>
"""

contact_html = """
<table width=100%>
<tr>
    <td colspan=3><h3><a href="/"><< </a>Dane kontaktu</h3></td>
    <td>{}</td>
</tr>
<tr>
    <td><strong>Imię:</strong></td>
    <td colspan=3>{}</td>
</tr>
<tr>
    <td><strong>Nazwisko:</strong></td>
    <td colspan=3>{}</td>
</tr>
<tr>
    <td><strong>Opis:</strong></td>
    <td colspan=3>{}</td>
</tr>
<tr style="height:10px"><td colspan=3></td></tr>
"""

@csrf_exempt
def home(request):

    selected_group = None
    group_shown = "Wszystkie kontakty"

    if request.method == "POST":
        if request.POST.get("submit") == "add_contact":
            add_name = request.POST.get("name")
            add_surname = request.POST.get("surname")
            add_desc = request.POST.get("desc")
            Person.objects.create(name=add_name, surname=add_surname, description=add_desc)
            new_person = Person.objects.get(name=add_name, surname=add_surname, description=add_desc)
            return redirect("/show/{}".format(new_person.id))

        elif request.POST.get("submit") == "add_group":
            add_name = request.POST.get("name")
            Group.objects.create(name=add_name)

        elif request.POST.get("group"):
            if request.POST.get("group") != "all_contacts":
                group_id = int(request.POST.get("group"))
                selected_group = Group.objects.get(pk=group_id)
                group_shown = str(selected_group.name).title()

    if selected_group:
        all_contacts = selected_group.member.all().order_by('surname', 'name')
    else:
        all_contacts = Person.objects.order_by('surname', 'name')

    groups = Group.objects.all().order_by('name')

    return render(request, 'home.html', {
        'group_shown': group_shown,
        'all_contacts': all_contacts,
        'groups': groups
    })

@csrf_exempt
def mod_contact(request, contact_id):
    contact = Person.objects.get(pk=contact_id)
    response = HttpResponse()

    if request.method == "POST":
        contact.name = request.POST.get("name")
        contact.surname = request.POST.get("surname")
        contact.description = request.POST.get("desc")
        contact.save()
        return redirect("/")

    if contact.description == None:
        desc = "-"
    else:
        desc = contact.description

    mod_contact_form_html = contact_html.format(
        "",
        """<input type="text" name="name" value="{}">""".format(contact.name),
        """<input type="text" name="surname" value="{}">""".format(contact.surname),
        """<input type="text" name="desc" value="{}">""".format(desc)
    ) + """
    <tr>
    <td colspan=4><button type="submit">Modyfikuj</button></d>
    </tr>
    """
    # print(mod_contact_form_html)
    response.write(
        container_html.format("""
            <form action=# method="POST">
            {}
            </form> 
        """.format(mod_contact_form_html))
    )
    return response


def del_contact(request, contact_id):
    contact = Person.objects.get(pk=contact_id)
    name = contact.name
    surname = contact.surname
    contact.delete()
    return HttpResponse("""Usunąłem {} {} z książki adresowej <a href="/">Powrót</a>""".format(name, surname))

@csrf_exempt
def show_contact(request, contact_id):

    contact = Person.objects.get(pk=contact_id)
    address_err_str = ""
    email_err_str = ""
    phone_err_str = ""

    if request.method == "POST":
        if request.POST.get("add") == "email":
            a_email = request.POST.get("email")
            a_label = request.POST.get("email_label")
            if re.findall('^(\w+@\w+\.\w+)$', a_email):
                Email.objects.create(label=a_label, email_address=a_email, email_owner=contact)
                email_err_str = """
                <font color="green">Dodano email<font>
                """
            else:
                email_err_str = """
                <font color="red">Błędny adres email<font>
                """
        elif request.POST.get("add") == "phone":
            a_no = request.POST.get("phone_no")
            a_label = request.POST.get("phone_label")
            if re.findall('^(\d){5,9}$', str(a_no)):
                Phone.objects.create(label=a_label, phone_no=a_no, phone_owner=contact)
                phone_err_str = """
                <font color="green">Dodano nr tel<font>
                """
            else:
                phone_err_str = """
                <font color="red">Błędny nr tel<font>
                """
        elif request.POST.get("add") == "address":
            Address.objects.create(street=request.POST.get("street"), street_no=request.POST.get("street_no"),\
                                 apt_no=request.POST.get("apt_no"), city=request.POST.get("city"),\
                                 resident=contact)
            address_err_str = """
            <font color="green">Dodano adres<font>
            """

    address = contact.address_set.all()
    email = Email.objects.filter(email_owner=contact)
    phone = Phone.objects.filter(phone_owner=contact)

    return render(request, 'contact.html', {
        'contact': contact,
        'address': address,
        'email': email,
        'phone': phone,
        'address_err_str': address_err_str,
        'email_err_str': email_err_str,
        'phone_err_str': phone_err_str,
    })

def del_mail(request, mail_id):
    response = HttpResponse()
    mail = Email.objects.get(pk=mail_id)
    return_id = mail.email_owner.id
    mail.delete()
    return redirect("/show/{}".format(return_id))

def del_address(request, address_id):
    response = HttpResponse()
    address = Address.objects.get(pk=address_id)
    return_id = address.resident.id
    address.delete()
    return redirect("/show/{}".format(return_id))

def del_phone(request, phone_id):
    response = HttpResponse()
    phone = Phone.objects.get(pk=phone_id)
    return_id = phone.phone_owner.id
    phone.delete()
    return redirect("/show/{}".format(return_id))

@csrf_exempt
def group(request, group_id):

    selected_group = Group.objects.get(pk=group_id)

    if request.method == "POST":
        person_id = int(request.POST.get("contact"))
        person_to_group = Person.objects.get(pk=person_id)
        selected_group.member.add(person_to_group)
        selected_group.save()

    all_contacts = Person.objects.all().order_by('surname', 'name')
    group_contacts = selected_group.member.all().order_by('surname', 'name')
    contacts = []
    for i in all_contacts:
        if i not in group_contacts:
            contacts.append(i)

    return render(request, 'group.html', {
        'group': selected_group,
        'contacts': contacts,
        'group_contacts': group_contacts
    })

def del_group(request, group_id):
    grouptodel = Group.objects.get(pk=group_id)
    name = grouptodel.name
    grouptodel.delete()
    return HttpResponse("""Usunąłem grupę "{}" z książki adresowej <a href="/">Powrót</a>""".format(name))

def del_from_group(request, contact_id, group_id):
    response = HttpResponse()
    person_to_del = Person.objects.get(pk=contact_id)
    selected_group = Group.objects.get(pk=group_id)
    selected_group.member.remove(person_to_del)
    selected_group.save()
    return redirect("/group/{}".format(group_id))

