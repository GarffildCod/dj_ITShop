from django.contrib.auth.models import User
from django.db import models ,transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='product_name')
    code = models.CharField(max_length=255, verbose_name='product_code')
    price = models.DecimalField(max_digits=20, decimal_places=2)
    unit = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['pk']

    def __str__(self) -> str:
        return f'{self.name} - {self.price}'

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)


    class Meta:
        ordering = ['id']

    def __str__(self) -> str:
        return f'{self.user} - {self.amount}'
    
    @staticmethod
    def get_balance(user: User):
        amount = Payment.objects.filter(user=user).aaggregate(Sum('amount'))['amount__sum']
        return amount or Decimal(0)

    


class Order(models.Model):
    STATUS_CART = '1_cart'
    STATUS_WAITING_FOR_PAYMONT = '2_waiting_for_paymont'
    STATUS_PAID = '3_paid'
    STATUS_CHOICES = {
        (STATUS_CART, 'cart'),
        (STATUS_WAITING_FOR_PAYMONT, 'waiting_for_paymont'),
        (STATUS_PAID, 'paid')
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # items = models.ManyToManyField(OrderItem, related_name='orders')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_CART)
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)


    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.user} - {self.amount} - {self.status}'
    

    @staticmethod
    def get_cart(user: User):
        cart = Order.objects.filter(user=user,
                                    status=Order.STATUS_CART
                                    ).first()
        if cart and (timezone.now() - cart.creation_time).days > 7:
            cart.delete()
            cart = None

        if not cart:
            cart = Order.objects.create(user=user,
                                    status=Order.STATUS_CART,
                                    amount=0)
        return cart
    

    def get_amount(self):
        amount = Decimal(0)
        for item in self.orderitem_set.all():
            amount += item.amount
        return amount
    
    def make_order(self):
        items = self.orderitem_set.all()
        if items and self.status == Order.STATUS_CART:
            self.status = Order.STATUS_WAITING_FOR_PAYMONT
            self.save()
            auto_payment_unpaid_orders(self.user)


    @staticmethod
    def get_amount_of_unpaid_orders(user: User):
        amount = Order.objects.filter(user=user,
                                      status = Order.STATUS_WAITING_FOR_PAYMONT
                                      ).aaggregate(Sum('amount'))['amount__sum']
        return amount or Decimal(0)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    discount = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        ordering = ['pk']

    def __str__(self) -> str:
        return f'{self.product} - {self.price}'
    
    @property
    def amount(self):
        return self.quantity * (self.price - self.discount)
    

@transaction.atomic()
def auto_payment_unpaid_orders(user: User):
    unpaid_orders = Order.objects.filter(user=user,
                                         status=Order.STATUS_WAITING_FOR_PAYMONT)
    for order in unpaid_orders:
        if Payment.get_balance(user) < order.amount:
            break
        order.payment = Payment.objects.all().last()
        order.status = Order.STATUS_PAID
        order.save()
        Payment.objects.create(user=user,
                               amount=order.amount)

@receiver(post_save, sender=OrderItem)
def recalculate_order_amount_after_save(sender, instance, **kwargs):
    order = instance.order
    order.amount = order.get_amount()
    order.save()

@receiver(post_delete, sender=OrderItem)
def recalculate_order_amount_after_delete(sender, instance, **kwargs):
    order = instance.order
    order.amount = order.get_amount()
    order.save()


@receiver(post_save, sender=Payment)
def auto_payment(sender, instance, **kwargs):
    user = instance.user
    auto_payment_unpaid_orders(user)