from django.db import models

# Create your models here.
from django.utils import timezone
from django.contrib.auth.models import User
from slugify import slugify
from mptt.models import MPTTModel, TreeForeignKey

class Shop(models.Model):
    owner=models.OneToOneField(User,related_name='shop',on_delete=models.CASCADE,verbose_name='Владелец')#
    name=models.CharField(max_length=100,verbose_name='Название')
    slug=models.SlugField(max_length=250,unique_for_date='created')
    phone=models.CharField(max_length=30,verbose_name='Номер телефона')
    address=models.CharField(max_length=30,verbose_name='Адресс')
    logo=models.ImageField(upload_to='shop_logo/',blank=False,verbose_name='Логотип')
    created=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    def save(self,  *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Shop, self).save(*args, **kwargs)


class Category(MPTTModel):
    name = models.CharField(max_length=64, unique=True)
    parent = TreeForeignKey('self', null=True,db_index=True,
                            blank=True, related_name='children',
                            on_delete=models.CASCADE)
    slug=models.SlugField(max_length=250,db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def save(self,  *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Category, self).save(*args, **kwargs)


class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин')
    product_name = models.CharField(max_length=30, verbose_name='Название товара')
    category = models.ManyToManyField(Category, verbose_name='Категория', blank=True, default=None, null=True)
    slug = models.SlugField(max_length=250, unique_for_date='created', blank=True)
    short_description = models.CharField(max_length=100, verbose_name='Короткое описание')
    description = models.TextField(max_length=1000,verbose_name='Полное описание')
    image = models.ImageField(upload_to='product_images/', blank=False, verbose_name='Изображение')
    price = models.PositiveIntegerField(default=0,verbose_name='Цена грн.')
    created = models.DateTimeField(default=timezone.now)
    availability=models.BooleanField(default=True,verbose_name='Наличие')


    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        return super(Product, self).save(*args, **kwargs)


def save_images(instance,filename):
    shop_id=instance.product.shop.id
    id=instance.product.id
    return 'gallery_images/{}/{}/{}'.format(shop_id,id,filename)


class ProductImages(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE,default=None)
    product_image = models.ImageField(upload_to=save_images, blank=True, verbose_name='Галерея изображений')


class Order(models.Model):
    first_name=models.CharField(max_length=50,verbose_name='Имя')
    last_name=models.CharField(max_length=50,verbose_name='Фамилия')
    phone=models.CharField(default=0,max_length=30,verbose_name='Номер телефона',blank=False)
    email=models.EmailField()
    city = models.CharField(max_length=100,verbose_name='Город')
    address=models.CharField(max_length=250,verbose_name='Адрес')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status=models.BooleanField(default=False,verbose_name='Статус')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items',verbose_name='Заказ')
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='order_items',verbose_name='Товар')
    price = models.DecimalField(max_digits=10, decimal_places=2,verbose_name='Цена')
    quantity = models.PositiveIntegerField(default=1,verbose_name='Количество')
    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity

