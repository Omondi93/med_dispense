from app import db
from datetime import datetime

class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    manufacturer_id = db.Column(
        db.Integer,
        db.ForeignKey("manufacturers.id"),
        nullable=False
    )

    batches = db.relationship("Batch", backref="medicine", lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)