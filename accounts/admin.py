from django.contrib import admin
from .models import CustomUser, AxieSetting, SlpPayLog, SlpDailyLog, SlpMonthlyLog
import datetime

# 削除する捜査を削除
admin.site.disable_action('delete_selected')


@admin.register(AxieSetting)
class AxieAdmin(admin.ModelAdmin):
    list_display = ['today_slp']


day_pay = AxieSetting.objects.get(pk=1)

"""データ抽出日時調整"""
d = datetime.date.today()  # 今日
fd = d.replace(day=1)  # 同月1日


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'axie_status']
    actions = ["daily_earn"]

    def daily_earn(self, request, queryset):
        for obj in queryset:
            if obj.axie_status == "AXIE_ON":
                if obj.axie_rank == "AXIE0":
                    obj.axie_daily_earn = day_pay.today_slp * day_pay.axie0_rate
                    obj.axie_all_earn = obj.axie_all_earn + obj.axie_daily_earn
                    if d == fd:  # 月初に初期化
                        obj.axie_monthly_earn = obj.axie_daily_earn
                    else:  # 月初でなければその日の報酬額を追加
                        obj.axie_monthly_earn = obj.axie_monthly_earn + obj.axie_daily_earn
                    obj.save()

                    """
                    条件分岐                    
                    """
            else:
                pass

    daily_earn.short_description = "報酬の配布"


@admin.register(SlpPayLog)
class UserPayLogAdmin(admin.ModelAdmin):
    list_display = ["pay_log_id", 'pay_log_day', 'pay_log_data']


@admin.register(SlpDailyLog)
class UserDailyLogAdmin(admin.ModelAdmin):
    list_display = ['daily_log_id', 'daily_log_day', "daily_log_data"]


@admin.register(SlpMonthlyLog)
class UserMonthlyLogAdmin(admin.ModelAdmin):
    list_display = ['monthly_log_id', 'monthly_log_day', "monthly_log_data"]
