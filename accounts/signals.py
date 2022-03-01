from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .admin import UserAdmin
from .models import CustomUser, SlpDailyLog, SlpMonthlyLog
import datetime

"""データ抽出日時調整"""
d = datetime.date.today()  # 今日
fd = d.replace(day=1)  # 同月1日


@receiver(pre_save, sender=CustomUser)
def sample(sender, instance, *args, **kwargs):
    SlpDailyLog.objects.create(daily_log_id=instance,
                               daily_log_day=timezone.now(),
                               daily_log_data=instance.axie_daily_earn)

    if d == fd:  # 月初に保存
        last_monthly_earn = instance.tracker.previous('axie_monthly_earn')
        SlpMonthlyLog.objects.create(monthly_log_id=instance,
                                     monthly_log_day=timezone.now(),
                                     monthly_log_data=last_monthly_earn)
    else:  # 月初でなければその日の報酬額を追加
        pass

