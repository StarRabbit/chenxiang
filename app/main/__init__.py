from flask import Blueprint

main = Blueprint('main',__name__)

from . import views
from ..models import BASEPERMISSION,SENIORPERMISSION

# 这个地方找的我好苦！
# 整个app的上下文除了一定要注意不要缺漏
# 这东西叫上下午处理器，经它处理后的变量可以全局访问，在这里可以使模板直接访问到返回的参数。
@main.app_context_processor
def inject_permissions():
    return dict(BASEPERMISSION=BASEPERMISSION,SENIORPERMISSION=SENIORPERMISSION)