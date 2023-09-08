from django.urls import path
from .views import MainPageView, BetLotteryView, LotteriesView, export_lottery_excel, ExportMembersView, ExportWinnersView, ExportWinnersAllView

urlpatterns = [
    path("", MainPageView.as_view(), name="main-page"),
    path("bet/<int:id>", BetLotteryView.as_view(), name="bet-lottery"),
    path("lotteries", LotteriesView.as_view(), name="lotteries"),
    path("export-lottery/", export_lottery_excel, name="export-lottery"),
    path("export-members/<int:id>", ExportMembersView.as_view(), name="export-members"),
    path("export-winners/<int:id>", ExportWinnersView.as_view(), name="export-winners"),
    path("export-all-winners/", ExportWinnersAllView.as_view(), name="export-all-winners")
]