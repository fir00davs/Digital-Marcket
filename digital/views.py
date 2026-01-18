from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from .models import *
from .forms import LoginForm, RegisterForm, DeliveryForm, EditAccountForm, EditCustomerForm
from django.contrib.auth import login, logout
from django.contrib import messages

from .tests import filter_products
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import CartForAuthenticatedUser, cart_info
import stripe
from store.settings import STRIPE_SECRET_KEY


# Главная страница
class MainPage(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'digital/index.html'
    extra_context = {'title': 'Digital Market'}

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)
        return categories


# Страница 	карточки товара
class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data()
        product = context['product']
        context['title'] = product.title
        context['same_models'] = Product.objects.filter(model=product.model)
        context['same_products'] = Product.objects.filter(category__parent=product.category.parent).exclude(pk=product.pk)
        return context


# Страница регистрации пользователей
def auth_register_page(request):
    if request.user.is_authenticated:
        return redirect('main')

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main')
    else:
        form = RegisterForm()

    context = {
        'title': 'Регистрация',
        'reg_form': form,
    }
    return render(request, 'digital/registration.html', context)


# Страница авторизации
def auth_login_page(request):
    if request.user.is_authenticated:

        return redirect('main')
    else:
        context = {
            'title': 'Авторизация',
            'log_form': LoginForm()
        }
        return render(request, 'digital/auth.html', context)


# Страница входа
def login_user_view(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                if user:
                    login(request, user)
                    messages.success(request, 'Авторизация прошла успешно')
                    return redirect('main')
            messages.error(request, 'Не верный логин или пароль')
            return redirect('auth')
    else:

        return redirect('main')


# Страница выхода
def logout_user_view(request):
    logout(request)
    messages.success(request, 'Уже уходите')
    return redirect('main')


# Страница полной регистрации
def register_user_view(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = RegisterForm(request.POST, request.FILES)   # ← добавили request.FILES
            if form.is_valid():
                user = form.save()
                phone_number = form.cleaned_data.get('phone_number')
                photo = form.cleaned_data.get('photo')         # ← берём из form.cleaned_data

                customer = Customer.objects.create(
                    user=user,
                    phone_number=phone_number,
                    photo=photo
                )
                Cart.objects.create(customer=customer)
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно')
            else:
                for err in form.errors:
                    messages.error(request, form.errors[err].as_text())
        return redirect('auth')
    else:
        return redirect('main')



# Страница товаров в категорие
class ProductByCategory(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'digital/category.html'
    paginate_by = 3

    def get_queryset(self):
        category = Category.objects.get(slug=self.kwargs['slug'])
        products = Product.objects.filter(category__in=category.subcategories.all())
        products = filter_products(self.request, products)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductByCategory, self).get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        context['title'] = category.title
        context['subcats'] = category.subcategories.all()
        context['prices'] = [i for i in range(500, 100001, 500)]
        products = Product.objects.filter(category__slug=self.request.GET.get('cat'))
        context['models'] = set([i.model for i in products])

        return context


# Страница для добавление товаров в избраное и удаление
@login_required(login_url='auth')
def save_favorite_product(request, slug):
    user = request.user
    product = Product.objects.get(slug=slug)
    favorites = FavoriteProduct.objects.filter(user=user)

    if product in [i.product for i in favorites]:
        fav = FavoriteProduct.objects.get(user=user, product=product)
        fav.delete()
        messages.success(request, 'Товар удалён из избранного')
    else:
        FavoriteProduct.objects.create(user=user, product=product)
        messages.success(request, 'Товар добавлен в избранное')

    next_page = request.META.get('HTTP_REFERER', 'main')
    return redirect(next_page)


# Список избранного
class FavoriteList(LoginRequiredMixin, ListView):
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'digital/product_list.html'
    extra_context = {'title': 'Избранные товары'}
    paginate_by = 3
    login_url = 'auth'

    def get_queryset(self):
        products = FavoriteProduct.objects.filter(user=self.request.user)
        products = [i.product for i in products]
        return products


# Страница добавление и удаление товара в корзину
@login_required(login_url='auth')
def add_or_delete_view(request, slug, action):
    result = CartForAuthenticatedUser(request, slug, action)

    if action == 'add':
        product = Product.objects.get(slug=slug)
        messages.success(request, 'Продукт добавлен в корзину')
    elif action == 'delete':
        product = Product.objects.get(slug=slug)
        messages.success(request, 'Продукт удалён из корзины')

    next_page = request.META.get('HTTP_REFERER', 'main')
    return redirect(next_page)


# Страница корзины
@login_required(login_url='auth')
def my_cart_view(request):
    cart = cart_info(request)
    context = {
        'title': 'Корзина',
        'products_cart': cart['products_cart'],
        'cart_price': cart['cart_price'],
        'cart_quantity': cart['cart_quantity']
    }
    return render(request, 'digital/my_cart.html', context)


# Очистка корзины
@login_required(login_url='auth')
def clear_cart_view(request):
    CartForAuthenticatedUser(request, slug=None, action='clear')
    messages.success(request, 'Корзина успешно очищена')
    next_page = request.META.get('HTTP_REFERER', 'basket')
    return redirect(next_page)


# Страница формы доставки
@login_required(login_url='auth')
def checkout_view(request):
    cart = cart_info(request)
    if cart['products_cart'] and request.method == 'POST':
        context = {
            'products_cart': cart['products_cart'],
            'cart': cart['cart'],
            'title': 'Оформление заказа',
            'form': DeliveryForm()
        }

        return render(request, 'digital/checkout.html', context)
    else:
        return redirect('main')


# Страница оплаты
@login_required(login_url='auth')
def create_checkout_session(request):
    stripe.api_key = STRIPE_SECRET_KEY
    if request.method == 'POST':
        cart = cart_info(request)
        price = cart['cart_price']
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': ',\n'.join(i.product.title for i in cart['products_cart'])},
                    'unit_amount': int(price) * 100
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )

        request.session[f'form_{request.user.pk}'] = request.POST
        return redirect(session.url)


# Страница сохранение оплаты
@login_required(login_url='auth')
def success_payment(request):
    cart = cart_info(request)

    try:
        form_data = request.session.get(f'form_{request.user.pk}')
        request.session.pop(f'form_{request.user.pk}')
    except:
        form_data = None

    if not cart['products_cart'] or not form_data:
        messages.error(request, 'Ошибка: корзина пуста или данные формы утеряны')
        return redirect('main')

    ship_form = DeliveryForm(data=form_data)
    if ship_form.is_valid():
        delivery = ship_form.save(commit=False)
        delivery.customer = Customer.objects.get(user=request.user)
        delivery.save()

        cart_user = CartForAuthenticatedUser(request)
        cart_user.save_order(delivery)
        cart_user.clear_cart()

        messages.success(request, f'Заказ успешно оплачен и оформлен')
        context = {'title': 'Успешная оплата', 'order_id': delivery.id}
        return render(request, 'digital/success.html', context)
    else:
        messages.error(request, 'Ошибка в данных доставки. Вернитесь к оформлению')
        return redirect('checkout')


# Страница профеля покупателя
@login_required(login_url='auth')
def profile_customer_view(request):
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer).order_by('-created_at')[:5]

    context = {
        'title': f'Профиль {request.user.username}',
        'user': request.user,
        'customer': customer,
        'orders': orders
    }
    return render(request, 'digital/profile.html', context)


# Страница редактирование
@login_required(login_url='auth')
def edit_profile_view(request):
    customer = Customer.objects.get(user=request.user)

    account_form = EditAccountForm(instance=request.user)
    customer_form = EditCustomerForm(instance=customer)

    if request.method == 'POST':
        account_form = EditAccountForm(request.POST, instance=request.user)
        customer_form = EditCustomerForm(request.POST, request.FILES, instance=customer)

        if account_form.is_valid() and customer_form.is_valid():
            account_form.save()
            customer_form.save()
            messages.success(request, 'Профиль обновлён')
            return redirect('profile')

    context = {
        'title': 'Редактировать профиль',
        'account_form': account_form,
        'customer_form': customer_form
    }
    return render(request, 'digital/edit_profile.html', context)


# Страница поиска
def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(title__icontains=query)

    context = {
        'title': f'Поиск: {query}',
        'products': products,
        'query': query
    }
    return render(request, 'digital/search.html', context)










