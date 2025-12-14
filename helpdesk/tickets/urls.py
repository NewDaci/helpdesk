from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_tickets),
    path('create/', views.create_ticket),
    path('<int:ticket_id>/status/', views.update_ticket_status),
    path('<int:ticket_id>/assign/', views.assign_ticket),
    path('<int:ticket_id>/delete/', views.delete_ticket),
    path('<int:ticket_id>/comment/', views.add_comment),
    path('ticket-reports/', views.ticket_report),
]
