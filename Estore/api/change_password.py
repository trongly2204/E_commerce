from ..models import Customer
from django.contrib.auth.hashers import make_password, check_password

def change_customer_password(customer_id, old_password, new_password, confirm_password):
    customer = Customer.objects.filter(id=customer_id).first()

    if not customer:
        return (False, "Customer not found.")

    if not check_password(old_password, customer.password):
        return (False, "Your current password is incorrect.")

    if new_password != confirm_password:
        return (False, "New passwords do not match.")

    customer.password = make_password(new_password)
    customer.save()
    return (True, "Password changed successfully.")
