# E_commerce
# 🛍️ Django E-Commerce Store

This is a basic e-commerce web application built with Django. It includes the following core features:

- Product catalog and homepage
- Cart system with add/remove/update functionality
- Automatic cart expiration after 20 minutes of inactivity
- Checkout with simulated PayPal payment
- Order summary and shipment tracking
- User authentication (sign up, login, logout)
- Profile page with password change support

---

## 🔧 Features

### 🛒 Cart
- Add and remove products
- Quantity validation based on stock
- Cart timeout clears after 20 minutes of inactivity
- Cart displayed per user

### 💳 Checkout
- Shipping method selection (Standard/Express)
- Shipping cost is dynamically calculated
- Total cost includes shipping
- Simulated PayPal API used for payment

### 📦 Orders & Shipping
- Orders are stored with line items and shipping details
- Tracking number is randomly generated (non-duplicated)

### 👤 Profile Page
- View user info and past orders
- Change password with validation
