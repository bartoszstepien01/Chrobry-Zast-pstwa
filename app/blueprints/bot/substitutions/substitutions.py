import requests
import datetime
from bs4 import BeautifulSoup

class Substitution(object):
    def __init__(self, array: []) -> None:
        self.lesson = array[1]
        self.teacher = array[2]
        self.subject = array[3]
        self.substituting_teacher = array[4]
    
    def __eq__(self, other):
        if not isinstance(other, Substitution): return False
        return self.lesson == other.lesson and self.teacher == other.teacher and self.subject == other.subject and self.substituting_teacher == other.substituting_teacher


class Substitutions(object):
    URL = ""

    def get_substitutions_for_grade(self, date: datetime.date, grade: str, substitutions: dict = None) -> list:
        if not substitutions: substitutions = self.get_substitutions(date)
        substitutions2 = None
        if substitutions:
            substitutions2 = []
            for grade2 in substitutions:
                if grade in grade2:
                    for substitution in substitutions[grade2]:
                        substitutions2.append(substitution)
        return substitutions2

    def get_substitutions(self, date: datetime.date) -> dict:
        page = self.download_substitutions(date)
        return self.parse_page(page.content) if page.ok else None

    def download_substitutions(self, date: datetime.date) -> requests.Response:
        page = requests.get("{0}subst_students{1}.htm".format(
            Substitutions.URL, date.strftime("%Y-%m-%d")))
        return page

    def parse_page(self, page: bytes) -> dict:
        soup = BeautifulSoup(page, features="html.parser")
        rows = soup.find_all("tr")

        substitutions = {}
        current_grade = ""
        for row in rows:
            cols = self.parse_row(row)
            if not cols:
                continue
            if len(cols) <= 5:
                cols.insert(0, current_grade)
            else:
                current_grade = cols[0]
            if not current_grade in substitutions:
                substitutions[current_grade] = []
            substitutions[current_grade].append(Substitution(cols))

        return substitutions

    def parse_row(self, row) -> list:
        cols = row.find_all("td")
        if not cols:
            return None
        cols = [col.text.strip() for col in cols]
        cols = cols[:-1]
        if cols[-1] == "" or cols[-2] == "":
            cols[-2] = "Odwołane"
        cols = [col for col in cols if col]
        if "->" in cols[-1]:
            cols[-2] += " / " + cols[-1]
        return cols