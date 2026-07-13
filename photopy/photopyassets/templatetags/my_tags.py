from django import template

register = template.Library()

@register.simple_tag
def my_tag():
    return "Hello World from my_tag()"

@register.simple_tag
def hello_tag():
    return "Halo Dunia dari hello_tag!"
