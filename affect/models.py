try:
    from django.utils import timezone as datetime
except ImportError:
    from datetime import datetime
from django.contrib.auth.models import Group, User
from django.db import models
from django_extensions.db.fields.json import JSONField


def suite():
    """Django test discovery."""
    import nose
    import os
    import unittest
    path = os.path.join(os.path.dirname(__file__), 'tests')
    suite = unittest.TestSuite()
    suite.addTests(nose.loader.TestLoader().loadTestsFromDir(path))
    return suite


class Flag(models.Model):
    name = models.SlugField(
        unique=True,
        help_text='Key that will be attached to the request')
    active = models.BooleanField(default=True)
    conflicts = models.ManyToManyField(
        'self', blank=True, null=True,
        help_text='Other flags that this flag conflicts with, highest priority'
        ' is applied.')
    priority = models.IntegerField(
        default=0,
        help_text='If flag conflicts with other flags, highest priority is '
        'applied (0 - low priority, 100 - high priority)')
    created = models.DateTimeField(
        default=datetime.now, db_index=True, editable=False,
        help_text=('Date when this flag was created.'))
    modified = models.DateTimeField(
        default=datetime.now, editable=False,
        help_text=('Date when this flag was last modified.'))

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super(Flag, self).save(*args, **kwargs)


class Criteria(models.Model):
    name = models.SlugField(
        unique=True,
        help_text='Name used when storing cookie for criteria decisions.')
    flags = models.ManyToManyField(
        Flag, blank=True, null=True,
        help_text='Flags to activate when this criteria is True.')
    persistent = models.BooleanField(
        default=False,
        help_text='This criteria is persistant to the user, and a cookie will '
        'be set. Set off to evaluate criteria for user on each request.')
    everyone = models.NullBooleanField(blank=True, help_text=(
        'Turn criteria on (True) or off (False) for all users. Overrides ALL '
        'other criteria.'))
    percent = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True,
        help_text=('A number between 0.0 and 99.9 to indicate a percentage of '
                   'users for whom flags will be active.'))
    testing = models.BooleanField(default=False, help_text=(
        'Allow this criteria to be set for a session for user testing.'))
    superusers = models.BooleanField(default=True, help_text=(
        'Activate this criteria for superusers?'))
    staff = models.BooleanField(default=False, help_text=(
        'Activate this criteria for staff?'))
    authenticated = models.BooleanField(default=False, help_text=(
        'Activate this criteria for authenticate users?'))
    DEVICE_CHOICES = ((0, 'Any'), (1, 'Desktop'), (2, 'Mobile'), (3, 'Tablet'))
    device_type = models.IntegerField(choices=DEVICE_CHOICES, default=0)
    entry_url = models.TextField(blank=True, default='', help_text=(
        'Activate this criteria for users who enter on one of these urls '
        '(comma separated list)'))
    referrer = models.TextField(blank=True, default='', help_text=(
        'Activate this criteria for users who entered from one of these '
        'domains (comma separated list)'))
    query_args = JSONField(
        blank=True, null=True, default=None,
        help_text='Dictionary of key value pairs to expect in the querystring.'
        '(ie. {"foo": "bar"} matches ?foo=bar; {"foo": "*"} matches ?foo=<any '
        'value>; {"foo": ["bar", "baz"] matches ?foo=bar or ?foo=baz)')
    #languages = models.TextField(blank=True, default='', help_text=(
    #    'Activate this criteria for users with one of these languages (comma '
    #    'separated list)'))
    groups = models.ManyToManyField(Group, blank=True, help_text=(
        'Activate this criteria for these user groups.'))
    users = models.ManyToManyField(User, blank=True, help_text=(
        'Activate this criteria for these users.'))
    max_cookie_age = models.IntegerField(
        default=2592000, blank=True, null=True,
        help_text='If this criteria is persistant, this is the amount of time '
        'in seconds before the cookie should expire. 0 or blank expires at end'
        ' of browser session.')
    note = models.TextField(blank=True, help_text=(
        'Note where this criteria is used.'))
    created = models.DateTimeField(
        default=datetime.now, db_index=True, editable=False,
        help_text=('Date when this criteria was created.'))
    modified = models.DateTimeField(
        default=datetime.now, editable=False,
        help_text=('Date when this criteria was last modified.'))

    class Meta:
        verbose_name_plural = 'criteria'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super(Criteria, self).save(*args, **kwargs)
