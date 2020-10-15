from django.conf.urls import url
from stringcase import spinalcase

from .apps import ApiConfig
from . import views
from . import utils


app_name = ApiConfig.name

def u(view):
    name = view.__name__
    return url(f'^{spinalcase(name)}$', view, name=name)

urlpatterns = [u(func) for func in utils.get_module_functions(views.__name__)]
