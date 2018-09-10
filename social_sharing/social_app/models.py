# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    content = models.TextField()
    event = models.ForeignKey('Event', models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'comment'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    photo = models.TextField(blank=True, null=True)
    date = models.CharField(max_length=45)
    location = models.CharField(max_length=200, blank=True, null=True)
    participants = models.TextField(blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'event'


class Participant(models.Model):
    participant_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    event = models.ForeignKey(Event, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'participant'


class Reaction(models.Model):
    reactionid = models.AutoField(primary_key=True)
    like_number = models.IntegerField()
    user_like = models.TextField()
    event = models.ForeignKey(Event, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'reaction'


class Session(models.Model):
    session_id = models.AutoField(primary_key=True)
    ip_adress = models.CharField(db_column='IP_adress', max_length=45)  # Field name made lowercase.
    user = models.ForeignKey('User', models.DO_NOTHING)
    last_login = models.CharField(max_length=45)
    login_status = models.CharField(max_length=45)
    session_value = models.TextField()

    class Meta:
        managed = False
        db_table = 'session'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    is_super_user = models.IntegerField()
    username = models.CharField(unique=True, max_length=45)
    password = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'user'
