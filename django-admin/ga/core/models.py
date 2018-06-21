from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _


class Order(models.Model):
    """
    List of user orders.
    """
    RUS_LANGUAGE = "rus"
    ENG_LANGUAGE = "eng"
    LANGUAGE = (
        (ENG_LANGUAGE, _("Английский")),
        (RUS_LANGUAGE, _("Русский")),
    )
    NEW_STATUS = "new"
    ACTIVE_STATUS = "active"
    DONE_STATUS = "done"
    STATUSES = (
        (NEW_STATUS, _("Новый (письмо подтверждения не отправлено)")),
        (ACTIVE_STATUS, _("Активен")),
        (DONE_STATUS, _("Обработан"))
    )

    dt_created = models.DateTimeField(null=False, auto_now_add=True,
                                      verbose_name=_("Дата создания"))
    user_email = models.CharField(null=False, max_length=250,
                                  verbose_name="E-mail")
    user_name = models.CharField(null=True, blank=True, max_length=250,
                                 verbose_name=_("ФИО"))
    lng = models.CharField(null=False, max_length=5, choices=LANGUAGE,
                           default=RUS_LANGUAGE, verbose_name=_("Язык"))
    user_id = models.CharField(null=True, blank=True, max_length=250,
                               verbose_name=_("ID пользователя"))
    status = models.CharField(null=False, max_length=20, choices=STATUSES,
                              default=NEW_STATUS, verbose_name=_("Статус"))
    dp = models.CharField(null=False, max_length=100,
                                 verbose_name=_("123"))
    d = models.CharField(null=False, max_length=100,
                                   verbose_name=_("123"))
    dp_code = models.CharField(null=False, max_length=100,
                                      verbose_name=_("123"))
    d_code = models.CharField(null=False, max_length=100,
                                        verbose_name=_("123"))
    token = models.TextField(null=False)
    dt_dp = models.DateField(null=False,
                                    verbose_name=_("123"))
    dt_confirmation = models.DateTimeField(null=True,
                                           verbose_name=_("123"))
    dt_finish = models.DateTimeField(null=True,
                                     verbose_name=_("123"))

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        indexes = [
            models.Index(fields=['dt_dp', ]),
        ]


class OrderItem(models.Model):
    """
    List of order items.
    """
    ACTIVE_STATUS = "active"
    FAIL_SEND_STATUS = "fail_send"
    SUCCESS_SEND_STATUS = "success_send"
    STATUSES = (
        (ACTIVE_STATUS, _("Активен")),
        (FAIL_SEND_STATUS, _("Сбой отправки")),
        (SUCCESS_SEND_STATUS, _("Направлено")),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    ttt_id = models.CharField(null=False, max_length=20,
                                verbose_name="123")
    ttt_name = models.CharField(null=True, max_length=250, blank=True,
                                  verbose_name=_("123"))
    dt_start_sell = models.DateTimeField(null=False,
                                         verbose_name=_("123"))
    start_s = models.CharField(null=False, max_length=250,
                                     verbose_name=_("123"))
    end_s = models.CharField(null=False, max_length=250,
                                   verbose_name=_("123"))
    status = models.CharField(null=False, max_length=20, choices=STATUSES,
                              default=ACTIVE_STATUS, verbose_name=_("Статус"))
    dt_dp = models.DateTimeField(null=False,
                                        verbose_name=_("123"))
    dt_arrival = models.DateTimeField(null=False,
                                      verbose_name=_("123"))
    dt_finish = models.DateTimeField(null=True,
                                     verbose_name=_("123"))
    dt_confirmation = models.DateTimeField(null=True,
                                           verbose_name=_("123"))

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
        indexes = [
            models.Index(fields=['order', ]),
            models.Index(fields=['ttt_id', ]),
        ]


class Settings(models.Model):
    """
    General settings
    """
    MAILING_TASK_LABEL = "mailing_task"
    MAILING_TASK_NAME = "mailing.celery.start_mailing"

    domain = models.CharField(null=False, max_length=250,
                              verbose_name=_("Домен"))
    mailing_time = models.TimeField(null=False,
                                    verbose_name=_("Время рассылки (МСК)"))
    mailing_threads = models.IntegerField(
        null=False, default=10, verbose_name=_("Количество потоков"))
    mails_keeping_days = models.IntegerField(
        null=False, default=30,
        verbose_name=_("Хранение исполненных заказов (дней)"))
    ttt_check_period = models.IntegerField(
        null=False, default=5,
        verbose_name=_("123"))
    ttt_keep_age = models.IntegerField(
        null=False, default=10,
        verbose_name=_("123"))

    class Meta:
        verbose_name = _("Настройка")
        verbose_name_plural = _("Настройки")

    @staticmethod
    def post_save(sender, instance, created, **kwargs):
        """
        Update djcelery beat schedule
        :param sender: The model class (Settings)
        :param instance: The actual instance being saved.
        :param created: A boolean; True if a new record was created
        :return:
        """

        # for migrations process
        if created:
            return

        from djcelery.models import PeriodicTask, CrontabSchedule

        try:
            task_object = PeriodicTask.objects.get(
                name=Settings.MAILING_TASK_LABEL)
            cron_object = task_object.crontab
        except ObjectDoesNotExist:
            cron_object = CrontabSchedule()
            task_object = PeriodicTask(
                name=Settings.MAILING_TASK_LABEL,
                task=Settings.MAILING_TASK_NAME
            )

        cron_object.minute = instance.mailing_time.minute
        cron_object.hour = instance.mailing_time.hour
        cron_object.save()

        task_object.crontab = cron_object
        task_object.args = "[{}]".format(instance.mailing_threads)
        task_object.save()


post_save.connect(Settings.post_save, sender=Settings)


class Tt(models.Model):
    """
    List of ttts.
    """
    RUS_LANGUAGE = "rus"
    ENG_LANGUAGE = "eng"
    LANGUAGE = (
        (ENG_LANGUAGE, _("Английский")),
        (RUS_LANGUAGE, _("Русский")),
    )
    request_origin_code = models.CharField(
        null=False, max_length=7,
        verbose_name=_("123"))
    request_d_code = models.CharField(
        null=False, max_length=7,
        verbose_name=_("123"))
    ttt_id = models.CharField(
        null=False, max_length=255,
        verbose_name=_("123"))
    ttt_name = models.CharField(
        null=True, max_length=255,
        verbose_name=_("123"))
    dt_dp = models.DateTimeField(
        null=False,
        verbose_name=_("123"))
    dt_arrival = models.DateTimeField(
        null=True,
        verbose_name=_("123"))
    td = models.IntegerField(
        null=True,
        verbose_name=_("123"))
    ttt_oname = models.CharField(
        null=True, max_length=255,
        verbose_name=_("123"))
    ttt_d_name = models.CharField(
        null=True, max_length=255,
        verbose_name=_("123"))
    c_type_list = models.CharField(
        null=True, max_length=255,
        verbose_name=_("123"))
    cs = models.CharField(
        null=True, max_length=255,
        verbose_name=_("123"))
    sales_depth = models.IntegerField(
        null=False,
        verbose_name=_("123"))
    dt_loaded = models.DateTimeField(
        null=False, auto_now_add=True,
        verbose_name=_("123"))
    dt_last_cache_update = models.DateTimeField(
        null=True,
        verbose_name=_("123"))

    class Meta:
        verbose_name = _('123')
        verbose_name_plural = _('123')

        indexes = [
            models.Index(fields=['ttt_id',
                                 'request_o_code',
                                 'request_d_code',
                                 'dt_dp']),
        ]


class Log(models.Model):
    """
    Orders log.
    """
    NEW_STATUS = "new"
    ACTIVE_STATUS = "active"
    FAIL_SEND_STATUS = "fail_send"
    SUCCESS_SEND_STATUS = "success_send"
    DONE_STATUS = "done"
    STATUSES = (
        (NEW_STATUS, _("Заказ: Новый (письмо подтверждения не отправлено)")),
        (ACTIVE_STATUS, _("Заказ: Активен")),
        (FAIL_SEND_STATUS, _("Элемент заказа: Сбой отправки")),
        (SUCCESS_SEND_STATUS, _("Элемент заказа: Направлено")),
        (DONE_STATUS, _("Элемент заказа: Обработан"))
    )
    order = models.ForeignKey(Order,
                              verbose_name=_("Заказ"))
    dt_created = models.DateTimeField(null=False,
                                      verbose_name=_("Время события"))
    action = models.CharField(null=False, max_length=20,
                              verbose_name=_("Категория события"),
                              choices=STATUSES)

    class Meta:
        verbose_name = _('Мониторинг')
        verbose_name_plural = _('Мониторинг')

        indexes = [
            models.Index(fields=['order', ]),
        ]
