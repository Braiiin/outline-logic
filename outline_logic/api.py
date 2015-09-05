from logic.v1.api import BaseAPI, need, hook
from logic.v1.args import KeyArg, Arg
from logic.v1.core.models import User
from . import models


class OutlineAPI(BaseAPI):
	"""API for Outlines"""

	model = models.Outline

	methods = {
		'get': model.fields_to_args(override={'required': False}),
		'post': model.fields_to_args(),
		'put': model.fields_to_args(),
		'delete': model.fields_to_args()
	}

	endpoints = {
		'fetch': model.fields_to_args(override={'required': False})
	}

	def can(self, obj, user, permission):
		"""Returns a boolean allowing or denying API access"""
		if permission in ['post', 'get', 'put', 'fetch']:
			return True
		return False
