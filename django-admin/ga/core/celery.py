import logging
from datetime import datetime, timedelta
import pytz

from celery.app import shared_task

logger = logging.getLogger("main")


def delete_ttt_cache():
    """
    delete old cache
    :return:
    """
    from core.models import Tt, Settings
    utc = pytz.UTC
    settings = Settings.objects.all()

    for ttt in Tt.objects.all():
        if ttt.dt_loaded is None:
            continue

        max_time_live = ttt.dt_loaded + timedelta(
            days=settings[0].ttt_keep_age)
        now = utc.localize(datetime.now())
        if max_time_live < now:
            ttt.delete()


def clear_orders():
    """
    to delete all orders, if they are old
    :return:
    """
    from core.models import Order, Settings
    utc = pytz.UTC
    settings = Settings.objects.all()

    orders = Order.objects.filter(status=Order.DONE_STATUS)
    for order in orders:
        if order.dt_finish is None:
            continue

        max_time_live = order.dt_finish + timedelta(
            days=settings[0].ttt_keep_age)
        now = utc.localize(datetime.now())
        if max_time_live < now:
            order.delete()


@shared_task()
def check_background_task():
    """
    to check all tasks, that we should perform
    :return:
    """
    clear_orders()
    delete_ttt_cache()
