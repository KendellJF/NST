from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(120), nullable=False)
    lname = db.Column(db.String(120), nullable=False)
    instagram_handle = db.Column(db.String(80), unique=True, nullable=True)
    entered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_selected = db.Column(db.Boolean, default=False, nullable=False)
    #selection_time = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Entry {self.instagram_handle}>'