from django import template

from core.utils import to_bn

register = template.Library()


@register.filter(name="bn")
def bn(value):
    """সংখ্যা/টেক্সটের ইংরেজি অঙ্কগুলোকে বাংলা অঙ্কে দেখায়।"""
    return to_bn(value)
