from django.contrib import admin
from .models import Category, Region, Type, Generation, Pokemon
# Register your models here.

admin.site.register(Category)
admin.site.register(Region)
admin.site.register(Type)
admin.site.register(Generation)
admin.site.register(Pokemon)