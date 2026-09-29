import os
import django
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from products.models import Product,Category
from order.models import Order,OrderItem
cat=Category.objects.all()[1]
print(cat.product_set.all())
# =========================
# 1. BASIC QUERIES
# =========================

#products = Product.objects.all()

#print(products)

products = Product.objects.annotate(
total_sales=Sum("orderitem__price")
).values()
print(products)
#ord=Order.objects.select_related("user").distinct().filter(total_amount__gte=100000)
#print([o.user.email for o in ord],ord.count())
ord_itm= OrderItem.objects.select_related("order__user","product").filter(product__name__startswith="ip",order__user__email="ram123@gmail.com").order_by("-price")
print(ord_itm.aggregate(total_price=Sum("price")),ord_itm.count())

print([(oi.product.name,oi.order.user.email)  for oi in ord_itm])
# =========================
# 2. FILTER
# =========================

#products = Product.objects.filter(price__gt=1000).prefetch_related("category")

#for product in products:
#    print(product.name, product.price,product.category)


# =========================
# 3. ORDERING
# =========================

#products = Product.objects.order_by("-price")

#for product in products:
#    print(product.name, product.price)


# =========================
# 4. AGGREGATION
# =========================

from django.db.models import Avg

average_price = Product.objects.aggregate(
    Avg("price")
)

print(average_price)