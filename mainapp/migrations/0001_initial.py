# Generated by Django 3.2.9 on 2023-06-14 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lottery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_end', models.DateTimeField(verbose_name='Дата окончания розыгрыша')),
                ('date_start', models.DateTimeField(auto_now_add=True, verbose_name='Дата старта розыгрыша')),
                ('summa', models.PositiveIntegerField(default=0, verbose_name='Сумма в розыгрыше')),
                ('min_members', models.PositiveIntegerField(default=0, verbose_name='Минимальное кол-во участников для старта')),
                ('finish', models.BooleanField(default=False, verbose_name='Завершён')),
            ],
            options={
                'verbose_name': 'Розыгрыш',
                'verbose_name_plural': 'Розыгрыши',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(blank=True, null=True, unique=True, verbose_name='Порядковый номер')),
            ],
            options={
                'verbose_name': 'Комната',
                'verbose_name_plural': 'Комнаты',
            },
        ),
        migrations.CreateModel(
            name='MemberLottery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_user', models.CharField(blank=True, max_length=70, null=True, unique=True, verbose_name='Токен пользователя')),
                ('num_member', models.PositiveIntegerField(default=1, unique=True, verbose_name='Порядковый номер участника')),
                ('sum_bet', models.PositiveIntegerField(default=1, verbose_name='Ставка')),
                ('num_choose', models.PositiveIntegerField(verbose_name='Выбранная цифра')),
                ('winner', models.BooleanField(default=False, verbose_name='Победитель')),
                ('lottery', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mainapp.lottery', verbose_name='Розыгрыш')),
            ],
            options={
                'verbose_name': 'Участник',
                'verbose_name_plural': 'Участники',
            },
        ),
        migrations.AddField(
            model_name='lottery',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.room', verbose_name='Комната'),
        ),
    ]
