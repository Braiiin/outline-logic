from logic.v1.models import Document, db
from logic.v1.core.models import User


def hashtag_or_hashtags(f):
    """
    Converts all hashtag strings and lists into single hashtags
    - custom decorator for the Hashtag class
    - first param for actual method must be hashtag
    - hashtags may or may not begin with the pound sign
    - return a list if received multiple hashtags, a single hashtag if only one
    """
    def helper(hashtag, *args, **kwargs):
        if isinstance(hashtag, str):
            if hashtag[0] == '#':
                return helper(hashtag[1:], *args, **kwargs)
            if ',' in hashtag:
                hashtag = {s.strip() for s in hashtag.split(',')}
        if isinstance(hashtag, (list, set)):
            rval = set()
            for tag in hashtag:
                tag = helper(tag, *args, **kwargs)
                if isinstance(tag, set):
                    {rval.add(tag) for tag in tag}
                else:
                    rval.add(tag)
            return rval
        else:
            rval = f(hashtag, *args, **kwargs)
            if not isinstance(rval, set):
                return {rval}
            else:
                return rval
    helper.__name__ = f.__name__
    return helper


class Hashtag(Document):
    """a hashtag"""

    categories = Document.choices('school', 'subject', 'topic')

    parent = db.StringField()
    name = db.StringField()
    category = db.StringField(choices=categories, default='topic')

    @staticmethod
    @hashtag_or_hashtags
    def add(hashtag):
        """ Adds a hashtag to database """
        return Hashtag(name=hashtag).get_or_create()


class Tag(Document):
    """a hashtag applied to an object"""

    hashtag = db.ReferenceField(Hashtag)
    oid = db.StringField()
    kind = db.StringField()  # name of the object's collection


class Outline(Document):
    """outline model"""

    title = db.StringField(required=True)
    content = db.StringField(required=True)
    author = db.ReferenceField(User)
    hashtags = db.ListField(db.ReferenceField(Hashtag))
