#*- coding: utf-8 -*-
# Etienne Glossi - Novembre 2009
# etienne.glossi@gmail.com

from publication import PublicationAdmin

class EditoAdmin(PublicationAdmin):
    list_display = ('titre', 'date_creation', 'date_modification', 'online')
