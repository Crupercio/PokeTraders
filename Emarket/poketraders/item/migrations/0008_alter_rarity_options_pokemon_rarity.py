# Generated by Django 5.1.1 on 2024-09-23 18:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0007_rarity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rarity',
            options={'ordering': ('name',), 'verbose_name_plural': 'Rarities'},
        ),
        migrations.AddField(
            model_name='pokemon',
            name='rarity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pokemons', to='item.rarity'),
        ),
    ]
