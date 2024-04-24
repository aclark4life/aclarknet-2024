from django import template
from django.contrib.staticfiles.finders import find as find_static_file
from django.conf import settings

register = template.Library()


@register.simple_tag
def encode_static(path, encoding="base64", file_type="image"):
    """
    a template tag that returns a encoded string representation of a staticfile

    Usage::

        {% encode_static path [encoding] %}

    Examples::

        <img src="{% encode_static 'path/to/img.png' %}">
    """
    file_path = find_static_file(path)
    ext = file_path.split(".")[-1]
    file_str = get_file_data(file_path).encode(encoding)
    return "data:{0}/{1};{2},{3}".format(file_type, ext, encoding, file_str)


@register.simple_tag
def raw_static(path):
    """
    a template tag that returns a raw staticfile

    Usage::

        {% raw_static path %}

    Examples::
        <style>{% raw_static path/to/style.css %}</style>

    """
    if path.startswith(settings.STATIC_URL):
        # remove static_url if its included in the path
        path = path.replace(settings.STATIC_URL, "")
    file_path = find_static_file(path)
    return get_file_data(file_path)


def get_file_data(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        f.close()
        return data
