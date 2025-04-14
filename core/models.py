from decimal import Decimal
from math import ceil

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import EmailField, CharField, OneToOneField, Avg

from core.managers import CustomUserManager


# Create your models here.

class User(AbstractUser):
    username = None
    email = EmailField(unique=True)
    name = CharField(max_length=255)
    billing_address = OneToOneField('OrderBilling', on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()


class Subscription(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class PostCategory(models.Model):
    class Meta:
        verbose_name_plural = 'Post Categories'

    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class ProductCategory(models.Model):
    class Meta:
        verbose_name_plural = 'Product Categories'
    image = models.ImageField(upload_to='product_category', null=True, blank=True)
    name = models.CharField(max_length=255)

class Product(models.Model):
    featured_image = models.ImageField(upload_to='featured_image')
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    category_id = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField()
    additional_information = models.TextField(null=True, blank=True)
    original_price = models.DecimalField(decimal_places=2, max_digits=10)
    discounted_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    is_featured = models.BooleanField(default=False)

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return range(1, int(avg or 0) + 1)

    @property
    def discount_percentage(self):
        if self.discounted_price:
            return ceil(((self.discounted_price - self.original_price) * 100) / self.original_price)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')

    def __str__(self):
        return f"{self.product_id} - {self.product_id.featured_image.name}"


class CustomerReview(models.Model):
    text = models.CharField(max_length=255)
    rating = models.IntegerField()
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.product_id} - {self.rating}"

class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class ProductTags(models.Model):
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='product_tags')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_tags')

    def __str__(self):
        return f"{self.product_id} - {self.tag_id.name}"

class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class OrderBilling(models.Model):
    class PaymentType(models.TextChoices):
        CREDIT_CARD = 'credit_card', 'Credit Card'
        DEBIT_CARD = 'debit_card', 'Debit Card'
        PAYPAL = 'paypal', 'PayPal'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        REJECTED = 'rejected', 'Rejected'

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    address_2 = models.CharField(max_length=255)
    country_id = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_countries')
    state = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    is_shipping_address_same = models.BooleanField(default=False)
    payment_type = models.CharField(choices=PaymentType, max_length=30)
    payment_status = models.CharField(choices=PaymentStatus, max_length=30)
    saveAsDefaultAdress = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=255)

class Promocode(models.Model):
    code = models.CharField(max_length=255)
    discount_percent = models.IntegerField()

    def __str__(self):
        return self.code

class Order(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='orders_user')
    order_billing = models.ForeignKey(OrderBilling, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_billing')
    promocode = models.ForeignKey(Promocode, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_promocode')

    @property
    def total_price(self):
        total = 0
        for item in self.order_items.all():
            if item.product.discounted_price:
                total += item.product.discounted_price * item.quantity
            else:
                total += item.product.original_price * item.quantity
        return total

    @property
    def coupon_discount(self):
        if self.promocode:
            discount = (self.total_price * Decimal(self.coupon.percent_off)) / Decimal(100)
            return discount
        return Decimal(0)

    def __str__(self):
        return f"{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_product_items')
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.id} - {self.product.name}"

class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    featured_image = models.ImageField(upload_to='post_images', null=True, blank=True)

    def __str__(self):
        return self.title

class Favourite(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favourites')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourite_user')

    def __str__(self):
        return self.product.name

class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title

class PostTags(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='post_tags')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_tags')

    def __str__(self):
        return f"{self.post.title} - {self.tag.name}"