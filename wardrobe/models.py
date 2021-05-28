from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(null=False, blank=False)

    def __str__(self):
        return self.user.username

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.image.url))
    admin_photo.allow_tags = True
#
class Style(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.name


class Occassion(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    styles = models.ManyToManyField('Style', related_name='styles')

    def __str__(self):
        return self.name


class Photos(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Items', null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(null=False, blank=False)
    style = models.ManyToManyField('Style', related_name='style')
    description = models.CharField(max_length=200, blank=True)

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.image.url))
    admin_photo.allow_tags = True


    def __str__(self):
        return self.description


class Outfit(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True)
    items = models.ManyToManyField('Photos', related_name='items')

    def __str__(self):
        return self.name



# class Pizza(models.Model):
#
#     name = models.CharField(max_length=30, null=True)
#     toppings = models.ManyToManyField('Topping', related_name='pizzas')
#
#     def __str__(self):
#         return self.name
#
#
# class Topping(models.Model):
#     name = models.CharField(max_length=30, null=True)
#
#     def __str__(self):
#         return self.name
