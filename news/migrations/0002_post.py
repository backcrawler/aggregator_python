# Generated by Django 3.0.7 on 2020-06-07 21:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('category', models.CharField(blank=True, choices=[('Politics', 'Politics'), ('Economy', 'Economy'), ('Sports', 'Sports')], default=None, max_length=16, null=True)),
                ('ref', models.URLField(db_index=True, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('source', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='news.Site')),
            ],
            options={
                'ordering': ('-created', 'ref'),
            },
        ),
    ]
