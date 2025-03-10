from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Webuser(db.Model):
    __tablename__ = 'Webuser'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(64)) 
    userid = db.Column(db.String(32), unique=True, nullable=False)
    username = db.Column(db.String(8), nullable=False)
