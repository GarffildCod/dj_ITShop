from django.shortcuts import render

from shop.scraping import scraping, ScrapingError

from django.views.generic import ListView
from django.views.generic import DetailView

from shop.models import Product


def fill_database(request):
    if request.method == 'POST' and request.user.is_staff:
        try:
            scraping()
        except ScrapingError as err:
            print(str(err))
            return render(request, 'shop/fill_database.html', {'massage': err})

    return render(request, 'shop/fill_database.html', {'massage': None})


def cart_page(request):
    return render(request, 'shop/cart_page.html')



class ProductsListView(ListView):
    model = Product
    template_name = 'shop/category.html'

class ProductsDetailView(DetailView):
    model = Product
    template_name = 'shop/shop-details.html'


