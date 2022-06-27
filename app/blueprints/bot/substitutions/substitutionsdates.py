import requests
import datetime
from bs4 import BeautifulSoup
import os

class SubstitutionsDates(object):
    DATES_URL = os.getenv("DATES_URL")

    def download_dates(self):
        return self.parse_page(self.download_page())

    def download_page(self):
        page = requests.get(SubstitutionsDates.DATES_URL)
        return page.content
    
    def parse_page(self, page):
        soup = BeautifulSoup(page, features="html.parser")
        rows = soup.find_all("tr")
        dates = []
        for row in rows:
            for date in self.parse_row(row):
                dates.append(self.parse_date(date))
        return dates
    
    def parse_row(self, row) -> list:
        cols = row.find_all("td")
        if not cols:
            return []
        cols = [col.text.strip() for col in cols]
        cols = [col for col in cols if col]
        return cols
    
    def parse_date(self, date):
        return datetime.datetime.strptime(date, "%d.%m.%Y").date()