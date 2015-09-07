from logic.v1.api import BaseAPI, need, hook
from logic.v1.args import KeyArg, Arg
from logic.v1.core.models import User
from . import models


class OutlineAPI(BaseAPI):
    """API for Outlines"""

    model = models.Outline

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
        'delete': {
            'args': model.fields_to_args(override={'required': False})
        }
    }

    endpoints = {
        'fetch': {
            'args': model.fields_to_args(override={'required': False})
        }
    }

    def can(self, obj, user, permission):
        """Returns a boolean allowing or denying API access"""
        if permission in ['post', 'get', 'put', 'fetch', 'delete']:
            return True
        return False
