from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instagram_handle = db.Column(db.String(80), unique=True, nullable=False)
    entered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    c1 = db.Column(db.Boolean, default=False, nullable=False)
    c2 = db.Column(db.Boolean, default=False, nullable=False)
    c3 = db.Column(db.Boolean, default=False, nullable=False)
    c4 = db.Column(db.Boolean, default=False, nullable=False)
    is_selected = db.Column(db.Boolean, default=False, nullable=False)
    #selection_time = db.Column(db.DateTime, nullable=True)

    @property
    def is_eligible(self):
        return self.c1 and self.c2 and self.c3 and self.c4
