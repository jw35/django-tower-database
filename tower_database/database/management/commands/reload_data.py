from django.core.management.base import BaseCommand, CommandError

from database.models import Tower, Contact, ContactMap, ContactMethod

import requests
import csv

from io import StringIO

easy_fields = (
    ('Place', 'place'),
    ('Dedication', 'dedication'),
    ('Full dedication', 'full_dedication'),
    ('Nickname', 'nickname'),
    ('Service', 'service'),
    ('Practice', 'practice'),
    ('Week', 'week'),
    ('Bells', 'bells'),
    ('Weight', 'weight'),
    ('Note', 'note'),
    ('OS grid', 'os_grid'),
    ('Postcode', 'postcode'),
    ('Lng', 'lat'),
    ('Lat', 'lng'),
    ('Website', 'website'),
    #('Picture', ''),
    #('Picture credit', ''),
    #('Secretary', ''),
    #('Phone', ''),
    #('Email', ''),
    #('Band contact', ''),
    #('Bells contact', ''),
    #('', 'primary_contact'),
    #('', 'contact_restrictions'),
    #('Peals', 'peals'),
    ('Dove Tower ID', 'dove_towerid'),
    ('Dove Ring ID', 'dove_ringid'),
    ('TowerBase ID', 'towerbase_id'),
    ('Notes', 'notes'),
    ('Longer notes', 'long_notes'),
    ('Maintainer notes', 'maintainer_notes'),
)

boolean_fields = (
    ('Include dedication', 'include_dedication'),
    ('Report', 'report'),
    ('Check', 'check_before_traveling'),
    ('GF', 'gf'),
)

lookup_fields = (
    ('County', 'county', {'Cambridgeshire': 'C', 'Norfolk': 'N'}),
    ('District', 'district', {'Cambridge': 'C', 'Ely': 'E', 'Huntingdon': 'H', 'Wisbech': 'W'}),
    ('Day', 'day', {'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed', 'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'}),
    ('Type', 'ring_type', {'Chime': 'Chime', 'Tubular Chime': 'T-Chime', 'Removed': '', 'Hung dead': ''}),
)

status_lookup = {
    'Regular ringing': 'R',
    'Occasional ringing': 'O',
    'No ringing': 'N'
}

class Command(BaseCommand):
    help = 'Reload the database from the master list'


    def handle(self, *args, **options):

        # Clear out all the old stuff
        Tower.objects.all().delete()
        Contact.objects.all().delete()

        # Get the CSV data from the master list
        spreadsheet = '1o1pAHht9B3VapS9FziLOrMQlSTMvxQ_JeoGSjfEA9hU'
        sheet = 'Ely DA towers'
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet}/gviz/tq"
        payload = {'tqx': 'out:csv', 'sheet': sheet}
        r = requests.get(url, payload)
        tower_csv = StringIO(r.text)

        for csv_row in csv.DictReader(tower_csv):

            self.stdout.write(csv_row['Place'])

            db_row = Tower()

            for f, t in easy_fields:
                setattr(db_row, t, csv_row[f])

            for f, t in boolean_fields:
                setattr(db_row, t, csv_row[f] == "Yes")

            for f, t, l in lookup_fields:
                if csv_row[f]:
                    self.stdout.write(f"{f}, {csv_row[f]}")
                    setattr(db_row, t, l[csv_row[f]])

            db_row.bells = int(csv_row['Bells'])
            if csv_row['Peals']:
                db_row.peals = int(csv_row['Peals'])

            if csv_row['Secretary']:
                contact = Contact(name=csv_row['Secretary'], publish=True)
                if csv_row['Band contact'] and not csv_row['Bells contact']:
                    contact.contact_restrictions = 'Band only'
                elif not csv_row['Band contact'] and csv_row['Bells contact']:
                    contact.contact_restrictions = 'Bells only'
                contact.save()
                db_row.contact = contact

                if csv_row['Phone']:
                    contact.contactmethod_set.create(contact_type='Phone', contact_value=csv_row['Phone'])
                if csv_row['Email']:
                    contact.contactmethod_set.create(contact_type='Email', contact_value=csv_row['Email'])

            db_row.save()

