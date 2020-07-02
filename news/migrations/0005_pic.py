# Generated by Django 3.0.7 on 2020-07-01 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20200614_1658'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=32)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
            ],
        ),
        migrations.AddField(
            model_name='site',
            name='img',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='news.Pic')
        ),
    ]