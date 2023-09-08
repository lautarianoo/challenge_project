from django.shortcuts import render, redirect
from django.views import View
import random
from .models import Lottery, MemberLottery
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpResponse
import tablib


def generate_code(length=50):
    letters = 'qwertyuiopasdfghjklzxcvbnm'
    digits = '1234567890'
    letters_upper = letters.upper()
    blank = list(letters + digits + letters_upper)
    random.shuffle(blank)
    code = ''.join([random.choice(blank) for x in range(length)])
    return code

def choose_winners(lottery):
    members = lottery.members.all()
    numbers = [member for member in members]
    count_numbers = {}
    for num in numbers:
        total_count = 0
        for i in numbers:
            if num.num_member == i.num_choose:
                total_count += 1
        count_numbers[num.num_member] = total_count
    winners = []
    total = 0
    for key, value in count_numbers.items():
        if value >= total:
            total = value
    for key, value in count_numbers.items():
        if total == value:
            winners.append(MemberLottery.objects.get(num_member=key, lottery=lottery))
    return winners

def export_lottery_excel(request):
    headers = ('Название', 'Комната', 'Статус', 'Дата создания', 'Сумма в розыгрыше, руб.', 'Дата розыгрыша')
    data = []
    data = tablib.Dataset(*data, headers=headers)
    lotteries = Lottery.objects.all()
    for lottery in lotteries:
        if lottery.finish:
            status = "Завершен"
        else:
            status = "Не состоялся"
        data.append((lottery.__str__(), lottery.room.__str__(), status, lottery.date_start.strftime("%m.%d.%Y %H:%M:%S"), lottery.summa, lottery.date_end.strftime("%m.%d.%Y %H:%M:%S")))
    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=export_lottery.xls"
    return response

class ExportMembersView(View):

    def get(self, request, *args, **kwargs):
        headers = ('Токен', 'Порядковый номер', 'Ставка, руб.', 'Выбранная цифра')
        data = []
        data = tablib.Dataset(*data, headers=headers)
        lottery = Lottery.objects.get(id=kwargs.get("id"))
        for member in lottery.members.all():
            data.append((member.token_user, member.num_member, member.sum_bet, member.num_choose))
        response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=export_members.xls"
        return response

class ExportWinnersView(View):

    def get(self, request, *args, **kwargs):
        headers = ('Токен', 'Порядковый номер', 'Ставка, руб.', 'Выбранная цифра', 'Выигрыш, руб.')
        data = []
        data = tablib.Dataset(*data, headers=headers)
        lottery = Lottery.objects.get(id=kwargs.get("id"))
        for member in lottery.members.filter(winner=True):
            data.append((member.token_user, member.num_member, member.sum_bet, member.num_choose, member.win_money))
        response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=export_winners.xls"
        return response

class ExportWinnersAllView(View):

    def get(self, request, *args, **kwargs):
        headers = ('Токен', 'Розыгрыш', 'Порядковый номер', 'Ставка, руб.', 'Выбранная цифра', 'Выигрыш, руб.')
        data = []
        data = tablib.Dataset(*data, headers=headers)
        for member in MemberLottery.objects.filter(winner=True):
            data.append((member.token_user, member.lottery.__str__(), member.num_member, member.sum_bet, member.num_choose, member.win_money))
        response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
        response['Content-Disposition'] = "attachment; filename=export_winners.xls"
        return response

def export_winners_excel(request):
    headers = ('Название', 'Комната', 'Статус', 'Дата создания', 'Сумма в розыгрыше, руб.', 'Дата розыгрыша')
    data = []
    data = tablib.Dataset(*data, headers=headers)
    lotteries = Lottery.objects.all()
    for lottery in lotteries:
        if lottery.finish:
            status = "Завершен"
        else:
            status = "Не состоялся"
        data.append((lottery.__str__(), lottery.room.__str__(), status, lottery.date_start.strftime("%m.%d.%Y %H:%M:%S"), lottery.summa, lottery.date_end.strftime("%m.%d.%Y %H:%M:%S")))
    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=export_lottery.xls"
    return response

class MainPageView(View):

    def get(self, request, *args, **kwargs):
        for lottery in Lottery.objects.all():
            if lottery.room.active and lottery.finish:
                lottery.room.active = False
        if "token" not in request.session.keys():
            new_token = generate_code()
            request.session["token"] = new_token
            request.session["summa"] = 1000
        lotteries = Lottery.objects.filter(finish=False)
        now = timezone.now()
        for lottery in lotteries:
            lottery.room.active = True
            if now > lottery.date_end:
                lottery.finish = True
                lottery.save()
                winners = choose_winners(lottery)
                for winner in winners:
                    winner.winner = True
                    winner.save()
                    if len(winners) > 1:
                        s = SessionStore(session_key=winner.session_key_user)
                        s["summa"] += lottery.summa/len(winners)
                        s.save()
                        winner.win_money += lottery.summa/len(winners)
                        winner.save()
                    else:
                        s = SessionStore(session_key=winner.session_key_user)
                        s["summa"] += lottery.summa
                        s.save()
                        winner.win_money += lottery.summa
                        winner.save()
        return render(request, "mainapp/main_page.html", {"lotteries": lotteries})

class BetLotteryView(View):

    def get(self, request, *args, **kwargs):
        lottery = Lottery.objects.get(id=kwargs.get("id"))
        return render(request, "mainapp/bet_lottery.html", {"lottery": lottery})

    def post(self, request, *args, **kwargs):
        if int(request.session["summa"]) >= int(request.POST.get("sum")):
            lottery = Lottery.objects.get(id=kwargs.get("id"))
            new_member = MemberLottery.objects.create(session_key_user=request.session.session_key, token_user=request.session.get("token"), sum_bet=int(request.POST.get("sum")), num_choose=int(request.POST.get("num")), lottery=lottery)
            new_member.num_member = lottery.members.count() + 1
            lottery.summa += int(request.POST.get("sum"))
            new_member.save()
            lottery.save()
            request.session["summa"] = request.session.get("summa") - int(request.POST.get("sum"))
            return redirect("main-page")
        return redirect("main-page")

class LotteriesView(View):

    def get(self, request, *args, **kwargs):
        context = {}
        lotteries = Lottery.objects.all()
        context["lotteries"] = lotteries
        now = timezone.now()
        for lottery in lotteries:
            if not lottery.finish:
                lottery.room.active = True
                if now > lottery.date_end:
                    lottery.finish = True
                    winners = choose_winners(lottery)
                    for winner in winners:
                        winner.winner = True
                        if len(winners) > 1:
                            s = SessionStore(session_key=winner.session_key_user)
                            s["summa"] += lottery.summa/2
                            s.save()
                            winner.win_money += lottery.summa / len(winners)
                            winner.save()
                        else:
                            s = SessionStore(session_key=winner.session_key_user)
                            s["summa"] += lottery.summa
                            s.save()
                            winner.win_money += lottery.summa
                            winner.save()
        context["winners"] = []
        context["members"] = []
        if "list-members" in request.GET.keys():
            lottery = Lottery.objects.get(id=request.GET.get("list-members"))
            context["members"] = lottery.members.all()
            context["lottery"] = lottery
        if "list-winners" in request.GET.keys():
            if request.GET.get("list-winners"):
                lottery = Lottery.objects.get(id=request.GET.get("list-winners"))
                context["winners"] = MemberLottery.objects.filter(winner=True, lottery=lottery)
                context["lottery"] = lottery
            else:
                lotteries = Lottery.objects.filter(finish=True)
                winners = []
                for lottery in lotteries:
                    for member in MemberLottery.objects.filter(winner=True, lottery=lottery):
                        winners.append(member)
                context["winners"] = winners
                context["lottery"] = None
        return render(request, "mainapp/lotteries.html", context)

