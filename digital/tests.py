from django.test import TestCase

# Create your tests here.
def filter_products(request, products):
    cat = request.GET.get('cat')
    price_from = request.GET.get('price_from')
    price_to = request.GET.get('price_to')
    model = request.GET.get('model')

    if cat:
        products = products.filter(category__slug=cat)
    if price_from:
        products = products.filter(price__gte=price_from)
    if price_to:
        products = products.filter(price__lte=price_to)
    if model:
        products = products.filter(model__slug=model)

    return products

