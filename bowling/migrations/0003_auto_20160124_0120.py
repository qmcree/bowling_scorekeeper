# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-24 07:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bowling', '0002_auto_20160124_0115'),
    ]

    operations = [
        migrations.RenameField(
            model_name='delivery',
            old_name='game_id',
            new_name='game',
        ),
        migrations.RenameField(
            model_name='delivery',
            old_name='player_id',
            new_name='player',
        ),
        migrations.RenameField(
            model_name='gamescore',
            old_name='game_id',
            new_name='game',
        ),
        migrations.RenameField(
            model_name='gamescore',
            old_name='player_id',
            new_name='player',
        ),
    ]
