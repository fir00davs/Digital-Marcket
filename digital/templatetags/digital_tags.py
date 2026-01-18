from digital.models import Category, FavoriteProduct
from django import template

register = template.Library()


@register.simple_tag()
def get_categories():
    categories = Category.objects.filter(parent=None)
    return categories

@register.simple_tag(takes_context=True)
def query_params(context, **kwargs):
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        if value is not None and (key != 'page' or value != 1):
            query[key] = value
        elif key in query:
            del query[key]

        lst = ['model', 'price_to', 'price_from']
        if key == 'cat':
            for i in lst:
                try:
                    del query[i]
                except:
                    pass


    return query.urlencode()

@register.simple_tag()
def get_favorites(user):
    favorites = FavoriteProduct.objects.filter(user=user)
    products = [i.product for i in favorites]
    return products









