from django.contrib import admin

def configure_admin_site():
    admin.site.site_header = 'Vangti Admin'
    admin.site.site_title = 'Vangti Admin Portal'
    admin.site.index_title = 'Welcome to Vangti Admin Portal' 