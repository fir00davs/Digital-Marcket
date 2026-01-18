from django.urls import path
from .views import *

urlpatterns = [
    path('', MainPage.as_view(), name='main'),
    path('product/<slug:slug>/', ProductDetail.as_view(), name='detail'),
    path('registration/', auth_register_page, name='auth_reg'),
    path('authentication/', auth_login_page, name='auth'),
    path('login/', login_user_view, name='login'),
    path('logout/', logout_user_view, name='logout'),
    path('register/', register_user_view, name='register'),
    path('category/<slug:slug>/', ProductByCategory.as_view(), name='category'),
    path('action_favorite/<slug:slug>/', save_favorite_product, name='action_fav'),
    path('favorites/', FavoriteList.as_view(), name='favs'),
    path('action_cart/<slug:slug>/<str:action>/', add_or_delete_view, name='action_cart'),
    path('action_cart/clear/', clear_cart_view, name='clear_cart'),
    path('basket/', my_cart_view, name='basket'),
    path('checkout/', checkout_view, name='checkout'),
    path('payment/', create_checkout_session, name='payment'),
    path('success/', success_payment, name='success'),
    path('profile/', profile_customer_view, name='profile'),
    path('edit_profile/', edit_profile_view, name='edit_profile'),
    path('search/', search_products, name='search'),



]

