# Generated by Django 4.1.3 on 2023-02-03 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0002_rename_vendor_fooditem_vendor"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fooditem",
            name="image",
            field=models.ImageField(
                default="foodimages/no-image.png", upload_to="foodimages"
            ),
        ),
    ]