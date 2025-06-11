from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    path('', views.communication_list, name='communication_list'),
    # Messages
    path('messages/', views.message_list, name='messages_list'),
    path('message/create/', views.message_create, name='message_create'),
    path('message/<int:message_id>/view/', views.message_view, name='message_view'),
    path('message/<int:message_id>/reply/', views.message_reply, name='message_reply'),
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
