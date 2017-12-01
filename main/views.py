from django.shortcuts import redirect
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

    if request.method == "POST":
        add_name = request.POST.get("name")
        add_surname = request.POST.get("surname")
        add_desc = request.POST.get("desc")
        Person.objects.create(name=add_name, surname=add_surname, description=add_desc)
        new_person = Person.objects.get(name=add_name, surname=add_surname, description=add_desc)
        return redirect("/show/{}".format(new_person.id))

    response = HttpResponse()
    all_contacts = Person.objects.order_by('surname')
    contacts_list_html = """<table width=100%>
    <tr>
        <th scope="col" align="left" width=25%><font color="grey">Imię</th>
        <th scope="col" width=25%><font color="grey">Nazwisko</th>
        <th scope="col"></th>
        <th scope="col"></th>
    </tr>"""

    for i in all_contacts:

        name = """<p><a href="/show/{}"><strong>{}</strong></a></p>""".format(i.id, i.name.title())
        surname = """<p><strong>{}</strong></p>""".format(i.surname.title())
        mod = """<a href="/mod/{}"><font size="2">Edytuj</font></a>""".format(i.id)
        del_contact = """<a href="/del/{}"><font size="2">Usuń</font></a>""".format(i.id)
        contacts_list_html = contacts_list_html + """<tr align="middle">
        <td align="left">{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td></tr>""".format(name, surname, mod, del_contact)

    contacts_list_html = contacts_list_html + """</table>
    <form method="POST" action=#>
        <p><strong><font color="grey">Dodaj kontakt:</strong></font></p>
        <label>Imię: <input type="text" name="name" style="width:100px"></label>
        <label>Nazwisko: <input type="text" name="surname" style="width:100px"></label>
        <label>Opis: <input type="text" name="desc"></label>
        <button type="submit" name="submit" value="add">Dodaj</button>
    </form>
    """
    response.write(container_html.format(contacts_list_html))
    return response

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
            # print(re.findall('^(\w+@\w+\.\w+)$', a_email))
            # print(len(re.findall('^(\w+@\w+\.\w+)$', a_email)))
            #
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

    response = HttpResponse()

    if contact.description == None:
        desc = "-"
    else:
        desc = contact.description

    link_to_mod_html = """
        <h4><a href="/mod/{}">Edytuj</a></h4>
    """.format(contact.id)

    contact_details_html = contact_html.format(link_to_mod_html, contact.name, contact.surname, desc)

    if Address.objects.filter(resident=contact) is not None:
        contact_details_html = contact_details_html + """
        <tr>
            <td colspan=4><h4>Adresy</h3></td>
        </tr>
        """

        for i in Address.objects.filter(resident=contact):
            if i.apt_no != "":
                apt_no = "/ " + str(i.apt_no)
            else:
                apt_no = ""
            contact_details_html = contact_details_html + """
            <tr>
                <td style="width:30%">{}</td>
                <td style="width:30%">{} {}</td>
                <td style="width:30%">{}</td>
                <td align="right"><a href="/deladdress/{}">Usuń</a></td>
            </tr>
            """.format(i.street, i.street_no, apt_no, i.city, i.id)

    contact_details_html = contact_details_html + """
    <tr>
    <form action=# method="POST">
        <td><input type="text" name="street" placeholder="nazwa ulicy..."></td>
        <td>nr: <input type="text" name="street_no" size="3"> m: 
        <input type="text" name="apt_no" size="3"></td>
        <td><input type="text" name="city" placeholder="miasto..."></td>
        <td align="right"><button type="submit" name="add" value="address">Dodaj</button></a></td>
    </form>
    </tr>
    <tr>
    <td colspan=4>{}</td>
    </tr>
    """.format(address_err_str)

    if Email.objects.filter(email_owner=contact) is not None:
        contact_details_html = contact_details_html + """
        <tr>
            <td colspan=4><h4>Adresy email</h3></td>
        </tr>
        """

        for i in Email.objects.filter(email_owner=contact):
            if i.label is not None:
                e_label = i.label
            else:
                e_label = ""
            contact_details_html = contact_details_html + """
            <tr>
                <td style="width:30%">{}</td>
                <td style="width:30%">{}</td>
                <td align="right" colspan=2><a href="/delmail/{}">Usuń</a></td>
            </tr>
            """.format(i.email_address, e_label, i.id)

    contact_details_html = contact_details_html + """
    <tr>
    <form action=# method="POST">
        <td><input type="text" name="email" placeholder="adres email..."></td>
        <td><input type="text" name="email_label" placeholder="etykieta adresu..."></td>
        <td align="right" colspan=2><button type="submit" name="add" value="email">Dodaj</button></a></td>
    </form>
    </tr>
    <tr>
    <td colspan=4>{}</td>
    </tr>
    """.format(email_err_str)

    if Phone.objects.filter(phone_owner=contact) is not None:
        contact_details_html = contact_details_html + """
        <tr>
            <td colspan=4><h4>Telefony</h3></td>
        </tr>
        """

        for i in Phone.objects.filter(phone_owner=contact):
            if i.label is not None:
                t_label = i.label
            else:
                t_label = ""
            contact_details_html = contact_details_html + """
            <tr>
                <td style="width:30%">{}</td>
                <td style="width:30%">{}</td>
                <td align="right" colspan=2><a href="/delphone/{}">Usuń</a></td>
            </tr>
            """.format(i.phone_no, t_label, i.id)

    contact_details_html = contact_details_html + """
    <tr>
    <form action=# method="POST">
        <td><input type="number" name="phone_no" placeholder="nr tel XXXXXXXXX"></td>
        <td><input type="text" name="phone_label" placeholder="etykieta numeru..."></td>
        <td align="right" colspan=2><button type="submit" name="add" value="phone">Dodaj</button></a></td>
    </form>
    </tr>
    <tr>
    <td colspan=4>{}</td>
    </tr>
    """.format(phone_err_str)

    contact_details_html = contact_details_html + "</table>"
    response.write(container_html.format(contact_details_html))
    return response

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

