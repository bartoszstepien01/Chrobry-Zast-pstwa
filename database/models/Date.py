from .. import db

class Date(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    current_substitutions = db.Column(db.JSON)