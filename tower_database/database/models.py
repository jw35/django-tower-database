from django.core.exceptions import ValidationError
from django.db import models

import re

# Create your models here.

class Contact(models.Model):
    name = models.CharField(max_length=100, blank=True)
    publish = models.BooleanField(default=True)

    # Stringify as name if present, otherwise a list of contact methods
    def __str__(self):
        if self.name:
            return self.name
        else:
            return "-no name- (" + ' / '.join([str(s) for s in self.contactmethod_set.all()]) + ')'

    class Meta:
        ordering = ["name"]



class Tower(models.Model):

    # match times without two-digit hour (so 9:30 which should be 09:30)
    BAD_TIME_PATTERN = re.compile(r'(?<!\d)\d:\d\d(?!\d)')

    COUNTY_CHOICES = {
        'C': 'Cambridgeshire',
        'N': 'Norfolk',
    }
    DISTRICT_CHOICES = {
        'C': 'Cambridge',
        'E': 'Ely',
        'H': 'Huntingdon',
        'W': 'Wisbech',
    }
    RINGING_CHOICES = {
        'R': 'Regular',
        'O': 'Occasional',
        'N': 'None',
    }
    DAY_CHOICES = {
        'Mon': 'Monday',
        'Tue': 'Tuesday',
        'Wed': 'Wednesday',
        'Thu': 'Thursday',
        'Fri': 'Friday',
        'Sat': 'Saturday',
        'Sun': 'Sunday'
    }

    RING_TYPE_CHOICES = {
        'Full-circle': 'Full-circle ring',
        'Lightweight': 'Lightweight ring',
        'Carillon': 'Carillon',
        'C-Chine': 'Clock chime',
        'T-Chime': 'Tubular chime',
        'H-Chinme': 'Hemispherical chime',
        'Chime': 'Chime',
        'Display': 'Display bells',
        'Future': 'Future ring',
        'Other': 'Other bells'
    }

    RESTRICTION_CHOICES = {
        'None': 'None',
        'Bells only': 'Bells only',
        'Band only': 'Band only',
    }

    def bell_validator(value):
        if value < 3 or value > 16:
            raise ValidationError("Number of bells must be between 3 and 16")

    def time_validator(value):
        BAD_TIME_PATTERN = re.compile(r'(?<!\d)\d:\d\d(?!\d)')
        if BAD_TIME_PATTERN.search(value):
            raise ValidationError("Time value missing leading '0'")

    def weight_validator(value):
        WEIGHT_PATTERN = re.compile(r'\d+½? cwt|\d+-\d+-\d+')
        if not WEIGHT_PATTERN.fullmatch(value):
            raise ValidationError(f"Wrong format for weight (use '2-4-3-4' or '12cwt')")

    def note_validator(value):
        NOTE_PATTERN = re.compile(r'[A-G](#|b)?')

        if not NOTE_PATTERN.fullmatch(value):
            raise ValidationError(f"Wrong format for note (use A-G optionally followed by # or b)")

    def grid_validator(value):
        GRID_PATTERN = re.compile(r'(TL|TF)\d{6}')
        if not GRID_PATTERN.fullmatch(value):
            raise ValidationError(f"Wrong format for OS grid (use, e.g. AB123456")

    def postcode_validator(value):
        POSTCODE_PATTERN = re.compile(r'\w\w\d+ \d\w\w')
        if not POSTCODE_PATTERN.fullmatch(value):
            raise ValidationError(f"Wrong format for Postcode")

    place = models.CharField(max_length=100, help_text="Town or village containing the tower")
    county  = models.CharField(max_length=100, choices=COUNTY_CHOICES, default='Cambridgeshire')
    dedication = models.CharField(max_length=100, help_text="Church dedication. Use ‘St’ not ‘St.’; ‘and’ not ‘&’")
    full_dedication = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=10, choices=DISTRICT_CHOICES)
    include_dedication = models.BooleanField(default=False, help_text="needed for places with more than one tower [Cambridge], or for towers in different places that have the same name [Chesterton])")
    ringing = models.CharField(max_length=20, choices=RINGING_CHOICES)
    report = models.BooleanField(default=False, verbose_name="In annual report?")
    service = models.CharField(max_length=200, blank=True, validators=[time_validator], help_text="Short description of normal service ringing. No initial capital (unless day of week)")
    practice = models.CharField(max_length=200, blank=True, validators=[time_validator], help_text="Short description of normal practice ringing. No initial capital (unless day of week)")
    day = models.CharField(max_length=9, blank=True, choices=DAY_CHOICES, verbose_name="Practice day", help_text="Day of the week of main practice")
    week = models.CharField(max_length=50, blank=True, help_text="Week(s) of the month for main practice if not all [‘2nd, 5th’, 'alt']")
    check_before_traveling = models.BooleanField(default=False, help_text="Check before travelling to practices?")
    bells = models.PositiveIntegerField(null=True, blank=True, help_text="Number of ringable bells",validators=[bell_validator])
    ring_type = models.CharField(max_length=20, null=True, blank=True, choices=RING_TYPE_CHOICES)
    weight =models.CharField(max_length=50, blank=True, validators=[weight_validator], help_text="Use ‘15-3-13’ or ‘6cwt’")
    note = models.CharField(max_length=10, blank=True, validators=[note_validator], help_text="Use ‘b’ and ‘#’")
    gf = models.BooleanField(blank=True, null=True, verbose_name="Ground Floor?")
    os_grid= models.CharField(max_length=8, blank=True, validators=[grid_validator], verbose_name='OS Grid')
    postcode = models.CharField(max_length=10, blank=True, validators=[postcode_validator])
    lat = models.DecimalField(max_digits=5, blank=True, null=True, decimal_places=3)
    lng = models.DecimalField(max_digits=5, blank=True, null=True, decimal_places=3)
    website = models.URLField(blank=True)
    primary_contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL, related_name="tower_primary_set")
    contact_restrictions = models.CharField(max_length=10, choices=RESTRICTION_CHOICES, default='None')
    other_contacts = models.ManyToManyField(Contact, through="ContactMap", related_name="tower_oher_set")
    peals = models.PositiveIntegerField(null=True , blank=True)
    dove_towerid = models.CharField(max_length=10, blank=True, verbose_name="Dove TowerID")
    dove_ringid = models.CharField(max_length=10, blank=True, verbose_name="Dove RingID")
    towerbase_id = models.CharField(max_length=10, blank=True, verbose_name="Towerbase ID")
    notes = models.CharField(max_length=100, blank=True, help_text="For display, especially in the Annual Report")
    long_notes = models.TextField(blank=True, help_text="For display when space isn’t at a premium")
    maintainer_notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.place}  {self.dedication}'

    class Meta:
        ordering = ["place", "dedication"]
        constraints = [
            models.UniqueConstraint(fields=["place", "dedication"], name="unique_place_dedication",
                violation_error_message="Can't have two towers with the same place and dedication")
        ]



class ContactMap(models.Model):

    ROLE_CHOICES = {
        'Contact': 'Other contact',
        'Tower Captain': 'Tower Captain',
        'Ringing Master': 'Ringing Master',
        'Steeplekeeper': 'Steeplekeeper'
    }

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)

    class Meta:
        '''
        # Throws AttributeError: 'list' object has no attribute 'clone' ???
        constraints = [
            models.UniqueConstraint(
                fields=["tower", "contact"], name="unique_person_group"
            )
        ],
        '''
        #unique_together = ['tower', 'contact']
        ordering = ["tower", "role"]

    def __str__(self):
        return f'{self.role} - {self.tower} {self.contact}'



class ContactMethod(models.Model):

    CONTACT_TYPE_CHOICES = {
        'Email': 'Email',
        'Phone': 'Phone',
        'Other': 'Other',
    }

    contact_type = models.CharField(max_length=5, choices=CONTACT_TYPE_CHOICES)
    contact_value = models.CharField(max_length=200)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["contact_type", "contact_value", "contact"], name="unique_contact_type_value",
                violation_error_message="This contact method already exists for this contact")
        ]

    def __str__(self):
        return f'{self.contact_type}: {self.contact_value}'
