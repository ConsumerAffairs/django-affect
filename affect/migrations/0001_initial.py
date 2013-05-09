# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Flag'
        db.create_table(u'affect_flag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'affect', ['Flag'])

        # Adding M2M table for field conflicts on 'Flag'
        db.create_table(u'affect_flag_conflicts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_flag', models.ForeignKey(orm[u'affect.flag'], null=False)),
            ('to_flag', models.ForeignKey(orm[u'affect.flag'], null=False))
        ))
        db.create_unique(u'affect_flag_conflicts', ['from_flag_id', 'to_flag_id'])

        # Adding model 'Criteria'
        db.create_table(u'affect_criteria', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('persistent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('everyone', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('percent', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1, blank=True)),
            ('testing', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('superusers', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('authenticated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('device_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('entry_url', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('referrer', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('query_args', self.gf('django.db.models.fields.TextField')(default='{}', null=True, blank=True)),
            ('max_cookie_age', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'affect', ['Criteria'])

        # Adding M2M table for field flags on 'Criteria'
        db.create_table(u'affect_criteria_flags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('criteria', models.ForeignKey(orm[u'affect.criteria'], null=False)),
            ('flag', models.ForeignKey(orm[u'affect.flag'], null=False))
        ))
        db.create_unique(u'affect_criteria_flags', ['criteria_id', 'flag_id'])

        # Adding M2M table for field groups on 'Criteria'
        db.create_table(u'affect_criteria_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('criteria', models.ForeignKey(orm[u'affect.criteria'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(u'affect_criteria_groups', ['criteria_id', 'group_id'])

        # Adding M2M table for field users on 'Criteria'
        db.create_table(u'affect_criteria_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('criteria', models.ForeignKey(orm[u'affect.criteria'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(u'affect_criteria_users', ['criteria_id', 'user_id'])


    def backwards(self, orm):
        # Deleting model 'Flag'
        db.delete_table(u'affect_flag')

        # Removing M2M table for field conflicts on 'Flag'
        db.delete_table('affect_flag_conflicts')

        # Deleting model 'Criteria'
        db.delete_table(u'affect_criteria')

        # Removing M2M table for field flags on 'Criteria'
        db.delete_table('affect_criteria_flags')

        # Removing M2M table for field groups on 'Criteria'
        db.delete_table('affect_criteria_groups')

        # Removing M2M table for field users on 'Criteria'
        db.delete_table('affect_criteria_users')


    models = {
        u'affect.criteria': {
            'Meta': {'object_name': 'Criteria'},
            'authenticated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'device_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'entry_url': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'everyone': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'flags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['affect.Flag']", 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_cookie_age': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'percent': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1', 'blank': 'True'}),
            'persistent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'query_args': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'referrer': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'superusers': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'testing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'affect.flag': {
            'Meta': {'object_name': 'Flag'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'conflicts': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'conflicts_rel_+'", 'null': 'True', 'to': u"orm['affect.Flag']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['affect']