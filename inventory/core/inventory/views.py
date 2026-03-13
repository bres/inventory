from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Prefetch, Q
from django.db.models import Count

import subprocess
import platform
from .models import (
    User,
    GeneralDirectorate,
    Directorate,
    Department,
    Office,
    Peripheral,
    Device,
    City,
    Area,
    Building,
    Floor,
    Room,
    Space,
    Socket,
    Assignment,
    DesktopComputer,
    LaptopComputer,
    AllInOneComputer,
    Printer,
    Ups,
    Switch,
    ServerComputer,
    Phone,
    CommonArea,
    AccessPoint
)


# Create your views here.
def dashboard(request):
    context = {
        "general_directorates_count": GeneralDirectorate.objects.count(),
        "directorates_count": Directorate.objects.count(),
        "departments_count": Department.objects.count(),
        "offices_count": Office.objects.count(),
        "cities_count": City.objects.count(),
        "areas_count": Area.objects.count(),
        "buildings_count": Building.objects.count(),
        "floors_count": Floor.objects.count(),
        "rooms_count": Room.objects.count(),
        "common_areas_count": CommonArea.objects.count(),
        "spaces_count": Space.objects.count(),
        "sockets_count": Socket.objects.count(),
        "assignments_count": Assignment.objects.count(),
        "users_count": User.objects.count(),
        "devices_count": Device.objects.count(),
        "peripherals_count": Peripheral.objects.count(),
        "desktops_count": DesktopComputer.objects.count(),
        "laptops_count": LaptopComputer.objects.count(),
        "servers_count": ServerComputer.objects.count(),
        "allInOnes_count": AllInOneComputer.objects.count(),
        "printers_count": Printer.objects.count(),
        "switches_count": Switch.objects.count(),
        "access_points_count": AccessPoint.objects.count(),
        "upses_count": Ups.objects.count(),
        "phones_count": Phone.objects.count(),
    }
    return render(request, "inventory/dashboard.html", context)


def general_directorates_list(request):
    general_directorates = GeneralDirectorate.objects.annotate(
        directorates_count=Count('directorates', distinct=True),
        departments_count=Count('directorates__departments', distinct=True),
        offices_count=Count('directorates__departments__offices', distinct=True),
        users_count=Count('directorates__departments__offices__user', distinct=True),
    )
    return render(request, 'inventory/general-directorates-list.html', {'general_directorates': general_directorates})

def directorates_list(request):
    directorates = Directorate.objects.select_related('general_directorate').annotate(
        departments_count=Count('departments', distinct=True),
        offices_count=Count('departments__offices', distinct=True),
        users_count=Count('departments__offices__user', distinct=True),
    )
    return render(request, 'inventory/directorates-list.html', {'directorates': directorates})


def departments_list(request):
    departments = Department.objects.select_related('directorate__general_directorate').annotate(
        offices_count=Count('offices', distinct=True),
        users_count=Count('offices__user', distinct=True),
    )
    return render(request, 'inventory/departments-list.html', {'departments': departments})


def offices_list(request):
    offices = Office.objects.select_related(
        'department__directorate__general_directorate'
    ).annotate(
        users_count=Count('user', distinct=True),
    )
    return render(request, 'inventory/offices-list.html', {'offices': offices})


def cities_list(request):
    cities = City.objects.annotate(
        areas_count=Count("areas", distinct=True),
        buildings_count=Count("areas__buildings", distinct=True),
        floors_count=Count("areas__buildings__floors", distinct=True),
        desktops_count=Count(
            "areas__buildings__floors__rooms__spaces__devices__desktopcomputer",
            distinct=True,
        ),
        allinones_count=Count(
            "areas__buildings__floors__rooms__spaces__devices__allinonecomputer",
            distinct=True,
        ),
        laptops_count=Count(
            "areas__buildings__floors__rooms__spaces__devices__laptopcomputer",
            distinct=True,
        ),
        printers_count=Count(
            "areas__buildings__floors__rooms__spaces__devices__printer", distinct=True
        ),
        ups_count=Count(
            "areas__buildings__floors__rooms__spaces__devices__ups", distinct=True
        ),
        servers_count=Count(
            "areas__buildings__floors__rooms__spaces__devices__servercomputer",
            distinct=True,
        ),
        switches_count=Count(
            "areas__buildings__floors__rooms__spaces__devices__switch", distinct=True
        ),
        accesspoints_count=Count(
            "areas__buildings__floors__rooms__spaces__devices__accesspoint", distinct=True
        ),
        phones_count=Count(
            "areas__buildings__floors__rooms__spaces__devices__phone", distinct=True
        ),
        peripherals_count=Count(
            "areas__buildings__floors__rooms__spaces__devices__peripherals",
            distinct=True,
        ),
    )
    return render(request, "inventory/cities-list.html", {"cities": cities})


def areas_list(request):
    areas = Area.objects.select_related("city").annotate(
        buildings_count=Count("buildings", distinct=True),
        floors_count=Count("buildings__floors", distinct=True),
        desktops_count=Count(
            "buildings__floors__rooms__spaces__devices__desktopcomputer", distinct=True
        ),
        allinones_count=Count(
            "buildings__floors__rooms__spaces__devices__allinonecomputer", distinct=True
        ),
        laptops_count=Count(
            "buildings__floors__rooms__spaces__devices__laptopcomputer", distinct=True
        ),
        servers_count=Count(
            "buildings__floors__rooms__spaces__devices__servercomputer", distinct=True
        ),
        printers_count=Count(
            "buildings__floors__rooms__spaces__devices__printer", distinct=True
        ),
        ups_count=Count(
            "buildings__floors__rooms__spaces__devices__ups", distinct=True
        ),
        switches_count=Count(
            "buildings__floors__rooms__spaces__devices__switch", distinct=True
        ),
        accesspoints_count=Count(
            "buildings__floors__rooms__spaces__devices__accesspoint", distinct=True
        ),

        phones_count=Count(
            "buildings__floors__rooms__spaces__devices__phone", distinct=True
        ),
        peripherals_count=Count(
            "buildings__floors__rooms__spaces__devices__peripherals", distinct=True
        ),
    )
    return render(request, "inventory/areas-list.html", {"areas": areas})


def buildings_list(request):
    buildings = Building.objects.select_related("area__city").annotate(
        floors_count=Count("floors", distinct=True),
        rooms_count=Count("floors__rooms", distinct=True),

        desktops_count=Count(
            "floors__rooms__spaces__devices__desktopcomputer", distinct=True
        ),
        allinones_count=Count(
            "floors__rooms__spaces__devices__allinonecomputer", distinct=True
        ),
        laptops_count=Count(
            "floors__rooms__spaces__devices__laptopcomputer", distinct=True
        ),
        servers_count=Count(
            "floors__rooms__spaces__devices__servercomputer", distinct=True
        ),
        printers_count=Count("floors__rooms__spaces__devices__printer", distinct=True),
        ups_count=Count("floors__rooms__spaces__devices__ups", distinct=True),
        accesspoints_count=Count("floors__rooms__spaces__devices__accesspoint", distinct=True),
        switches_count=Count("floors__rooms__spaces__devices__switch", distinct=True),
        phones_count=Count("floors__rooms__spaces__devices__phone", distinct=True),
        peripherals_count=Count(
            "floors__rooms__spaces__devices__peripherals", distinct=True
        ),
    )
    return render(request, "inventory/buildings-list.html", {"buildings": buildings})


def floors_list(request):
    floors = Floor.objects.select_related("building__area__city").annotate(
        rooms_count=Count("rooms", distinct=True),
        common_areas_count=Count("common_areas", distinct=True),
        desktops_count=Count("rooms__spaces__devices__desktopcomputer", distinct=True),
        allinones_count=Count(
            "rooms__spaces__devices__allinonecomputer", distinct=True
        ),
        laptops_count=Count("rooms__spaces__devices__laptopcomputer", distinct=True),
        servers_count=Count("rooms__spaces__devices__servercomputer", distinct=True),
        printers_count=Count("rooms__spaces__devices__printer", distinct=True),
        ups_count=Count("rooms__spaces__devices__ups", distinct=True),
        switches_count=Count("rooms__spaces__devices__switch", distinct=True),
        phones_count=Count("rooms__spaces__devices__phone", distinct=True),
        accesspoints_count=Count("rooms__spaces__devices__accesspoint", distinct=True),
        peripherals_count=Count("rooms__spaces__devices__peripherals", distinct=True),
    )
    return render(request, "inventory/floors-list.html", {"floors": floors})


def common_areas_list(request):
    common_areas = CommonArea.objects.select_related(
        "floor__building__area__city"
    ).annotate(
        desktops_count=Count("devices__desktopcomputer", distinct=True),
        allinones_count=Count("devices__allinonecomputer", distinct=True),
        laptops_count=Count("devices__laptopcomputer", distinct=True),
        servers_count=Count("devices__servercomputer", distinct=True),
        printers_count=Count("devices__printer", distinct=True),
        ups_count=Count("devices__ups", distinct=True),
        switches_count=Count("devices__switch", distinct=True),
        phones_count=Count("devices__phone", distinct=True),
        accesspoints_count=Count("devices__accesspoint", distinct=True),
        peripherals_count=Count("devices__peripherals", distinct=True),
    )
    return render(
        request, "inventory/common-areas-list.html", {"common_areas": common_areas}
    )


def rooms_list(request):
    rooms = Room.objects.select_related('floor__building__area__city').annotate(
        spaces_count=Count('spaces', distinct=True),
        desktops_count=Count('spaces__devices__desktopcomputer', distinct=True),
        allinones_count=Count('spaces__devices__allinonecomputer', distinct=True),
        laptops_count=Count('spaces__devices__laptopcomputer', distinct=True),
        servers_count=Count('spaces__devices__servercomputer', distinct=True),
        printers_count=Count('spaces__devices__printer', distinct=True),
        ups_count=Count('spaces__devices__ups', distinct=True),
        switches_count=Count('spaces__devices__switch', distinct=True),
        phones_count=Count('spaces__devices__phone', distinct=True),
        accesspoints_count=Count('spaces__devices__accesspoint', distinct=True),
        peripherals_count=Count('spaces__devices__peripherals', distinct=True),
    )
    return render(request, 'inventory/rooms-list.html', {'rooms': rooms})


def spaces_list(request):
    spaces = Space.objects.select_related('room__floor__building__area__city').annotate(
        devices_count=Count('devices', distinct=True),
        sockets_count=Count('sockets', distinct=True),
        desktops_count=Count('devices__desktopcomputer', distinct=True),
        allinones_count=Count('devices__allinonecomputer', distinct=True),
        laptops_count=Count('devices__laptopcomputer', distinct=True),
        servers_count=Count('devices__servercomputer', distinct=True),
        printers_count=Count('devices__printer', distinct=True),
        ups_count=Count('devices__ups', distinct=True),
        switches_count=Count('devices__switch', distinct=True),
        phones_count=Count('devices__phone', distinct=True),
        accesspoints_count=Count('devices__accesspoint', distinct=True),
        peripherals_count=Count('devices__peripherals', distinct=True),
    )
    return render(request, 'inventory/spaces-list.html', {'spaces': spaces})


def sockets_list(request):
    sockets = Socket.objects.select_related('space__room__floor__building__area__city').annotate(
        devices_count=Count('devices', distinct=True),
    )
    return render(request, 'inventory/sockets-list.html', {'sockets': sockets})


def assignments_list(request):
    assignments = Assignment.objects.select_related(
        'user',
        'device__space__room__floor__building__area__city',
        'device__common_area',
    )
    return render(request, 'inventory/assignments-list.html', {'assignments': assignments})


def users_list(request):
    users = User.objects.select_related(
        'general_directorate',
        'directorate',
        'department',
        'office',
    )
    return render(request, 'inventory/users-list.html', {'users': users})


def devices_list(request):
    devices = Device.objects.all()
    return render(request, "inventory/devices-list.html", {"devices": devices})


# def desktops_list(request):
#     desktops =DesktopComputer.objects.all()
#     return render(request,'inventory/desktops-list.html',{'desktops':desktops})


def desktops_list(request):
    desktops = DesktopComputer.objects.prefetch_related(
        Prefetch(
            "device_ptr__assignments",  # ← related_name
            queryset=Assignment.objects.filter(
                Q(end_date__isnull=True) | Q(end_date__gte=timezone.now().date())
            ).select_related("user"),
        ),
        Prefetch(
            "device_ptr__peripherals",  # ← related_name
            queryset=Peripheral.objects.all(),
        ),
    )
    return render(request, "inventory/desktops-list.html", {"desktops": desktops,'office_count': desktops.filter(usage_type='office').count(),
        'lab_count': desktops.filter(usage_type='laboratory').count()})


def laptops_list(request):
    laptops = LaptopComputer.objects.select_related('space__room__floor__building__area__city').prefetch_related(
        'device_ptr__assignments__user',
        'device_ptr__peripherals',
    )
    return render(request, 'inventory/laptops-list.html', {'laptops': laptops})


def servers_list(request):
    servers = ServerComputer.objects.select_related('space__room__floor__building__area__city').prefetch_related(
        'device_ptr__assignments__user',
    )
    return render(request, 'inventory/servers-list.html', {'servers': servers})


def allInOnes_list(request):
    allinones = AllInOneComputer.objects.select_related('space__room__floor__building__area__city').prefetch_related(
        'device_ptr__assignments__user',
        'device_ptr__peripherals',
    )
    return render(request, 'inventory/allInOnes-list.html', {'allinones': allinones})


def printers_list(request):
    printers = Printer.objects.select_related('space__room__floor__building__area__city').prefetch_related(
        'device_ptr__assignments__user',
    )
    return render(request, 'inventory/printers-list.html', {'printers': printers})


def upses_list(request):
    upses = Ups.objects.select_related('space__room__floor__building__area__city').prefetch_related(
        'device_ptr__assignments__user',
    )
    return render(request, 'inventory/upses-list.html', {'upses': upses})


def peripherals_list(request):
    peripherals = Peripheral.objects.select_related('device__space__room__floor__building__area__city')
    return render(request, 'inventory/peripherals-list.html', {'peripherals': peripherals})


def switches_list(request):
    switches = Switch.objects.select_related('space__room__floor__building__area__city').prefetch_related(
        'device_ptr__assignments__user',
    )
    return render(request, 'inventory/switches-list.html', {'switches': switches})

def access_points_list(request):
    accesspoints = AccessPoint.objects.select_related('space__room__floor__building__area__city').prefetch_related(
        'device_ptr__assignments__user',
    )
    return render(request, 'inventory/access-points-list.html', {'accesspoints':accesspoints})


def phones_list(request):
    phones = Phone.objects.select_related('space__room__floor__building__area__city').prefetch_related(
        'device_ptr__assignments__user',
    )
    return render(request, 'inventory/phones-list.html', {'phones': phones})


def queries_list(request):
    # phones =Phone.objects.all()
    return render(request, "inventory/queries-list.html")


def map(request):
    # phones =Phone.objects.all()
    return render(request, "inventory/map.html")


def ping_device(request):
    ip = request.GET.get("ip")

    if not ip:
        return render(
            request,
            "ping_result.html",
            {"ip": None, "reachable": None, "output": "No IP provided."},
        )

    # Windows uses -n, Linux/macOS use -c
    param = "-n" if platform.system().lower() == "windows" else "-c"

    ping = subprocess.run(
        ["ping", param, "1", ip],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    reachable = ping.returncode == 0

    return render(
        request,
        "inventory/ping_result.html",
        {"ip": ip, "reachable": reachable, "output": ping.stdout},
    )
