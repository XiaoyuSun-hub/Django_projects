from django.contrib import admin

# Register your models here.

from cats.models import Breed, Cat

# Register your models here.

admin.site.register(Breed)
admin.site.register(Cat)