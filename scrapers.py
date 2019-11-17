from datetime import date
from pathlib import Path
import aiohttp
import asyncio
import click
import csv
import json
import lxml.html
import re


async def vinoperfect(http, directory):
    async with http.get('https://ca-en.caudalie.com/collections/vinoperfect/vinoperfect-natural-brightening-stars-1.html') as resp:
        tree = lxml.html.fromstring(await resp.read())
    span, = tree.cssselect('#product-price-1263')
    price = float(span.text_content().strip().replace('$', ''))
    with (directory / 'vinoperfect.csv').open('a') as f:
        csv.writer(f).writerow((date.today(), price))


async def step1(http, directory):
    async with http.get('https://www.makeupforever.com/ca/en-ca/make-up/face/primer/step1') as resp:
        text = await resp.text()
    data = json.loads(re.search(r'jQuery\.extend\(Drupal.settings, (.*)\);', text).group(1))
    price_html = data['mufe_theme']['product_list']['product_71508']['sku_list']['3']['items']['30-127']['price']
    price = float(lxml.html.fromstring(price_html).text_content().replace('CAD', '').strip())
    with (directory / 'step1.csv').open('a') as f:
        csv.writer(f).writerow((date.today(), price))


async def run(directory):
    async with aiohttp.ClientSession(raise_for_status=True) as http:
        tasks = [
            vinoperfect(http, directory),
            step1(http, directory),
        ]
        await asyncio.gather(*tasks)


@click.command()
@click.argument('data_directory', type=click.Path(exists=True, file_okay=False, writable=True))
def main(data_directory):
    data_directory = Path(data_directory)
    asyncio.get_event_loop().run_until_complete(run(data_directory))


if __name__ == '__main__':
    main()
