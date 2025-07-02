import random
import string
from ..models import Shipment


def tracking_number_api(length=10):
    while True:
        tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Shipment.objects.filter(tracking_number =tracking_number).exists():
            return tracking_number