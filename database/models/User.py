from .. import db

class User(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    grade = db.Column(db.String(5))