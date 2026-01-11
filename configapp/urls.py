from django.urls import path
from . import views

app_name = 'configapp'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),

    path('register/', views.register_view, name='register'),
    path('verify/<int:user_id>/', views.verify_view, name='verify'),
    path('verify/<int:user_id>/resend/', views.resend_verification, name='resend_verification'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
