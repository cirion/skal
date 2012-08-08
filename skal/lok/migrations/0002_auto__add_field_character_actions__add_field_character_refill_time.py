# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Character.actions'
        db.add_column('lok_character', 'actions',
                      self.gf('django.db.models.fields.IntegerField')(default=20),
                      keep_default=False)

        # Adding field 'Character.refill_time'
        db.add_column('lok_character', 'refill_time',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 8, 8, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Character.actions'
        db.delete_column('lok_character', 'actions')

        # Deleting field 'Character.refill_time'
        db.delete_column('lok_character', 'refill_time')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'lok.change': {
            'Meta': {'object_name': 'Change'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'new': ('django.db.models.fields.IntegerField', [], {}),
            'old': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'lok.character': {
            'Meta': {'object_name': 'Character'},
            'actions': ('django.db.models.fields.IntegerField', [], {'default': '20'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_health': ('django.db.models.fields.IntegerField', [], {}),
            'gender': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'money': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'refill_time': ('django.db.models.fields.DateTimeField', [], {}),
            'total_choices': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'lok.characteritem': {
            'Meta': {'object_name': 'CharacterItem'},
            'character': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Character']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Item']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'lok.characterplot': {
            'Meta': {'object_name': 'CharacterPlot'},
            'character': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Character']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Plot']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'lok.characterstat': {
            'Meta': {'object_name': 'CharacterStat'},
            'character': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Character']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Stat']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'lok.choice': {
            'Meta': {'object_name': 'Choice'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Scenario']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'lok.choiceitemprereq': {
            'Meta': {'object_name': 'ChoiceItemPreReq'},
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Choice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Item']"}),
            'minimum': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'lok.choicemoneyprereq': {
            'Meta': {'object_name': 'ChoiceMoneyPreReq'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Choice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'lok.choicestatprereq': {
            'Meta': {'object_name': 'ChoiceStatPreReq'},
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Choice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'minimum': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'stat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Stat']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'lok.healthoutcome': {
            'Meta': {'object_name': 'HealthOutcome'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Result']"})
        },
        'lok.item': {
            'Meta': {'object_name': 'Item'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'lok.itemoutcome': {
            'Meta': {'object_name': 'ItemOutcome'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Item']"}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Result']"})
        },
        'lok.moneyoutcome': {
            'Meta': {'object_name': 'MoneyOutcome'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Result']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'lok.plot': {
            'Meta': {'object_name': 'Plot'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'lok.plotoutcome': {
            'Meta': {'object_name': 'PlotOutcome'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Plot']"}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Result']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'lok.result': {
            'Meta': {'object_name': 'Result'},
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Choice']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '4000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'lok.scenario': {
            'Meta': {'object_name': 'Scenario'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '2'})
        },
        'lok.scenarioitemprereq': {
            'Meta': {'object_name': 'ScenarioItemPreReq'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Item']"}),
            'minimum': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Scenario']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'lok.scenarioplotprereq': {
            'Meta': {'object_name': 'ScenarioPlotPreReq'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Plot']"}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Scenario']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'lok.scenariostatprereq': {
            'Meta': {'object_name': 'ScenarioStatPreReq'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'minimum': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Scenario']"}),
            'stat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Stat']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'lok.stat': {
            'Meta': {'object_name': 'Stat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'lok.statoutcome': {
            'Meta': {'object_name': 'StatOutcome'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Result']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum': ('django.db.models.fields.IntegerField', [], {'default': '100000'}),
            'stat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lok.Stat']"})
        }
    }

    complete_apps = ['lok']