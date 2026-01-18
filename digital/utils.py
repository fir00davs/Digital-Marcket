from .models import Cart, ProductCart, Product, Customer, Order, ProductOrder


class CartForAuthenticatedUser:
    def __init__(self, request, slug=None, action=None):
        self.user = request.user
        if action:
            self.add_or_delete(slug, action)

    def get_cart_info(self):
        customer = Customer.objects.get(user=self.user)
        cart = Cart.objects.get(customer=customer)
        products_cart = cart.productcart_set.all()
        return {
            'cart': cart,
            'products_cart': products_cart,
            'cart_price': cart.cart_total_price,
            'cart_quantity': cart.cart_total_quantity,
            'customer': customer
        }

    def add_or_delete(self, slug, action):
        cart = self.get_cart_info()['cart']

        if action == 'clear' and slug is None:
            cart.productcart_set.all().delete()
            return

        product = Product.objects.get(slug=slug)
        product_cart, created = ProductCart.objects.get_or_create(cart=cart, product=product)

        if action == 'add' and product.quantity > 0 and product_cart.quantity < product.quantity:
            product_cart.quantity += 1
        elif action == 'delete':
            product_cart.quantity -= 1
        elif action == 'clear':
            product_cart.quantity = 0

        product_cart.save()

        if product_cart.quantity <= 0:
            product_cart.delete()

    def save_order(self, delivery):
        """✅ ДОБАВЛЕН СВЕТ!"""
        data = self.get_cart_info()
        order = Order.objects.create(
            customer=data['customer'],
            delivery=delivery,
            price=data['cart_price'],
            cart=data['cart']
        )
        order.save()

        for p_cart in data['products_cart']:
            ProductOrder.objects.create(
                order=order,
                name=p_cart.product.title,
                slug=p_cart.product.slug,
                price=p_cart.product.get_price(),
                photo=p_cart.product.image,
                color_name=p_cart.product.color_name,
                quantity=p_cart.quantity,
                total_price=p_cart.quantity * p_cart.product.get_price()
            )
        return order

    def clear_cart(self):
        cart = self.get_cart_info()['cart']
        products_cart = cart.productcart_set.all()
        for p_cart in products_cart:
            product = p_cart.product
            product.quantity -= p_cart.quantity
            product.save()
            p_cart.delete()
        cart.save()


def cart_info(request):
    if request.user.is_authenticated:
        cart = CartForAuthenticatedUser(request)
        return cart.get_cart_info()
    return {'cart_price': 0, 'cart_quantity': 0, 'products_cart': []}
