from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_page, name='product_page'),
    path('login/', views.login_page, name='login_page'), 
    path('signup/', views.signup_page, name='signup_page'),
    path('logout/', views.logout_page, name='logout_page'),
    path('cart/<int:customer_id>/', views.cart_page, name='cart_page'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear_cart/<int:customer_id>/', views.clear_cart, name='clear_cart'),
    path('check_out_page/<int:customer_id>/', views.check_out_page, name='check_out_page'),
    path('order_summary_page/<int:order_id>/', views.order_summary_page, name='order_summary_page'),
    path('user_order_page/<int:customer_id>/', views.user_order_page, name='user_order_page'),
    path('profile_page/<int:customer_id>/', views.profile_page, name='profile_page'),



]
