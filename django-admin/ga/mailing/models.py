from django.db import models
from django.utils.translation import ugettext_lazy as _


class Template(models.Model):
    """
    Html-templates
    """

    T_TABLE = "123"
    SALES_NOTIFICATION = "123"
    CONFIRM_ORDER = "Подтверждение заказа"
    NAMES = (
        (T_TABLE, _("123")),
        (SALES_NOTIFICATION, _("123")),
        (CONFIRM_ORDER, _("Подтверждение заказа"))
    )

    name = models.CharField(null=False, max_length=250,
                            verbose_name=_("Название"), choices=NAMES)
    slug = models.CharField(null=False, max_length=20, verbose_name=_("Метка"))
    eng_template = models.TextField(null=False,
                                    verbose_name=_("Шаблон на английском"))
    rus_template = models.TextField(null=False,
                                    verbose_name=_("Шаблон на русском"))
    eng_title = models.CharField(null=False, max_length=250,
                                 verbose_name=_("Тема на английском"))
    rus_title = models.CharField(null=False, max_length=250,
                                 verbose_name=_("Тема на русском"))

    class Meta:
        verbose_name = _('Шаблон')
        verbose_name_plural = _('Шаблоны')
