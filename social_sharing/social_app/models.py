# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class CommentManager(models.Manager):
    def get_comment(self, user, event):
        return self.get(user=user, event=event)

    def create_comment(self, content, user, event, create_time):
        return self.create(content=content, user=user, event=event, create_time=create_time)

    def delete_comment(self, user, event):
        participant = self.get(user=user, event=event)
        participant.delete()

    def filter_by_event(self, event):
        return self.filter(event = event)


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    content = models.TextField()
    event = models.ForeignKey('Event', models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)
    create_time = models.IntegerField()
    comment_objects = CommentManager()

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


class EventManager(models.Manager):
    def filter_time_range(self, start_time, end_time):
        return self.filter(time__range=(start_time, end_time)).order_by('-time')[0:5]

    def get_event_details(self, event_id):
        return self.get(event_id=event_id)

    def search_event(self, start_time, end_time, hashtag):
        return self.filter(date_took_place__range=(start_time, end_time), hashtag=hashtag)

    def create_event(self, title, description, photo, date_took_place, location, user, time, hashtag):
        return self.create(title=title, description=description, photo=photo, date_took_place=date_took_place,
                           location=location, user=user,time=time, hashtag=hashtag)


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    photo = models.TextField(blank=True, null=True)
    date_took_place = models.CharField(max_length=45, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    time = models.IntegerField()
    hashtag = models.CharField(max_length=45, blank=True, null=True)
    event_objects = EventManager()

    class Meta:
        managed = False
        db_table = 'event'


class ParticipantManager(models.Manager):
    def get_participant(self, user, event):
        return self.get(user=user, event=event)

    def create_participant(self,user, event):
        return self.create(user=user, event=event)

    def delete_participant(self, user, event):
        participant = self.get(user=user, event=event)
        participant.delete()

    def filter_by_event(self, event):
        return self.filter(event = event)


class Participant(models.Model):
    participant_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    event = models.ForeignKey(Event, models.DO_NOTHING)
    participant_objects = ParticipantManager()

    class Meta:
        managed = False
        db_table = 'participant'


class ReactionManager(models.Manager):
    def get_reaction(self, user, event):
        return self.get(user=user, event=event)

    def create_reaction(self,user, event):
        return self.create(user=user, event=event)

    def delete_reaction(self, user, event):
        reaction = self.get(user=user, event=event)
        reaction.delete()

    def filter_by_event(self, event):
        return self.filter(event = event)


class Reaction(models.Model):
    reaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    event = models.ForeignKey(Event, models.DO_NOTHING)
    reaction_objects = ReactionManager()

    class Meta:
        managed = False
        db_table = 'reaction'


class SessionManger(models.Manager):
    def get_session(self, session_value):
        return self.get(session_value=session_value)

    def delete_session(self, session_value):
        session = self.get(session_value=session_value)
        session.delete()

    def create_session(self, ip_adress, user, last_login, login_status, session_value):
        return self.create(ip_adress=ip_adress, user=user, last_login=last_login, login_status=login_status,
                           session_value=session_value)


class Session(models.Model):
    session_id = models.AutoField(primary_key=True)
    ip_adress = models.CharField(db_column='IP_adress', max_length=45)  # Field name made lowercase.
    user = models.ForeignKey('User', models.DO_NOTHING)
    last_login = models.IntegerField()
    login_status = models.CharField(max_length=45)
    session_value = models.CharField(max_length=100)
    session_objects = SessionManger()

    class Meta:
        managed = False
        db_table = 'session'


class UserManager(models.Manager):
    def get_user(self, user_id=None, username=None):
        if user_id is not None:
            return self.get(user_id=user_id)
        if username is not None:
            return self.get(username=username)


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    is_super_user = models.IntegerField()
    username = models.CharField(unique=True, max_length=45)
    password = models.CharField(max_length=100)
    user_objects = UserManager()

    class Meta:
        managed = False
        db_table = 'user'
