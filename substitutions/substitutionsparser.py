import requests
import xml.etree.ElementTree as ET
from substitutions import substitutions as sub
import datetime
import os


class SubstitutionsParser(object):
    HOURS = os.getenv("HOURS").split(",")

    WEEKDAYS = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"]

    METADATA_URL = os.getenv("METADATA_URL")

    SUBJECTS_METADATA = None

    def get_full_string(self, substitutions: list, date: datetime.date) -> str:
        canceled = self.get_canceled_string(substitutions)
        substitutionss = self.get_substitutions_string(substitutions)

        if not canceled and not substitutions:
            canceled = "\n⛔ BRAK ZASTĘPSTW\n"

        return """ℹ️ Zastępstwa na dzień {0} ({1})
{2}{3}
➡️ LINK
{4}""".format(date.strftime("%d.%m"), SubstitutionsParser.WEEKDAYS[date.weekday()], canceled, substitutionss, "{0}subst_students{1}.htm".format(sub.Substitutions.URL, date.strftime("%Y-%m-%d")))

    def get_substitutions_string(self, substitutions: list) -> str:
        substitutions = self.get_substitutions(substitutions)
        substitutions = self.substitutions_to_str_list(substitutions)
        return "\n🔄 ZASTĘPSTWA\n" + "\n".join(substitutions) + "\n" if len(substitutions) else ""

    def get_substitutions(self, substitutions: list) -> list:
        return [substitution for substitution in substitutions if substitution.substituting_teacher != "Odwołane"]

    def substitutions_to_str_list(self, substitutions: list) -> list:
        result = []
        for substitution in substitutions:
            subject1, subject2 = self.get_subjects(substitution)
            classroom1, classroom2 = self.get_classrooms(substitution)

            if classroom1 and classroom2:
                subject1 += " ({0})".format(classroom1)
                subject2 += " ({0})".format(classroom2)

            result.append("{0} – {1} -> {2}".format(
                SubstitutionsParser.HOURS[int(substitution.lesson)], subject1, subject2))
        result.sort(key=lambda x: int(x.split(":")[0]))
        return result

    def get_subjects(self, substitution: sub.Substitution) -> tuple:
        if "->" in substitution.subject:
            subjects = substitution.subject.split("->")
            subjects = self.replace_names(subjects)
            return subjects[0], subjects[1]
        else:
            return substitution.teacher, substitution.substituting_teacher if not "/" in substitution.substituting_teacher else substitution.substituting_teacher.split("/")[0].strip()

    def get_classrooms(self, substition: sub.Substitution) -> tuple:
        if "/" in substition.substituting_teacher:
            temp = substition.substituting_teacher.split("/")
            classroom1, classroom2 = temp[1].split(" -> ")
            classroom1 = classroom1.strip()
            return classroom1, classroom2
        return "", ""

    def get_canceled_string(self, substitutions: list) -> str:
        canceled = self.get_canceled(substitutions)
        canceled = self.canceled_to_str_list(canceled)
        return "\n❌ ODWOŁANE\n" + "\n".join(canceled) + "\n" if len(canceled) else ""

    def get_canceled(self, substitutions: list) -> list:
        return [substitution for substitution in substitutions if substitution.substituting_teacher == "Odwołane"]

    def canceled_to_str_list(self, canceled: list) -> list:
        canceled = [SubstitutionsParser.HOURS[int(
            can.lesson)] + " – " + can.subject for can in canceled]
        canceled = self.replace_names(canceled)
        canceled.sort(key=lambda x: int(x.split(":")[0]))
        return canceled

    def replace_names(self, substitutions: list) -> list:
        for i in range(len(substitutions)):
            for short, name in SubstitutionsParser.SUBJECTS_METADATA.items():
                if short == "WF chł": name = "WF chłopcy"
                elif short == "WF dz": name = "WF dziewczyny"
                
                substitutions[i] = substitutions[i].replace(short, name)
        return substitutions

    def update_metadata(self) -> None:
        SubstitutionsParser.SUBJECTS_METADATA = self.get_subjects_metadata()

    def get_subjects_metadata(self) -> dict:
        myroot = ET.fromstring(self.download_metadata())
        subjects = myroot.find("subjects")
        subjects_metadata = {}

        for subject in subjects.findall("subject"):
            subjects_metadata[subject.get("short")] = subject.get("name")

        return subjects_metadata

    def download_metadata(self) -> str:
        xml = requests.get(SubstitutionsParser.METADATA_URL).text
        return xml