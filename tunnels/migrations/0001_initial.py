# Generated by Django 5.0.1 on 2024-11-22 08:01

import django.db.models.deletion
import simple_history.models
import tunnels.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('location', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalSite',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('location', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical site',
                'verbose_name_plural': 'historical sites',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalTunnelRequest',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('business_unit', models.CharField(max_length=100, validators=[tunnels.validators.validate_business_unit])),
                ('use_case', models.TextField()),
                ('service_owner', models.CharField(max_length=100)),
                ('notification_dl', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('NETWORK_APPROVED', 'Network Approved'), ('SECURITY_APPROVED', 'Security Approved'), ('REJECTED', 'Rejected'), ('IMPLEMENTED', 'Implemented'), ('EXPIRED', 'Expired'), ('DECOMMISSIONED', 'Decommissioned')], default='PENDING', max_length=20)),
                ('phase1_encryption', models.CharField(choices=[('AES-256', 'AES-256'), ('AES-192', 'AES-192'), ('AES-128', 'AES-128')], max_length=10)),
                ('phase1_authentication', models.CharField(default='SHA256', max_length=10)),
                ('phase1_dh_group', models.CharField(choices=[('2', 'Group 2 (1024-bit)'), ('5', 'Group 5 (1536-bit)'), ('14', 'Group 14 (2048-bit)')], max_length=2)),
                ('phase1_lifetime', models.IntegerField(default=28800, validators=[tunnels.validators.validate_lifetime])),
                ('phase2_encryption', models.CharField(choices=[('AES-256', 'AES-256'), ('AES-192', 'AES-192'), ('AES-128', 'AES-128')], max_length=10)),
                ('phase2_authentication', models.CharField(default='SHA256', max_length=10)),
                ('phase2_pfs_group', models.CharField(choices=[('2', 'Group 2 (1024-bit)'), ('5', 'Group 5 (1536-bit)'), ('14', 'Group 14 (2048-bit)')], max_length=2)),
                ('phase2_lifetime', models.IntegerField(default=3600, validators=[tunnels.validators.validate_lifetime])),
                ('peer_gateway', models.GenericIPAddressField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('network_approved_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('requester', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('security_approved_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tunnels.site')),
            ],
            options={
                'verbose_name': 'historical tunnel request',
                'verbose_name_plural': 'historical tunnel requests',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalFirewall',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('hostname', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=255)),
                ('interface', models.CharField(default='ethernet1/1', max_length=50)),
                ('tunnel_interface', models.CharField(default='tunnel.1', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tunnels.site')),
            ],
            options={
                'verbose_name': 'historical Firewall',
                'verbose_name_plural': 'historical Firewalls',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Firewall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=255)),
                ('interface', models.CharField(default='ethernet1/1', max_length=50)),
                ('tunnel_interface', models.CharField(default='tunnel.1', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('site', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='firewall', to='tunnels.site')),
            ],
            options={
                'verbose_name': 'Firewall',
                'verbose_name_plural': 'Firewalls',
            },
        ),
        migrations.CreateModel(
            name='TunnelRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_unit', models.CharField(max_length=100, validators=[tunnels.validators.validate_business_unit])),
                ('use_case', models.TextField()),
                ('service_owner', models.CharField(max_length=100)),
                ('notification_dl', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('NETWORK_APPROVED', 'Network Approved'), ('SECURITY_APPROVED', 'Security Approved'), ('REJECTED', 'Rejected'), ('IMPLEMENTED', 'Implemented'), ('EXPIRED', 'Expired'), ('DECOMMISSIONED', 'Decommissioned')], default='PENDING', max_length=20)),
                ('phase1_encryption', models.CharField(choices=[('AES-256', 'AES-256'), ('AES-192', 'AES-192'), ('AES-128', 'AES-128')], max_length=10)),
                ('phase1_authentication', models.CharField(default='SHA256', max_length=10)),
                ('phase1_dh_group', models.CharField(choices=[('2', 'Group 2 (1024-bit)'), ('5', 'Group 5 (1536-bit)'), ('14', 'Group 14 (2048-bit)')], max_length=2)),
                ('phase1_lifetime', models.IntegerField(default=28800, validators=[tunnels.validators.validate_lifetime])),
                ('phase2_encryption', models.CharField(choices=[('AES-256', 'AES-256'), ('AES-192', 'AES-192'), ('AES-128', 'AES-128')], max_length=10)),
                ('phase2_authentication', models.CharField(default='SHA256', max_length=10)),
                ('phase2_pfs_group', models.CharField(choices=[('2', 'Group 2 (1024-bit)'), ('5', 'Group 5 (1536-bit)'), ('14', 'Group 14 (2048-bit)')], max_length=2)),
                ('phase2_lifetime', models.IntegerField(default=3600, validators=[tunnels.validators.validate_lifetime])),
                ('peer_gateway', models.GenericIPAddressField()),
                ('network_approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='network_approvals', to=settings.AUTH_USER_MODEL)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('security_approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='security_approvals', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tunnels.site')),
            ],
            options={
                'ordering': ['-created_at'],
                'permissions': [('can_approve_tunnel', 'Can approve tunnel requests'), ('can_push_to_firewall', 'Can push tunnel config to firewall'), ('can_validate_tunnel', 'Can validate tunnel annually')],
            },
        ),
        migrations.CreateModel(
            name='NetworkCIDR',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cidr', models.CharField(max_length=100, validators=[tunnels.validators.validate_network_cidr])),
                ('is_local', models.BooleanField(default=True)),
                ('tunnel_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tunnels.tunnelrequest')),
            ],
            options={
                'verbose_name': 'Network CIDR',
                'verbose_name_plural': 'Network CIDRs',
            },
        ),
        migrations.CreateModel(
            name='HistoricalTunnelValidation',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('validation_date', models.DateTimeField(blank=True, editable=False)),
                ('next_validation_date', models.DateTimeField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('VALIDATED', 'Validated'), ('EXPIRED', 'Expired'), ('DECOMMISSIONED', 'Decommissioned')], default='PENDING', max_length=20)),
                ('business_justification', models.TextField(blank=True)),
                ('notification_sent', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('validated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('tunnel_request', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tunnels.tunnelrequest')),
            ],
            options={
                'verbose_name': 'historical tunnel validation',
                'verbose_name_plural': 'historical tunnel validations',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalNetworkCIDR',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('cidr', models.CharField(max_length=100, validators=[tunnels.validators.validate_network_cidr])),
                ('is_local', models.BooleanField(default=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('tunnel_request', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tunnels.tunnelrequest')),
            ],
            options={
                'verbose_name': 'historical Network CIDR',
                'verbose_name_plural': 'historical Network CIDRs',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='TunnelValidation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('validation_date', models.DateTimeField(auto_now_add=True)),
                ('next_validation_date', models.DateTimeField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('VALIDATED', 'Validated'), ('EXPIRED', 'Expired'), ('DECOMMISSIONED', 'Decommissioned')], default='PENDING', max_length=20)),
                ('business_justification', models.TextField(blank=True)),
                ('notification_sent', models.BooleanField(default=False)),
                ('tunnel_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='validations', to='tunnels.tunnelrequest')),
                ('validated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
