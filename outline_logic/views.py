from logic.v1.views import register_api
from .api import OutlineAPI, HashtagAPI, TagAPI


register_api(OutlineAPI, 'outline')
register_api(HashtagAPI, 'hashtag')
register_api(TagAPI, 'tag')
