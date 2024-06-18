from decimal import Decimal
import zoneinfo
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User
from shop.models import Product, Payment, Order, OrderItem


class TestDataBase(TestCase):
    fixtures = [
        "shop/fixtures/mydata.json"
    ]

    def setUp(self):
        self.user = User.objects.get(username='root')
        self.p = Product.objects.all().first()



    def test_user_exists(self):
        users = User.objects.all()
        users_number = users.count()
        user = users.first()
        self.assertEqual(users_number, 1)
        self.assertEqual(user.username, 'root')
        self.assertTrue(user.is_superuser)

    def test_user_check_password(self):
        self.assertTrue(self.user.check_password('123'))

    # def test_all_date(self):
    #     self.assertGreater(Product.objects.all().count(), 0)
    #     self.assertGreater(Payment.objects.all().count(), 0)
    #     self.assertGreater(Order.objects.all().count(), 0)
    #     self.assertGreater(OrderItem.objects.all().count(), 0)



# Первый тест
    def find_cart_number(self):
        cart_number = Order.objects.filter(user=self.user, 
                                           status=Order.STATUS_CART
                                           ).count()
        return cart_number
    
    def test_function_get_cart(self):
        # 1 not carts
        self.assertEqual(self.find_cart_number(), 0)
        # 2 Create cart 
        Order.get_cart(self.user)
        self.assertEqual(self.find_cart_number(), 1)
        # 3 Get created cart 
        Order.get_cart(self.user)
        self.assertEqual(self.find_cart_number(), 1)


# Второй тест
    def test_cart_older_7_days(self):
        cart = Order.get_cart(self.user)
        cart.creation_time = timezone.datetime(2000, 1, 1, tzinfo=zoneinfo.ZoneInfo('UTC'))
        cart.save()
        cart = Order.get_cart(self.user)
        self.assertEqual((timezone.now() - cart.creation_time).days, 0)


# Третий тест
    def test_recalculate_order_amount_after_changing_orderitem(self):
        # 1
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(0))
        # 2
        i = OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=2)
        i = OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=3)
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(10))
        # 3
        i.delete()
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(4))

# Четвертый тест
    def test_cart_status_changing_after_applying_make_order(self):
        cart = Order.get_cart(self.user)
        cart.make_order()
        self.assertEqual(cart.status, Order.STATUS_CART)

        i = OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=2)
        cart.make_order()
        self.assertEqual(cart.status, Order.STATUS_WAITING_FOR_PAYMONT)

# Пятый тест
    # def test_method_get_amount_of_unpaind_orders(self):
    #     #1
    #     amount = Order.get_amount_of_unpaid_orders(self.user)
    #     self.assertEqual(amount, Decimal(0))

    #     #2
    #     cart = Order.get_cart(self.user)
    #     OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=2)
    #     amount = Order.get_amount_of_unpaid_orders(self.user)
    #     self.assertEqual(amount, Decimal(0))

    #     #3
    #     cart.make_order()
    #     amount = Order.get_amount_of_unpaid_orders(self.user)
    #     self.assertEqual(amount, Decimal(0))

    #     #4
    #     cart.status = Order.STATUS_PAID
    #     cart.save()
    #     amount = Order.get_amount_of_unpaid_orders(self.user)
    #     self.assertEqual(amount, Decimal(0))

    #     #5
    #     Order.objects.all().delete()
    #     amount = Order.get_amount_of_unpaid_orders(self.user)
    #     self.assertEqual(amount, Decimal(0))


# шестой тест
    # def test_method_test_balance(self):
    #     #1
    #     amount = Payment.get_balance(self.user)
    #     self.assertEqual(amount, Decimal(13000))
    #     #2
    #     Payment.objects.create(user = self.user, amount=100)
    #     amount = Payment.get_balance(self.user)
    #     self.assertEqual(amount, Decimal(13100))
    #     #3
    #     Payment.objects.create(user = self.user, amount=-50)
    #     amount = Payment.get_balance(self.user)
    #     self.assertEqual(amount, Decimal(13050))
    #     #4
    #     Payment.objects.all().delete()
    #     amount = Payment.get_balance(self.user)
    #     self.assertEqual(amount, Decimal())



#  Седьмой тест

    def test_auto_paymant_apply_make_order_true(self):
        Order.objects.all().delete()
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=2)
        self.assertEqual(Payment.get_balance(self.user), Decimal(13000))
        cart.make_order()
        self.assertEqual(Payment.get_balance(self.user), Decimal(12996))

    def test_auto_paymant_apply_make_order_false(self):
        Order.objects.all().delete()
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=50000)
        cart.make_order()
        self.assertEqual(Payment.get_balance(self.user), Decimal(13000))


#  Восьмой тест
# 1 варинт
    def test_auto_payment_after_add_required_payment(self):
        Payment.objects.create(user = self.user, amount=556)
        self.assertEqual(Payment.get_balance(self.user), Decimal(0))
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(0))

# 2 варинт
    def test_auto_payment_for_earlier_order(self):
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=50000)
        Payment.objects.create(user = self.user, amount=1000)
        self.assertEqual(Payment.get_balance(self.user), Decimal(444))
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(1000))

# 3 варинт
    def test_auto_payment_for_all_order(self):
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=50000)
        Payment.objects.create(user = self.user, amount=10000)
        self.assertEqual(Payment.get_balance(self.user), Decimal(9444))
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(0))



        