from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

# Create your models here.


# Категории товаров
class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название')
    icon = models.ImageField(upload_to='icons/', verbose_name='Иконка', null=True, blank=True)
    slug = models.SlugField(unique=True, verbose_name='Слаг категории')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Родитель',
                               related_name='subcategories', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    def get_icon(self):
        if self.icon:
            return self.icon.url
        else:
            return '-'

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'


# Товары
class Product(models.Model):
    title = models.CharField(max_length=250, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг товара')
    quantity = models.IntegerField(default=10, verbose_name='Количество товара')
    price = models.IntegerField(default=100, verbose_name='Цена товара')
    color_name = models.CharField(max_length=70, default='Белый', verbose_name='Название света')
    color_code = models.CharField(max_length=70, default='#ffffff', verbose_name='Код света')
    guarantee = models.IntegerField(default=0, verbose_name='Гарантия товара')
    discount = models.IntegerField(default=0, verbose_name='Скидка на товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    image = models.ImageField(upload_to='products/', verbose_name='Фото товара', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория', related_name='products')
    model = models.ForeignKey('ModelProduct', on_delete=models.CASCADE, verbose_name='Модель',
                              related_name='model_products')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('detail', kwargs={'slug': self.slug})

    def get_price(self):
        if self.discount:
            p = self.price - self.price * self.discount // 100
            return p
        else:
            return self.price

    def get_price_month(self):
        p = self.get_price() // 12
        return p

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


# Модели товаров
class ModelProduct(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название модели')
    slug = models.SlugField(unique=True, verbose_name='Слаг модели')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели товаров'


# Характеристики
class Characteristic(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название характеристики')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'


# Характеристики товаров
class ProductCharacteristic(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_characteristics',
                                verbose_name='Товар')
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE, verbose_name='Тип характеристики')
    value = models.CharField(max_length=150, verbose_name='Значение')

    def __str__(self):
        return f'{self.product.title} — {self.characteristic.name}: {self.value}'

    class Meta:
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товара'
        constraints = [models.UniqueConstraint(fields=('product', 'characteristic'),
                                               name='unique_characteristic_per_product')]


def user_photo_path(instance, filename):
    return f'users/{instance.user_id}/{filename}'


# Пользователи
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона')
    city = models.CharField(max_length=100, verbose_name='Город', null=True, blank=True)
    address = models.CharField(max_length=100, verbose_name='Адрес', null=True, blank=True)
    region = models.CharField(max_length=100, verbose_name='Регион', null=True, blank=True)
    photo = models.ImageField(upload_to=user_photo_path, null=True, blank=True, verbose_name='Фото профеля')

    def __str__(self):
        return f'Покупатель {self.user.username}'

    class Meta:
        verbose_name = 'Покупателя'
        verbose_name_plural = 'Покупатели'


# Избранное
class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f'Товар {self.product.title} пользователя {self.user.username}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


# Корзина
class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, verbose_name='Покупатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Корзина покупателя {self.customer.user.username} №: {self.pk}'

    class Meta:
        verbose_name = 'Корзину'
        verbose_name_plural = 'Корзины покупателей'

    @property
    def cart_total_price(self):
        products = self.productcart_set.all()
        price = sum([i.get_total_price for i in products])
        return price

    @property
    def cart_total_quantity(self):
        products = self.productcart_set.all()
        quantity = sum([i.quantity for i in products])
        return quantity


# Товары в корзине
class ProductCart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.IntegerField(default=0, verbose_name='В количестве')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name='Корзина')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    @property
    def get_total_price(self):
        return self.quantity * self.product.get_price()

    def __str__(self):
        return f'Товар {self.product.title} корзины №: {self.cart.pk} покупателя {self.cart.customer.user}'

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товар корзин'


# Доставка
class Delivery(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Покупатель')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.CharField(max_length=100, verbose_name='Почта')
    phone = models.CharField(max_length=30, verbose_name='Номер получателя')
    comment = models.CharField(max_length=250, verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оформления доставки')
    region = models.CharField(max_length=50, verbose_name='Регион')
    city = models.CharField(max_length=50, verbose_name='Город')
    address = models.CharField(max_length=100, verbose_name='Адресс')
    status = models.BooleanField(default=False, verbose_name='Статус доставки')

    def __str__(self):
        return f'Доставка для покупателя {self.customer.user.username}'

    class Meta:
        verbose_name = 'Доставку'
        verbose_name_plural = 'Доставки'


# Заказ
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Покупатель')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name='Корзина')
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, verbose_name='Доставка')
    price = models.IntegerField(default=0, verbose_name='Цена заказа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оплаты заказа')
    completed = models.BooleanField(default=0, verbose_name='Статус оплаты заказа')

    def __str__(self):
        return f'Заказа № {self.pk} покупателя {self.customer.user.username}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы покупателей'


# Товары заказа
class ProductOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ', related_name='products')
    name = models.CharField(max_length=300, verbose_name='Название товара')
    slug = models.CharField(max_length=300, verbose_name='Слаг товара')
    price = models.IntegerField(default=0, verbose_name='Цена товара')
    photo = models.ImageField(upload_to='products/', verbose_name='Фото товара')
    color_name = models.CharField(max_length=70, default='Белый', verbose_name='Название света')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    total_price = models.IntegerField(default=0, verbose_name='На сумму в кол-во')

    def __str__(self):
        return f'Товар {self.name} заказ № {self.order.pk}, покупателя {self.order.customer.user.username}'

    class Meta:
        verbose_name = 'Товар заказа'
        verbose_name_plural = 'Товары заказов'
