from datetime import date
from pathlib import Path
import aiohttp
import asyncio
import click
import csv
import json
import logging
import lxml.html
import re


async def family_sponsorship(http):
    async with http.get('https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/family-sponsorship/sponsor-parents-grandparents/tell-us-you-want-sponsor-parent-grandparent.html') as resp:
        tree = lxml.html.fromstring(await resp.read())
    date_modified, = tree.cssselect('time[property="dateModified"]')
    date_modified = date_modified.text_content().strip()
    if date_modified != '2020-03-27':
        logging.info('Date modified: %s', date_modified)


async def run(directory):
    async with aiohttp.ClientSession(raise_for_status=True) as http:
        tasks = [
            family_sponsorship(http),
        ]
        await asyncio.gather(*tasks)


@click.command()
@click.argument('data_directory', type=click.Path(exists=True, file_okay=False, writable=True))
def main(data_directory):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s")
    data_directory = Path(data_directory)
    asyncio.get_event_loop().run_until_complete(run(data_directory))


if __name__ == '__main__':
    main()
