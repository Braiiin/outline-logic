from logic.v1.models import Document, db
from logic.v1.core.models import User

class Outline(Document):
    """outline model"""

    title = db.StringField(required=True)
    content = db.StringField(required=True)
    author = db.ReferenceField(User)
