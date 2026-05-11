from app import db
from datetime import datetime
from app.utils.security import hash_password, verify_password


class Manufacturer(db.Model):
    __tablename__ = "manufacturers"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # -------------------------
    # 🔐 AUTH METHODS
    # -------------------------
    def set_password(self, password):
        self.password_hash = hash_password(password)

    def check_password(self, password):
        return verify_password(password, self.password_hash)

    # -------------------------
    # 🔗 RELATIONSHIPS
    # -------------------------
    medicines = db.relationship(
        "Medicine",
        backref="manufacturer",
        lazy=True,
        cascade="all, delete-orphan"
    )

    batches = db.relationship(
        "Batch",
        backref="manufacturer",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # -------------------------
    # 🧾 DEBUG REPRESENTATION
    # -------------------------
    def __repr__(self):
        return f"<Manufacturer id={self.id} name={self.name}>"