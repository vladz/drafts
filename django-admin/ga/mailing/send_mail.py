from typing import TYPE_CHECKING, List
from datetime import timedelta, datetime, date
import logging

from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template as DjangoTemplate
from django.utils.html import strip_tags
from django.conf import settings

from mailing.settings import (CONFIRMATION_TYPE_MESSAGE,
                              NOTIFICATION_TYPE_MESSAGE)
from mailing.build_tpl import build_ttt_table

if TYPE_CHECKING:
    from core.models import Order, OrderItem
    from mailing.data_classes import DeepSales

logger = logging.getLogger("main")


def send(order: 'Order', order_items: 'List[OrderItem]',
         domain: str, type_msg: str) -> bool:
    """
    Send mail

    :param order: order of user
    :param order_items: items of order
    :param domain: domain to unsubscribe
    :param type_msg: type of message (for pick template)
    :return:
    """
    from core.models import Order
    from mailing.models import Template

    from_email = settings.DEFAULT_FROM_EMAIL

    template_obj = Template.objects.get(slug=type_msg)
    template = template_obj.rus_template
    subject = template_obj.rus_title

    if order.lng == Order.ENG_LANGUAGE:
        template = template_obj.eng_template
        subject = template_obj.eng_title
    tpl = DjangoTemplate(template)
    pixel_link = "{}/api/tr.png?token={}&status={}".format(
        domain,
        order.token,
        type_msg
    )
    if type_msg == NOTIFICATION_TYPE_MESSAGE:
        order_items_id = [str(item.pk) for item in order_items]
        pixel_link = "{}&items={}".format(pixel_link, ",".join(order_items_id))

    context = Context(
        {
            'name': order.user_name,
            'dt_dp': order.dt_dp,
            'dp': order.dp,
            'd': order.d,
            'ttt_table': build_ttt_table(order_items, order.lng),
            'buy_link': "<buy_link>",
            'unsubscribe_link': "/unsubscribe?token={}&lng={}".format(
                order.token, order.lng),
            'pixel': "<img src='{}' />".format(pixel_link)
        }
    )
    html_content = tpl.render(context)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email,
                                 [order.user_email])
    msg.attach_alternative(html_content, "text/html")
    return msg.send()


def send_confirmation(order: 'Order', domain: str):
    """
    Fill template and send confirmation mail

    :param order: order of user
    :param domain: domain to unsubscribe
    :return:
    """
    from core.models import Order, OrderItem
    order_items = OrderItem.objects.filter(order=order)

    send(order, order_items, domain, CONFIRMATION_TYPE_MESSAGE)

    order.status = Order.ACTIVE_STATUS
    order.save()


def send_notification(order_items: 'List[OrderItem]',
                      sales_depth: int, domain: str):
    """
    Fill template and send notification mail

    :param order_items: items of order
    :param sales_depth: day to sales
    :param domain: domain of site
    :return:
    """
    from core.models import OrderItem

    day_before = 1
    sales_depth += day_before
    today = date.today()

    for order_item in order_items:
        dt_start_sale = order_item.dt_dp - timedelta(days=sales_depth)

        logger.debug("Dates: {} - {}, Tt: {}".format(
                     today, dt_start_sale.date(), order_item.ttt_id))

        if dt_start_sale.date() > today:
            continue

        logger.debug("Tt: {}, Send Email".format(order_item.ttt_id))

        order_item.status = order_item.SUCCESS_SEND_STATUS

        if not send(order_item.order, [order_item], domain,
                    NOTIFICATION_TYPE_MESSAGE):
            order_item.status = order_item.FAIL_SEND_STATUS

        order_item.dt_finish = datetime.now()
        order_item.save()

        # are there order items. if not - set done status
        rest_items = OrderItem.objects.filter(order=order_item.order).exclude(
            status=order_item.FAIL_SEND_STATUS).exclude(
            status=order_item.SUCCESS_SEND_STATUS)

        if not rest_items:
            order_item.order.status = order_item.order.DONE_STATUS
            order_item.order.dt_finish = datetime.now()
            order_item.order.save()
