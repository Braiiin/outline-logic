from logic.v1.api import BaseAPI, need, hook
from logic.v1.args import KeyArg, Arg
from logic.v1.core.models import User
from .models import Hashtag, Tag
from mongoengine import Q
from . import models
import json


def process_hashtags(hashtags):
    """takes a string of hashtags and returns a list of Hashtag objects
    accepts comma-delimited lists with strings that can include or exclude
    pound signs"""
    return Hashtag.add(hashtags)


def sync_tags(tags, hashtags):
    """Delete extra tags not in the list of hashtags"""
    if len(tags) != len(hashtags):
        for tag in tags:
            if tag.hashtag not in hashtags:
                tag.delete()


class OutlineAPI(BaseAPI):
    """API for Outlines"""

    model = models.Outline

    methods = {
        'get': {
            'args': model.fields_to_args(override={'required': False},
                hashtags=Arg(list, use=process_hashtags))
        },
        'post': {
            'args': model.fields_to_args(
                hashtags=Arg(list, use=process_hashtags))
        },
        'put': {
            'args': model.fields_to_args(
                hashtags=Arg(list, use=process_hashtags))
        },
        'delete': {},
    }

    endpoints = {
        'fetch': {
            'args': model.fields_to_args(override={'required': False},
                hashtags=Arg(list, use=process_hashtags))
        },
        'search': {
            'args': {
                'query': Arg(str)
            }
        }
    }

    def post_get(self, obj, data, rval):
        """Convert hashtags into string list of hashtags"""
        hashtags = [h.name for h in rval.hashtags]
        data = json.loads(rval.load(hashtags=None).to_json())
        data['hashtags'] = hashtags
        return data

    def post_put(self, obj, data, rval):
        """Synchronize tags with hashtags"""
        tags = Tag(kind='Outline', oid=str(rval.id)).fetch()
        sync_tags(tags, rval.hashtags)
        return rval

    def post_post(self, obj, data, rval):
        """Saves all Hashtags in Tags many-to-many table"""
        obj = rval
        for hashtag in data['hashtags']:
            Tag(
                hashtag=hashtag,
                oid=str(obj.id),
                kind=obj.__class__.__name__
            ).save()
        return rval

    def fetch(self, obj, data):
        data = self.model(**data).to_dict()
        if not data['hashtags']:
            data.pop('hashtags')
        return self.model.objects(**data).all()

    # TODO: cleanup
    def search(self, obj, data):
        """performs search functionality"""
        queries = data['query'].split(' ')
        hashtags, titles = [], []
        for query in queries:
            if not query:
                continue
            if query[0] == '#':
                hashtags.append(str(Hashtag(name=query[1:]).get_or_create().id))
            else:
                titles.append(query)
        query = Q()
        for hashtag in hashtags:
            query = query & Q(hashtags=hashtag)
        for title in titles:
            query = query \
            & (Q(title__icontains=title) \
            | Q(content__icontains=title))
        outlines, nval = self.model.objects(query).all(), []
        for outline in outlines:
            hashtags = [h.get().name for h in outline.hashtags]
            data = json.loads(outline.load(hashtags=None).to_json())
            data['hashtags'] = hashtags
            nval.append(data)
        return nval

    def can(self, obj, user, permission):
        """Returns a boolean allowing or denying API access"""
        if permission in ['fetch', 'get']:
            return True
        if user.status != 'active':
            return False
        if permission in ['post', 'put', 'delete']:
            return True
        return False


class HashtagAPI(BaseAPI):
    """API for hashtags"""

    model = Hashtag

    methods = {
        'get': {
            'args': model.fields_to_args(override={'required': False})
        },
        'post': {
            'args': model.fields_to_args()
        },
        'put': {
            'args': model.fields_to_args()
        },
        'delete': {}
    }

    endpoints = {
        'fetch': {}
    }

    def can(self, obj, user, need):
        """Required permissions implementation"""
        if need in ['fetch', 'get']:
            return True
        if user.status != 'active':
            return False
        if need in ['post']:
            return True
        if need == 'put':
            return user.id == obj.id
        return False

    def fetch(self, _, data):
        return self.model(**data).fetch(order_by='name')


class TagAPI(BaseAPI):
    """API for relationships between hashtags and objects"""

    model = Tag

    methods = {
        'get': {
            'args': model.fields_to_args(override={'required': False})
        },
        'post': {
            'args': model.fields_to_args()
        },
        'put': {
            'args': model.fields_to_args()
        },
        'delete': {}
    }

    endpoints = {
        'fetch': {
            'args': model.fields_to_args(
                override={'required': False},
                exclude=['created_at', 'id', 'updated_at'])
        },
    }

    def can(self, obj, user, need):
        """Required permissions implementation"""
        if need in ['fetch', 'get']:
            return True
        if user.status != 'active':
            return False
        if need in ['post', 'delete', 'put']:
            return True
        return False

    def post_fetch(self, obj, data, rval):
        """Converts all tag oids into objects"""
        tags = []
        objects = list(rval.distinct('oid'))
        for tag in rval:
            if tag.oid in objects:
                obj = DBRef(tag.kind, tag.oid).get()
                data = json.loads(tag.to_json())
                data['object'] = obj
                tags.append(data)
                objects.remove(tag.oid)
        return tags
