from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import base64
import logging
import json
from typing import List

from celery.app import shared_task
from django.conf import settings
import requests
import pytz

from mailing.send_mail import send_confirmation, send_notification
from mailing.data_classes import LDS, DeepS

logger = logging.getLogger("main")


@shared_task()
def start_mailing(threads: int):
    """
    Notifications about tickets start sales

    :param threads: number of threads of sending email
    :return:
    """
    from core.models import OrderItem, Settings

    utc = pytz.UTC
    now = utc.localize(datetime.now())
    today = now.date()

    orders_items: List[OrderItem] = OrderItem.objects.filter(
        status=OrderItem.ACTIVE_STATUS,
        order__dt_dp__gte=today).select_related("order").all()

    if not orders_items:
        return

    group_order_items = {}
    orders_dict = {}
    ttts: ListDeepSales
    settings_obj = Settings.objects.all()
    executor = ThreadPoolExecutor(max_workers=threads)

    user_pass = base64.b64encode("{}:{}".format(
        settings.EXT_USER, settings.EXT_PASSWORD).encode())
    headers = {
        "Authorization": "Basic {}".format(user_pass.decode()),
        "Pos": settings.EXT_POS,
    }

    # group parameters
    for order_one in orders_items:
        # group ttt data
        dep_code = order_one.order.dp_code
        dest_code = order_one.order.d_code
        dep_date = order_one.order.dt_dp

        group_order_items.setdefault(dep_code, {}).setdefault(dest_code, set())
        group_order_items[dep_code][dest_code].add(dep_date)

        # group order data
        orders_dict.setdefault(dep_date, {}).setdefault(order_one.ttt_id, [])
        orders_dict[dep_date][order_one.ttt_id].append(order_one)

    # check all dates of all order item
    url = "{}/EXT_API/SddDirection".format(settings.EXT_URL)
    for dep_code in group_order_items:
        for dest_code in group_order_items[dep_code]:
            dep_dates = group_order_items[dep_code][dest_code]
            for dep_date_one in dep_dates:
                logger.debug(f'{dep_date_one} - {dep_code} - {dest_code}')
                json_data = {
                    "OrCode": dep_code,
                    "DCode": dest_code,
                    "DDate": dep_date_one.strftime(
                        "%Y-%m-%dT%H:%m:00.000"),
                }
                try:
                    answer = requests.post(url,
                                           headers=headers, json=json_data)
                except requests.exceptions.ConnectionError:
                    logger.error("can not connect to {}".format(url))
                    break

                if answer.status_code != 200:
                    logger.error(answer.text)
                    break

                try:
                    ttts = ListDeepSales.from_json(answer.text)
                except json.JSONDecodeError as e:
                    logger.error(e)

                if settings.DEBUG:
                    test_items = OrderItem.objects.filter(
                        ttt_id=settings.TEST_T_NUMBER,
                        order__dt_dp=dep_date_one)
                    if test_items:
                        order_item = test_items[0]
                        dt_start_sale = order_item.dt_dp - now

                        logger.debug(f'now: {now}, '
                                     f'dt_dep: {order_item.dt_dp}, '
                                     f'delta: {int(dt_start_sale.days)}')

                        ttts.SddTts.append(
                            DeepSales(
                                TtNumber=settings.TEST_T_NUMBER,
                                Sdd=int(dt_start_sale.days)
                            )
                        )

                if not ttts.SddTts:
                    continue

                # iterate by results (from remote API)
                for ttt_one in ttts.SddTts:
                    logger.debug(f'{ttt_one}')
                    if ttt_one.TtNumber in orders_dict[dep_date_one]:
                        logger.debug(f'{ttt_one} in orders')
                        executor.submit(
                            send_notification,
                            orders_dict[dep_date_one][ttt_one.TtNumber],
                            ttt_one.Sdd, settings_obj[0].domain)


@shared_task()
def accept_order():
    """
    Confirmation new Order

    :return:
    """
    from core.models import Order, Settings

    orders = Order.objects.filter(status=Order.NEW_STATUS)
    settings_obj = Settings.objects.all()
    executor = ThreadPoolExecutor(max_workers=settings_obj[0].mailing_threads)
    for order_one in orders:
        executor.submit(send_confirmation, order_one, settings_obj[0].domain)
