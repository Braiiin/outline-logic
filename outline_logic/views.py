from logic.v1.views import register_api
from .api import OutlineAPI


register_api(OutlineAPI, 'outline')
