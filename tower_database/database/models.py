from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

import re

# Create your models here.

class Contact(models.Model):
    name = models.CharField(max_length=100, blank=True, help_text="Contact name (with or without title), or role")
    phone = models.CharField(max_length=100, blank=True, help_text="Contact phone number")
    phone2 = models.CharField(max_length=100, blank=True, verbose_name="Phone", help_text="Alternate phone number")
    email = models.EmailField(max_length=100, blank=True, help_text="Contact email address")

    def __str__(self):
        return ' / '.join([f for f in (self.name, self.phone, self.phone2, self.email) if f != ''])

    class Meta:
        ordering = ["name", "email"]
        unique_together = "name", "phone", "phone2", "email"
        constraints = [
            models.CheckConstraint(
                condition=~Q(name='') | ~Q(phone = '') | ~Q(phone2 = '') | ~Q(email=''),
                name="no_non_blank_contacts",
                violation_error_message="Contacts can't be entirely blank"
            ),
        ]

class TowerConstants():

    # Probable times without leading '0''
    BAD_TIME_PATTERN = re.compile(r'(?<!\d)\d:\d\d(?!\d)')

    # Acceptable weight patterns
    WEIGHT_PATTERN = re.compile(r'\d+½? cwt|\d+-\d+-\d+')

    # Acceptable note patterns (with no Cb or E#)
    NOTE_PATTERN = re.compile(r'([DGA](#|b)?)|([CF]#?)|([EB]b?)')

    # 6 figure NAtional Grid in the Association area
    GRID_PATTERN = re.compile(r'(TL|TF)\d{6}')

    # Acceptable PostCodes (probably overly restrictive)
    POSTCODE_PATTERN = re.compile(r'\w\w\d+ \d\w\w')

    # Match 'check' if not followed by a Bank Holiday reference, 'by arrangement' and 'by invitation'
    CHECK_PATTERN = re.compile(r'check(?! if Bank Holiday)|by arrangement|by invitation', re.IGNORECASE)

    # Valid phrases for week patterns
    WEEK_PHRASE_PATTERN = re.compile(r'1st|2nd|3rd|4th|5th|not')

class Tower(models.Model):

    class Counties(models.TextChoices):
        CAMBRIDGESHIRE = "C"
        NORFOLK = "N"

    class Districts(models.TextChoices):
        CAMBRIDGE = 'C'
        ELY = 'E'
        HUNTINGDON= 'H'
        WISBECH = 'W'

    class RingingStatus(models.TextChoices):
        REGULAR = 'R'
        OCCASIONAL = 'O'
        NONE = 'N'

    class Days(models.TextChoices):
        MONDAY = 'Mon'
        TUESDAY = 'Tue'
        WEDNESDAY = 'Wed'
        THURSDAY = 'Thu'
        FRIDAY = 'Fri'
        SATURDAY = 'Sat'
        SUNDAY = 'Sun'

    class RingTypes(models.TextChoices):
        FULL = 'Full', 'Full-circle ring'
        LIGHT = 'Light', 'Lightweight ring'
        CARILLON = 'Carillon', 'Carillon'
        C_CHIME = 'C-chine', 'Clock chime'
        T_CHIME = 'T-chime', 'Tubular chime'
        H_CHIME = 'H-chinme', 'Hemispherical chime'
        CHIME = 'Chime', 'Chime'
        DISPLAY = 'Display', 'Display bells'
        FUTURE = 'Future', 'Future ring'
        OTHER = 'Other', 'Other bells'


    class ContactUses(models.TextChoices):
        ALL = 'All'
        BELLS_ONLY = 'Bells only'
        BAND_ONLY = 'Band only'
        NONE = 'None'

    def bell_validator(value):
        if value < 3 or value > 12:
            raise ValidationError("Number of bells must be between 3 and 12")

    def time_validator(value):
        if TowerConstants.BAD_TIME_PATTERN.search(value):
            raise ValidationError("Time value missing leading '0'")


    def weight_validator(value):
        if not TowerConstants.WEIGHT_PATTERN.fullmatch(value):
            raise ValidationError(f"Wrong format for weight (use e.g. '2-4-3-4' or '12cwt')")

    def note_validator(value):
        if not TowerConstants.NOTE_PATTERN.fullmatch(value):
            raise ValidationError(f"Wrong format for note (use A-G optionally followed by # or b if appropriate)")

    def grid_validator(value):
        if not TowerConstants.GRID_PATTERN.fullmatch(value):
            raise ValidationError(f"Wrong format for OS grid (use, e.g. TL123456")

    def postcode_validator(value):
        if not TowerConstants.POSTCODE_PATTERN.fullmatch(value):
            raise ValidationError(f"Wrong format for Postcode")

    place = models.CharField(max_length=100, help_text="Town or village containing the tower")
    county  = models.CharField(max_length=100, choices=Counties, default='Cambridgeshire')
    dedication = models.CharField(max_length=100, help_text="Church dedication. Use ‘St’ not ‘St.’; ‘and’ not ‘&’")
    full_dedication = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=10, choices=Districts)
    include_dedication = models.BooleanField(default=False, help_text="For places with more than one tower [Cambridge], or for towers in different places that have the same name [Chesterton])")
    ringing_status = models.CharField(max_length=20, blank=True, choices=RingingStatus, help_text="Full-circle ringing status")
    report = models.BooleanField(default=False, verbose_name="In annual report?")
    service = models.CharField(max_length=200, blank=True, validators=[time_validator], help_text="Short description of normal service ringing. No initial capital (unless day of week)")
    practice = models.CharField(max_length=200, blank=True, validators=[time_validator], help_text="Short description of normal practice ringing. No initial capital (unless day of week)")
    practice_day = models.CharField(max_length=9, blank=True, choices=Days, help_text="Day of the week of main practice")
    practice_weeks = models.CharField(max_length=50, blank=True, help_text="Week(s) of the month for main practice if not all [‘2nd, 5th’, 'alt']")
    travel_check = models.BooleanField(default=False, help_text="Check before travelling to practices?")
    bells = models.PositiveIntegerField(null=True, blank=True, help_text="Number of ringable bells",validators=[bell_validator])
    ring_type = models.CharField(max_length=20, blank=True, choices=RingTypes)
    weight =models.CharField(max_length=50, blank=True, validators=[weight_validator], help_text="Use ‘15-3-13’ or ‘6cwt’")
    note = models.CharField(max_length=10, blank=True, validators=[note_validator], help_text="Use ‘b’ and ‘#’")
    gf = models.BooleanField(blank=True, null=True, verbose_name="Ground Floor?")
    os_grid= models.CharField(max_length=8, blank=True, validators=[grid_validator], verbose_name='OS Grid')
    postcode = models.CharField(max_length=10, blank=True, validators=[postcode_validator])
    lat = models.DecimalField(max_digits=5, blank=True, null=True, decimal_places=3)
    lng = models.DecimalField(max_digits=5, blank=True, null=True, decimal_places=3)
    primary_contact = models.ForeignKey(Contact, blank=True, null=True, on_delete=models.PROTECT, related_name="tower_primary_set")
    contact_use = models.CharField(max_length=10, choices=ContactUses, default='All', help_text="Intended use of contact details")
    other_contacts = models.ManyToManyField(Contact, through="ContactMap", related_name="tower_oher_set")
    peals = models.PositiveIntegerField(null=True , blank=True, help_text="Peals in most recent Annual Report")
    dove_towerid = models.CharField(max_length=10, blank=True, verbose_name="Dove TowerID")
    dove_ringid = models.CharField(max_length=10, blank=True, verbose_name="Dove RingID")
    towerbase_id = models.CharField(max_length=10, blank=True, verbose_name="Towerbase ID")
    notes = models.CharField(max_length=100, blank=True, help_text="For display, especially in the Annual Report")
    long_notes = models.TextField(blank=True, help_text="For display when space isn’t at a premium")
    maintainer_notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.place}  {self.dedication}'

    def clean(self):

        """
        Make various cross-field checks. Many of these are a bit heuristic.
        """

        errors = []

        # ringing & saervice/practice
        if self.ringing_status == Tower.RingingStatus.NONE and (self.service or self.practice):
            errors.append(f"Riging Status '{self.get_ringing_status_display()}' inconsistent with Service or Practice")

        # day
        if (self.practice and not self.practice_day) or (self.get_practice_day_display() not in self.practice):
            errors.append(f"Practice Day '{self.practice_day}' inconsistent with Practice '{self.practice}'")

        # Practice
        if TowerConstants.CHECK_PATTERN.search(self.practice) and not self.travel_check:
            errors.append(f"Practice '{self.practice}' mentions 'check' but Travel Check not set")

        # Week
        if not TowerConstants.CHECK_PATTERN.search(self.practice):
            for phrase in TowerConstants.WEEK_PHRASE_PATTERN.findall(self.practice):
                if phrase not in self.practice_weeks:
                    errors.append(f"'{phrase}' appears in in Practice '{self.practice}' but not in Practice Weeks '{self.practice_weeks}'")


        for phrase in self.practice_weeks.split(', '):
            if 'BH' in phrase:
                if 'Bank' not in self.practice:
                    errors.append(f"'BH' in Practice Weeks '{self.practice_weeks}'  but 'Bank' not in Practice '{self.practice}'")
            elif phrase not in self.practice:
                errors.append(f"'{phrase}' in Practice Weeks but not in Practice '{self.practice}'")

        # Check
        if self.travel_check and not TowerConstants.CHECK_PATTERN.search(self.practice):
           errors.append(f"Travel Check set but Practice '{self.practice}' doesn't mention 'check'")

        if errors:
            raise ValidationError(errors)


    class Meta:
        ordering = ["place", "dedication"]
        constraints = [
            models.UniqueConstraint(fields=["place", "dedication"], name="unique_place_dedication",
                violation_error_message="Can't have two towers with the same place and dedication")
        ]


class Website(models.Model):

    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    website = models.URLField()

    def __str__(self):
        return f'{self.website}  ({self.tower})'

    class Meta:
        ordering = ["website"]


class ContactMap(models.Model):

    class Roles(models.TextChoices):
        OTHER_CONTACT = 'C'
        TOWER_CAPTAI = 'TC'
        RINGING_MASTER = 'RM'
        STEEPLEKEEPER = 'SK'

    role = models.CharField(max_length=30, choices=Roles)
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    publish = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.get_role_display()} - {self.tower} - {self.contact}'

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

