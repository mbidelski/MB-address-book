from django.db import models

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=64, null=True)
    surname = models.CharField(max_length=64, null=True)
    description = models.TextField(null=True)

class Address(models.Model):
    city = models.CharField(max_length=64, null=True)
    street = models.CharField(max_length=64, null=True)
    street_no = models.CharField(max_length=64, null=True)
    apt_no = models.CharField(max_length=64, null=True)
    resident = models.ForeignKey(Person)

class Phone(models.Model):
    label = models.CharField(max_length=64, null=True)
    phone_no = models.IntegerField(null=True)
    phone_owner = models.ForeignKey(Person)

class Email(models.Model):
    label = models.CharField(max_length=64, null=True)
    email_address = models.CharField(max_length=64, null=True)
    email_owner = models.ForeignKey(Person)

class Group(models.Model):
    name = models.CharField(max_length=64, null=True)
    member = models.ManyToManyField(Person)


