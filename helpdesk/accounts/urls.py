from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register),
    path('me/', views.me),
    path('update/', views.update_account),
    path('delete/', views.delete_account),
    path('logout/', views.logout),
    path('search/', views.search_users),
    path('<int:user_id>/role/', views.update_user_role),

]
