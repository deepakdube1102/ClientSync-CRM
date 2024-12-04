from django.urls import path
from .views import about, add_record, contact, customer_dashboard, customer_login, customer_logout, customer_registration, download_all_records,  home, main_page, logout_users,  register_user, customer_record, delete_record, update_profile, update_record, user_profile, password_reset



urlpatterns = [
  path('', main_page, name= 'main'), 
  path('home/', home, name='home'), 
  path('user_profile/', user_profile, name='user_profile'),
  path('logout/', logout_users, name= 'logout'), 
  path('register/', register_user, name= 'register'),
  path('record/<int:pk>', customer_record, name='record'),
  path('delete_record/<int:pk>', delete_record, name='delete_record'),
  path('add_record/', add_record, name='add_record'),
  path('update_record/<int:pk>', update_record, name='update_record'),
  path('about/', about, name='about'),
  path('contact/', contact, name='contact'),
  path('records/download_all/', download_all_records, name='download_all_records'),
  path('password_reset/', password_reset, name='password_reset'),
  path('update_profile/', update_profile, name='update_profile'),
  path('customer/registration/', customer_registration, name='customer_registration'),
  path('customer/login/', customer_login, name='customer_login'),
  path('customer_dashboard/', customer_dashboard, name='customer_dashboard'),
  path('customer/logout/', customer_logout, name='customer_logout'),
  
]