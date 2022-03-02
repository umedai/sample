from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin
from model_utils import FieldTracker


class UserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('メールアドレス', unique=True)
    first_name = models.CharField('姓', max_length=30)
    last_name = models.CharField('名', max_length=30)

    # Axieの報酬管理
    daily_earn = models.DecimalField("本日の収益(SLP)", max_digits=10, decimal_places=3, default="0")
    monthly_earn = models.DecimalField("今月の収益(SLP)", max_digits=10, decimal_places=3, default="0")
    all_earn = models.DecimalField("総収益(SLP)", max_digits=10, decimal_places=3, default="0")
    axie_payout = models.DecimalField("出金額(SLP)", max_digits=10, decimal_places=3, default="0")
    tracker = FieldTracker()

    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text=(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):  # __unicode__ in python 2.*
        return self.email


# 毎日の獲得報酬ログ
class SlpDailyLog(models.Model):
    daily_log_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    daily_log_day = models.DateField("日付", auto_now=True, auto_now_add=False)
    daily_log_data = models.DecimalField("金額", max_digits=10, decimal_places=3, default="0")


# 月々の獲得報酬ログ
class SlpMonthlyLog(models.Model):
    monthly_log_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    monthly_log_day = models.DateField("日付", auto_now=True, auto_now_add=False)
    monthly_log_data = models.DecimalField("金額", max_digits=10, decimal_places=3, default="0")


# 入出金管理ログモデル
class SlpPayLog(models.Model):
    pay_log_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pay_log_day = models.DateField("日付", auto_now=True, auto_now_add=False)
    pay_log_data = models.DecimalField("金額", max_digits=10, decimal_places=3, default="0")
    axie_all_payout = models.DecimalField("総出金額(SLP)", max_digits=10, decimal_places=3, default="0")

    # 申請中判定
    SENDING = "sending"
    OUT = "out"
    STATUS = [
        (SENDING, "申請中"),
        (OUT, "出金済")
    ]
    pay_status = models.CharField(
        "出金管理ステータス",
        max_length=8,
        choices=STATUS,
    )
