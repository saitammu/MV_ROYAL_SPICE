from django.db import migrations

VENDORS_DATA = {
    'Chicken': ['dhum','fry','boneless','kulfi','lollypop','small body','thangidi','staff chicken'],
    'Mutton': ['nulli gosh','mutton curry','mutton dhum'],
    'Dhanush': ['curd','paneer','mushroom','babycorn','milk','butter','green beans','corn','corn tin','veg chicken','garlic'],
    'Vegetables': ['potato','carrot','capsicum','cabbage','tomato','beans','sambar vegetables','chillies','staff vegetables'],
    'Prawns': ['prawns','pandugappa fish','tandoori full fish','staff fish'],
    'Balaji': ['mustard oil','chaat masala','saunf','828 sauce','rose water','keera water','tomato sauce','chilli sauce','sambar powder','inguva','noodles','mutton masala','white pepper','cleaning powder','silver foil'],
    'Onions': ['onions'],
    'Spices': ['elaichi','lavanga','dalchini','javitri','black pepper','shajeera','jeera','ghee','moquitels','saunf','jaiphal','star flower','black elaichi','kishmish'],
    'Leafs': ['coriander','mint','palak','curry leaf','gongura'],
    'Lemons': ['lemons'],
    'Water': ['water'],
    'Kirana Traders': ['basmati rice','oil','salt','rock salt','maida','corn flour','tasting salt','mirchi'],
    'Chaitanya': ['chilli powder','dhaniya powder','chicken masala','turmeric','coconut powder','ragi flour'],
    'Local Kirana': ['dal','sugar','staff groceries'],
    'Kaju Nidadavolu': ['kaju'],
    'Kaju Local': ['kaju','kaju nooka','puchapappu'],
    'Natu Koodi': ['natukodi'],
    'Ghee': ['ghee'],
    'Basha': ['basha fish','chinese fish'],
}

def seed_vendors(apps, schema_editor):
    Vendor = apps.get_model('tracker', 'Vendor')
    SubCategory = apps.get_model('tracker', 'SubCategory')
    for vendor_name, items in VENDORS_DATA.items():
        vendor = Vendor.objects.create(name=vendor_name)
        for item in items:
            SubCategory.objects.get_or_create(vendor=vendor, name=item)

def unseed_vendors(apps, schema_editor):
    Vendor = apps.get_model('tracker', 'Vendor')
    Vendor.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [('tracker', '0001_initial')]
    operations = [migrations.RunPython(seed_vendors, unseed_vendors)]
