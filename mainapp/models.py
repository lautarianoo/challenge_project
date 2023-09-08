from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models

class Room(models.Model):

    number = models.PositiveIntegerField(verbose_name="Порядковый номер", unique=True, blank=True, null=True)
    active = models.BooleanField(verbose_name="Активная", default=False)

    def __str__(self):
        return f"Комната #{self.number}"

    class Meta:
        verbose_name = "Комната"
        verbose_name_plural = "Комнаты"

class MemberLottery(models.Model):

    session_key_user = models.CharField(verbose_name="Ключ сессии", max_length=300, blank=True, null=True)
    token_user = models.CharField(verbose_name="Токен пользователя", max_length=70, null=True, blank=True)
    num_member = models.PositiveIntegerField(verbose_name="Порядковый номер участника", default=1)
    lottery = models.ForeignKey("Lottery", verbose_name="Розыгрыш", on_delete=models.SET_NULL, related_name="members", blank=True, null=True)
    sum_bet = models.PositiveIntegerField(verbose_name="Ставка", default=1)
    num_choose = models.PositiveIntegerField(verbose_name="Выбранная цифра")
    winner = models.BooleanField(verbose_name="Победитель", default=False)
    win_money = models.PositiveIntegerField(verbose_name="Выиграл (руб.)", default=0)

    def __str__(self):
        return f"Участник #{self.num_member} | Розыгрыш #{self.lottery.id}"

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

class Lottery(models.Model):

    room = models.ForeignKey(Room, verbose_name="Комната", on_delete=models.CASCADE, blank=True, null=True)
    date_end = models.DateTimeField(verbose_name="Дата окончания розыгрыша")
    date_start = models.DateTimeField(verbose_name="Дата старта розыгрыша", auto_now_add=True)
    summa = models.PositiveIntegerField(verbose_name="Сумма в розыгрыше", default=0)
    min_members = models.PositiveIntegerField(verbose_name="Минимальное кол-во участников для старта", default=0)
    finish = models.BooleanField(verbose_name="Завершён", default=False)

    def __str__(self):
        return f"Розыгрыш #{self.id}"

    class Meta:
        verbose_name = "Розыгрыш"
        verbose_name_plural = "Розыгрыши"