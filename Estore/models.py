from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.
#customers table
class Customer(models.Model):
    roles_choice = [('Standard', 'standard'),
             ('Gold', 'gold')]
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    roles = models.CharField(choices=roles_choice, default='standard', max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.username
    
#products table
class Product(models.Model):
    category_choices = [('TV', 'Tv'),
                        ('Acessories', 'accessories'),
                        ('Phone', 'phone'),
                        ('Laptop', 'laptop')]
    product_name = models.CharField(max_length=50, unique=True)
    product_quantity = models.PositiveIntegerField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_description = models.TextField()
    product_category = models.CharField(choices=category_choices, max_length=20)
    product_image = models.ImageField(upload_to='product_images/', validators=[FileExtensionValidator(['jpg', 'png'])])


    def __str__(self):
        return self.product_name

#orders table
class Order(models.Model):
    order_customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_created = models.DateTimeField(auto_now_add=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def total_quantity(self):
        return sum(item.order_quantity for item in self.items.all())
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())
    def __str__(self):
        return self.order_customer_id.username
    
#order each product table
class OrdereachTransaction(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_quantity = models.PositiveIntegerField()
    
    def total_price(self):
        return self.order_quantity * self.order_price
    def __str__(self):
        return f"{self.product.product_name} x {self.order_quantity}"

#cart table
class Cart(models.Model):
    cart_customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cart_created = models.DateTimeField(auto_now_add=True)

    def total_quantity(self):
        return sum(item.cart_quantity for item in self.items.all())
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())
    def __str__(self):
        return f"{self.cart_customer_id.username}"

#each item in cart table
class CarteachProduct(models.Model):
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart_price = models.DecimalField(max_digits=10, decimal_places=2)
    cart_quantity = models.PositiveIntegerField()

    def total_price(self):
        return self.cart_quantity * self.cart_price
    def __str__(self):
        return f"{self.product.product_name} x {self.cart_quantity}"
    
#Shipping table

class Shipment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    delivery_method_choices = [('standard', 'Standard'),
                                ('express', 'Express')]

    SHIPMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),             # Order received but not shipped
    ('processing', 'Processing'),       # Preparing shipment
    ('shipped', 'Shipped'),             # Sent to courier
    ('in_transit', 'In Transit'),       # On the way
    ('delivered', 'Delivered'),         # Reached destination
    ('failed', 'Delivery Failed'),      # Delivery attempt failed
    ('cancelled', 'Cancelled')          # Shipment cancelled
]
    customer_name = models.CharField(max_length=50)
    customer_email = models.EmailField()
    customer_phonenumber = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.PositiveIntegerField(default=0)
    method = models.CharField(choices=delivery_method_choices, default='standard', max_length=20)
    tracking_number = models.CharField(max_length=100, unique=True)
    paid_date = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=100)
    status = models.CharField(choices=SHIPMENT_STATUS_CHOICES, default='pending', max_length=20)

    def __str__(self):
        return f"{self.customer_name} x {self.tracking_number} x {self.status}"

#logging table
class Logging(models.Model):
    username_logging = models.ForeignKey(Customer, on_delete=models.CASCADE)
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username_logging.username} x {self.logged_at}"