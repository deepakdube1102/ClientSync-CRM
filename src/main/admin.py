from django.contrib import admin

from .models import Record

from .models import Customer

admin.site.register(Record)
admin.site.register(Customer)