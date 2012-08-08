# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Scenario'
        db.create_table('lok_scenario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2000)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=2)),
        ))
        db.send_create_signal('lok', ['Scenario'])

        # Adding model 'Choice'
        db.create_table('lok_choice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Scenario'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=1000)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('lok', ['Choice'])

        # Adding model 'Plot'
        db.create_table('lok_plot', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2000)),
        ))
        db.send_create_signal('lok', ['Plot'])

        # Adding model 'Item'
        db.create_table('lok_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('lok', ['Item'])

        # Adding model 'Stat'
        db.create_table('lok_stat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('lok', ['Stat'])

        # Adding model 'ScenarioStatPreReq'
        db.create_table('lok_scenariostatprereq', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Scenario'])),
            ('stat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Stat'])),
            ('minimum', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maximum', self.gf('django.db.models.fields.IntegerField')(default=100)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('lok', ['ScenarioStatPreReq'])

        # Adding model 'ScenarioItemPreReq'
        db.create_table('lok_scenarioitemprereq', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Scenario'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Item'])),
            ('minimum', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('lok', ['ScenarioItemPreReq'])

        # Adding model 'ScenarioPlotPreReq'
        db.create_table('lok_scenarioplotprereq', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Scenario'])),
            ('plot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Plot'])),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('lok', ['ScenarioPlotPreReq'])

        # Adding model 'ChoiceStatPreReq'
        db.create_table('lok_choicestatprereq', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('choice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Choice'])),
            ('stat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Stat'])),
            ('minimum', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maximum', self.gf('django.db.models.fields.IntegerField')(default=100)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('lok', ['ChoiceStatPreReq'])

        # Adding model 'ChoiceItemPreReq'
        db.create_table('lok_choiceitemprereq', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('choice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Choice'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Item'])),
            ('minimum', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('lok', ['ChoiceItemPreReq'])

        # Adding model 'ChoiceMoneyPreReq'
        db.create_table('lok_choicemoneyprereq', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('choice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Choice'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('lok', ['ChoiceMoneyPreReq'])

        # Adding model 'Result'
        db.create_table('lok_result', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('choice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Choice'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=4000)),
        ))
        db.send_create_signal('lok', ['Result'])

        # Adding model 'MoneyOutcome'
        db.create_table('lok_moneyoutcome', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('choice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Result'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('lok', ['MoneyOutcome'])

        # Adding model 'StatOutcome'
        db.create_table('lok_statoutcome', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('choice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Result'])),
            ('stat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Stat'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('maximum', self.gf('django.db.models.fields.IntegerField')(default=100000)),
        ))
        db.send_create_signal('lok', ['StatOutcome'])

        # Adding model 'ItemOutcome'
        db.create_table('lok_itemoutcome', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Result'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Item'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('lok', ['ItemOutcome'])

        # Adding model 'PlotOutcome'
        db.create_table('lok_plotoutcome', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Result'])),
            ('plot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Plot'])),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('lok', ['PlotOutcome'])

        # Adding model 'HealthOutcome'
        db.create_table('lok_healthoutcome', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Result'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('lok', ['HealthOutcome'])

        # Adding model 'Character'
        db.create_table('lok_character', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('money', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('gender', self.gf('django.db.models.fields.IntegerField')()),
            ('current_health', self.gf('django.db.models.fields.IntegerField')()),
            ('total_choices', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('lok', ['Character'])

        # Adding model 'CharacterStat'
        db.create_table('lok_characterstat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('character', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Character'])),
            ('stat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Stat'])),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('lok', ['CharacterStat'])

        # Adding model 'CharacterPlot'
        db.create_table('lok_characterplot', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('character', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Character'])),
            ('plot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Plot'])),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('lok', ['CharacterPlot'])

        # Adding model 'CharacterItem'
        db.create_table('lok_characteritem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('character', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Character'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lok.Item'])),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('lok', ['CharacterItem'])

        # Adding model 'Change'
        db.create_table('lok_change', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('old', self.gf('django.db.models.fields.IntegerField')()),
            ('new', self.gf('django.db.models.fields.IntegerField')()),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('lok', ['Change'])


    def backwards(self, orm):
        # Deleting model 'Scenario'
        db.delete_table('lok_scenario')

        # Deleting model 'Choice'
        db.delete_table('lok_choice')

        # Deleting model 'Plot'
        db.delete_table('lok_plot')

        # Deleting model 'Item'
        db.delete_table('lok_item')

        # Deleting model 'Stat'
        db.delete_table('lok_stat')

        # Deleting model 'ScenarioStatPreReq'
        db.delete_table('lok_scenariostatprereq')

        # Deleting model 'ScenarioItemPreReq'
        db.delete_table('lok_scenarioitemprereq')

        # Deleting model 'ScenarioPlotPreReq'
        db.delete_table('lok_scenarioplotprereq')

        # Deleting model 'ChoiceStatPreReq'
        db.delete_table('lok_choicestatprereq')

        # Deleting model 'ChoiceItemPreReq'
        db.delete_table('lok_choiceitemprereq')

        # Deleting model 'ChoiceMoneyPreReq'
        db.delete_table('lok_choicemoneyprereq')

        # Deleting model 'Result'
        db.delete_table('lok_result')

        # Deleting model 'MoneyOutcome'
        db.delete_table('lok_moneyoutcome')

        # Deleting model 'StatOutcome'
        db.delete_table('lok_statoutcome')

        # Deleting model 'ItemOutcome'
        db.delete_table('lok_itemoutcome')

        # Deleting model 'PlotOutcome'
        db.delete_table('lok_plotoutcome')

        # Deleting model 'HealthOutcome'
        db.delete_table('lok_healthoutcome')

        # Deleting model 'Character'
        db.delete_table('lok_character')

        # Deleting model 'CharacterStat'
        db.delete_table('lok_characterstat')

        # Deleting model 'CharacterPlot'
        db.delete_table('lok_characterplot')

        # Deleting model 'CharacterItem'
        db.delete_table('lok_characteritem')

        # Deleting model 'Change'
        db.delete_table('lok_change')


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
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_health': ('django.db.models.fields.IntegerField', [], {}),
            'gender': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'money': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
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