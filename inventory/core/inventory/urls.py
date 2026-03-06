from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('general-directorates/', views.general_directorates_list, name='general-directorates-list'),
    path('directorates/', views.directorates_list, name='directorates-list'),
    path('departments/', views.departments_list, name='departments-list'),
    path('offices/', views.offices_list, name='offices-list'),
    path('cities/', views.cities_list, name='cities-list'),
    path('areas/', views.areas_list, name='areas-list'),
    path('buildings/', views.buildings_list, name='buildings-list'),
    path('floors/', views.floors_list, name='floors-list'),
    path('rooms/', views.rooms_list, name='rooms-list'),
    path('common-areas/', views.common_areas_list, name='common-areas-list'),
    path('spaces/', views.spaces_list, name='spaces-list'),
    path('sockets/', views.sockets_list, name='sockets-list'),
    path('assignments/', views.assignments_list, name='assignments-list'),
    path('users/', views.users_list, name='users-list'),
    path('devices/', views.devices_list, name='devices-list'),
    path('peripherals/', views.peripherals_list, name='peripherals-list'),
    path('desktops/', views.desktops_list, name='desktops-list'),
    path('allInOnes/', views.allInOnes_list, name='allInOnes-list'),
    path('laptops/', views.laptops_list, name='laptops-list'),
    path('servers/', views.servers_list, name='servers-list'),
    path('upses/', views.upses_list, name='upses-list'),
    path('printers/', views.printers_list, name='printers-list'),
    path('switches/', views.switches_list, name='switches-list'),
    path('phones/', views.phones_list, name='phones-list'),
    path('queries/', views.queries_list, name='queries-list'),
    path('map/', views.map, name='map'),
    path("ping-device/", views.ping_device, name="ping_device"),




]