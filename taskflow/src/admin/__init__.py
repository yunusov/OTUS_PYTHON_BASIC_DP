from sqladmin import Admin

from .access_token import AccessTokenAdmin
from .user import UserAdmin

def register_admin_views(admin: Admin):
    admin.add_view(AccessTokenAdmin)
    admin.add_view(UserAdmin)