from django.urls import path

from catalog import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('request/', views.user_requests_view, name='user_requests'),
    path('request/delete/<int:pk>/', views.deleting_request_view, name='delete'),
    path('request/create/', views.creating_request_view, name='create'),
]