from django.contrib import admin
from .models import Product, Order, Customer, Cart, Shipment, Logging, CarteachProduct, OrdereachTransaction


# Register your models here.
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(Shipment)
admin.site.register(Logging)
admin.site.register(CarteachProduct)
admin.site.register(OrdereachTransaction)