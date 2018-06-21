from typing import List, TYPE_CHECKING, Union
from django.template import Context, Template as DjangoTemplate


if TYPE_CHECKING:
    from core.models import OrderItem
    from django.utils.safestring import SafeBytes, SafeString


def build_ttt_table(order_items: List['OrderItem'],
                      lng: str) -> 'Union[SafeBytes, SafeString]':
    from core.models import Order
    from mailing.models import Template
    type_message = "ttt_table"

    template_obj = Template.objects.get(slug=type_message)
    template = template_obj.rus_template
    if lng == Order.ENG_LANGUAGE:
        template = template_obj.eng_template
    tpl = DjangoTemplate(template)
    context = Context(
        {
            'ttts': order_items,
        }
    )
    return tpl.render(context)
