from flask import Flask, Response
from substitutions.substitutions import Substitutions
from substitutions.substitutionsdates import SubstitutionsDates
from substitutions.substitutionsparser import SubstitutionsParser

app = Flask(__name__)

@app.route("/<grade>")
def catch_all(grade):
    substitutions = Substitutions()
    dates = SubstitutionsDates()
    parser = SubstitutionsParser()

    parser.load_metadata()

    date = dates.download_dates()[0]
    substitution = substitutions.get_substitutions_for_grade(date, grade)
    
    return parser.get_full_string(substitution, date)