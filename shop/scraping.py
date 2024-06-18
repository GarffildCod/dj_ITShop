
from decimal import Decimal
from itertools import product
import re
import requests
from bs4 import BeautifulSoup

from shop.models import Product, Payment, Order, OrderItem

URL_SCRAPING_DOMAIN = 'https://www.madwave.ru/images/medium/pic_1/10021668.jpg?1527514975'
URL_SCRAPING = 'https://www.madwave.ru/catalog/obuv-0'


class ScrapingError(Exception):
    pass


class ScrapingTimeoutError(ScrapingError):
    pass


class ScrapingHTTPError(ScrapingError):
    pass


class ScrapingOtherError(ScrapingError):
    pass


def scraping():
    try:
        resp = requests.get(URL_SCRAPING, timeout=10.0)
    except requests.exceptions.Timeout:
        raise ScrapingTimeoutError(" timed out")
    except Exception as e:
        raise ScrapingOtherError(f'{e}')

    if resp.status_code != 200:
        raise ScrapingHTTPError(f"HTTP {resp.status_code}: {resp.text}")


    data_list = []
    html = resp.text


    soup = BeautifulSoup(html, 'html.parser')
    blocks = soup.select('.product')

    code1= 0
    
    for block in blocks:
        data = {}
        code1 +=1
        data['code'] = code1

        name = block.select_one('.title').get_text().strip()
        data['name'] = name

        image_url = URL_SCRAPING_DOMAIN + block.select_one('img')['src']
        data['image_url'] = image_url

        price_raw = block.select_one('.old-price').text
        price = re.sub(r'\D', '', price_raw)
        data['price'] = price   
        
        data_list.append(data)
        print(data)

    
    for item in data_list:
        # if not Product.objects.filter(code=item['code']).exists():
        Product.objects.create(
                name=item['name'],
                code=item['code'],
                price=item['price'],
                image_url=item['image_url'],
            )
    return data_list


if __name__ == '__main__':
    scraping()

 