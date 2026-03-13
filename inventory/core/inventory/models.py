from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower
from django.utils import timezone

# =====================================================
# BASE ABSTRACT MODEL
# =====================================================
class LifeCycle(models.Model):
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(default=timezone.now)
    valid_to = models.DateField(null=True, blank=True)
    
    class Meta:
        abstract = True

# =====================================================
# GEOGRAPHICAL STRUCTURE
# =====================================================
class City(models.Model):
    name = models.CharField(max_length=150, unique=True)
    
    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
    
    def __str__(self):
        return self.name

class Area(models.Model):
    city = models.ForeignKey(
        City,
        on_delete=models.RESTRICT,
        related_name="areas"
    )
    name = models.CharField(max_length=150)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["city", "name"], name="unique_area_per_city")
        ]
    
    def __str__(self):
        return f"{self.city} - {self.name}"

class Building(LifeCycle):
    area = models.ForeignKey(
        Area,
        on_delete=models.RESTRICT,
        related_name="buildings"
    )
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=250, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Floor(LifeCycle):
    building = models.ForeignKey(
        Building,
        on_delete=models.RESTRICT,
        related_name="floors"
    )
    floor_number = models.IntegerField()

    class Meta:
        unique_together = ("building", "floor_number")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(floor_number__gte=-2),
                name="floor_number_min_minus_2",
                violation_error_message="Ο αριθμός ορόφου δεν μπορεί να είναι μικρότερος του -2."
            )
        ]

    def clean(self):
        if self.floor_number is not None and self.floor_number < -2:
            raise ValidationError(
                {"floor_number": "Ο αριθμός ορόφου δεν μπορεί να είναι μικρότερος του -2."}
            )

    def __str__(self):
        return f"{self.floor_number}"

# =====================================================
# COMMON AREA (Διάδρομοι, Κοινόχρηστοι Χώροι)
# =====================================================
class CommonArea(LifeCycle):
    AREA_TYPE_CHOICES = [
        ("corridor",    "Corridor"),
        ("lobby",       "Lobby"),
        ("server_room", "Server Room"),
        ("other",       "Other"),
    ]
    floor = models.ForeignKey(
        Floor,
        on_delete=models.RESTRICT,
        related_name="common_areas"
    )
    name = models.CharField(max_length=150)
    area_type = models.CharField(
        max_length=20,
        choices=AREA_TYPE_CHOICES,
        default="corridor"
    )

    class Meta:
        unique_together = ("floor", "name")

    @property
    def building(self):
        return self.floor.building

    def __str__(self):
        return f"{self.name} ({self.get_area_type_display()}) - Floor {self.floor.floor_number}"


class RoomManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            "floor__building__area__city"
        )


class Room(LifeCycle):
    floor = models.ForeignKey(
        Floor,
        on_delete=models.RESTRICT,
        related_name="rooms"
    )
    room_code = models.CharField(max_length=50)

    objects = RoomManager()

    class Meta:
        unique_together = ("floor", "room_code")

    @property
    def building(self):
        return self.floor.building

    def __str__(self):
        return self.room_code

class SpaceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            "room__floor__building__area__city"
        )


class Space(LifeCycle):
    room = models.ForeignKey(
        Room,
        on_delete=models.RESTRICT,
        related_name="spaces"
    )
    name = models.CharField(max_length=100)
    position_index = models.PositiveIntegerField()

    objects = SpaceManager()

    class Meta:
        ordering = ["position_index"]
        unique_together = (
            ("room", "position_index"),
        )
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "room",
                name="unique_space_name_per_room_ci"
            )
        ]
    @property
    def floor(self):
        return self.room.floor
    
    @property
    def device_count(self):
        return self.devices.count()  # peripherals are FK children of devices, not devices themselves
    
    @property
    def building(self):
        return self.room.floor.building

    def save(self, *args, **kwargs):
        # Normalize name: strip whitespace + title-case so "a", "A", "  a  " → "A"
        self.name = self.name.strip().capitalize()
        if not self.pk:
            last = Space.objects.filter(room=self.room).order_by("-position_index").first()
            self.position_index = (last.position_index + 1) if last else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

class Socket(LifeCycle):
    socket_code = models.CharField(
        max_length=50,
        help_text="Unique identifier for the socket."
    )
    space = models.ForeignKey(
        Space,
        on_delete=models.RESTRICT,
        related_name="sockets"
    )
    
    def clean(self):
        if self.space:
            building = self.space.room.floor.building
            exists = Socket.objects.filter(
                socket_code=self.socket_code,
                space__room__floor__building=building
            ).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError(
                    f"Socket code '{self.socket_code}' already exists in building '{building}'."
                )
    
    def __str__(self):
        return self.socket_code

# =====================================================
# ORGANIZATIONAL STRUCTURE
# =====================================================
class GeneralDirectorate(LifeCycle):
    name = models.CharField(max_length=200, unique=True)
    
    def __str__(self):
        return self.name

class Directorate(LifeCycle):
    name = models.CharField(max_length=200)
    general_directorate = models.ForeignKey(
        GeneralDirectorate,
        on_delete=models.RESTRICT,
        related_name="directorates"
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["general_directorate", "name"], name="unique_directorate_per_gd")
        ]
    
    def __str__(self):
        return self.name

class Department(LifeCycle):
    name = models.CharField(max_length=200)
    directorate = models.ForeignKey(
        Directorate,
        on_delete=models.RESTRICT,
        related_name="departments"
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["directorate", "name"], name="unique_department_per_directorate")
        ]
    
    def __str__(self):
        return self.name

class Office(LifeCycle):
    name = models.CharField(max_length=200)
    department = models.ForeignKey(
        Department,
        on_delete=models.RESTRICT,
        related_name="offices"
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["department", "name"], name="unique_office_per_department")
        ]
    
    def __str__(self):
        return self.name

# =====================================================
# USERS
# =====================================================
class User(LifeCycle):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("retired", "Retired"),
        ("transferred", "Transferred"),
    ]
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    general_directorate = models.ForeignKey(
        GeneralDirectorate,
        on_delete=models.RESTRICT
    )
    directorate = models.ForeignKey(
        Directorate,
        null=True,
        blank=True,
        on_delete=models.RESTRICT
    )
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.RESTRICT
    )
    office = models.ForeignKey(
        Office,
        null=True,
        blank=True,
        on_delete=models.RESTRICT
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )
    
    def clean(self):
        errors = {}

        # Directorate πρέπει να ανήκει στη δηλωμένη GeneralDirectorate
        if self.directorate and self.general_directorate:
            if self.directorate.general_directorate != self.general_directorate:
                errors["directorate"] = (
                    f"Το Directorate '{self.directorate}' δεν ανήκει "
                    f"στη GeneralDirectorate '{self.general_directorate}'."
                )

        # Department πρέπει να ανήκει στο δηλωμένο Directorate
        if self.department:
            if not self.directorate:
                errors["department"] = (
                    "Δεν μπορεί να οριστεί Department χωρίς Directorate."
                )
            elif self.department.directorate != self.directorate:
                errors["department"] = (
                    f"Το Department '{self.department}' δεν ανήκει "
                    f"στο Directorate '{self.directorate}'."
                )

        # Office πρέπει να ανήκει στο δηλωμένο Department
        if self.office:
            if not self.department:
                errors["office"] = (
                    "Δεν μπορεί να οριστεί Office χωρίς Department."
                )
            elif self.office.department != self.department:
                errors["office"] = (
                    f"Το Office '{self.office}' δεν ανήκει "
                    f"στο Department '{self.department}'."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.name} {self.surname}"

# =====================================================
# DEVICE (BASE)
# =====================================================
class Device(LifeCycle):
    USAGE_TYPE_CHOICES = [
        ("office", "Office"),
        ("laboratory", "Laboratory"),
        ("warehouse", "Warehouse"),
    ]
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100, blank=True, null=True)
    serial = models.CharField(max_length=100, unique=True)
    registration_code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )
    ip_address = models.CharField(max_length=100, blank=True, null=True, unique=True)
    mac_address = models.CharField(max_length=50, blank=True, null=True, unique=True)
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPE_CHOICES)
    space = models.ForeignKey(
        Space,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="devices",
        help_text="Space where this device is located (για κανονικά γραφεία/δωμάτια)"
    )
    common_area = models.ForeignKey(
        "CommonArea",
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="devices",
        help_text="Common area where this device is located (για διαδρόμους/κοινόχρηστους χώρους)"
    )
    socket = models.ForeignKey(
        Socket,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="devices",
        help_text="Socket this device is plugged into (optional)"
    )

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"

    def clean(self):
        # Ακριβώς ένα από τα δύο πρέπει να οριστεί
        if not self.space and not self.common_area:
            raise ValidationError(
                "Πρέπει να οριστεί είτε Space είτε Common Area."
            )
        if self.space and self.common_area:
            raise ValidationError(
                "Δεν μπορούν να οριστούν και Space και Common Area ταυτόχρονα."
            )

    @property
    def room(self):
        return self.space.room if self.space else None

    @property
    def floor(self):
        if self.space:
            return self.space.floor
        if self.common_area:
            return self.common_area.floor
        return None

    @property
    def building(self):
        if self.space:
            return self.space.building
        if self.common_area:
            return self.common_area.floor.building
        return None

    @property
    def location(self):
        """Επιστρέφει την τοποθεσία ανεξαρτήτως τύπου (Space ή CommonArea)."""
        if self.space:
            return f"{self.space.building} / {self.space.floor} / {self.room} / {self.space}"
        if self.common_area:
            return self.common_area
        return ""

    
    def get_specific_device(self):
        """Get the actual child instance (LaptopComputer, Printer, etc.)"""
        for attr in ['laptopcomputer', 'desktopcomputer', 'allinonecomputer',
                     'servercomputer', 'printer', 'ups', 'accesspoint',
                     'switch', 'phone']:
            if hasattr(self, attr):
                return getattr(self, attr)
        return self
    
    def __str__(self):
        return f"{self.brand} - {self.serial}"

# =====================================================
# DEVICE SUBCLASSES (Multi-table Inheritance)
# =====================================================
class DesktopComputer(Device):
    device_label = "Desktop"
    cpu = models.CharField(max_length=100)
    ram_gb = models.IntegerField()
    storage_gb = models.IntegerField()


class AllInOneComputer(Device):
    device_label = "All-in-One"
    cpu = models.CharField(max_length=100)
    ram_gb = models.IntegerField()
    storage_gb = models.IntegerField()
    screen_size = models.CharField(max_length=10)


class LaptopComputer(Device):
    device_label = "Laptop"
    cpu = models.CharField(max_length=100)
    ram_gb = models.IntegerField()
    storage_gb = models.IntegerField()
    screen_size = models.CharField(max_length=10)


class ServerComputer(Device):
    device_label = "Server"
    rack_unit = models.CharField(max_length=50)


class Printer(Device):
    device_label = "Printer"
    PRINTER_TYPE_CHOICES = [
        ("laser", "Laser"),
        ("inkjet", "Inkjet"),
        ("multifunction", "Multifunction"),
    ]
    printer_type = models.CharField(max_length=20, choices=PRINTER_TYPE_CHOICES)


class Ups(Device):
    device_label = "UPS"
    capacity_va = models.IntegerField()
    
    class Meta:
        verbose_name = "UPS"
        verbose_name_plural = "UPS units"


class AccessPoint(Device):
    device_label = "Access Point"
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)


class Switch(Device):
    device_label = "Switch"
    SWITCH_LAYER_CHOICES = [
        ("L2", "Layer 2"),
        ("L3", "Layer 3"),
        ("L2+L3", "Layer 2 + Layer 3"),
    ]
    layer_capability = models.CharField(
        max_length=10,
        choices=SWITCH_LAYER_CHOICES,
        default="L2"
    )
    total_ports = models.IntegerField()
    poe_supported = models.BooleanField(default=False)
    poe_budget_watts = models.IntegerField(null=True, blank=True)
    uplink_speed = models.CharField(max_length=20, blank=True, null=True)
    downlink_speed = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"Switch {self.brand} {self.model or ''} (SN: {self.serial})"


class Phone(Device):
    device_label = "Phone"
    PHONE_TYPE_CHOICES = [
        ("analog", "Analog"),
        ("digital", "Digital"),
    ]
    phone_type = models.CharField(max_length=20, choices=PHONE_TYPE_CHOICES)

# =====================================================
# PERIPHERALS
# =====================================================
class Peripheral(LifeCycle):
    PERIPHERAL_TYPE_CHOICES = [
        ("keyboard", "Keyboard"),
        ("monitor", "Monitor"),
        ("mouse", "Mouse"),
    ]
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="peripherals"
    )
    peripheral_type = models.CharField(max_length=20, choices=PERIPHERAL_TYPE_CHOICES)
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    specifications = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.peripheral_type} ({self.device})"

# =====================================================
# ASSIGNMENTS
# =====================================================
class Assignment(models.Model):
    ASSIGNMENT_TYPE_CHOICES = [
        ("primary", "Primary"),
        ("shared", "Shared"),
        ("temporary", "Temporary"),
    ]
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    device = models.ForeignKey(Device, on_delete=models.RESTRICT, related_name="assignments")
    assignment_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    assignment_type = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_TYPE_CHOICES,
        default="primary"
    )
    notes = models.TextField(blank=True, null=True)
    
    def clean(self):
        if self.end_date and self.end_date < self.assignment_date:
            raise ValidationError("End date cannot be before assignment date.")
