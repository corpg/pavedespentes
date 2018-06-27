#*- coding: utf-8 -*-
# Etienne Glossi - Novembre 2009
# etienne.glossi@gmail.com
# See for more informations: http://www.b-list.org/weblog/2008/dec/24/admin/

# Modèle de la classe 'PublicationAdmin' qui sert de base à l'administration des publications (admin.site.register(MaPublication, PublicationAdmin).

from datetime import datetime
from default import PublishAdminForm, PublishAdmin
from publish import models, Publication
from publish.utils import make_link            

class PublicationAdmin(PublishAdmin):
    exclude = ('label', 'mot_cles')
    list_display = ('titre', 'auteur', 'date_creation', 'date_modification', 'online')

    # --- Méthodes surchargées --- #
    # Lors de l'enregistrement d'une catégorie
    def save_model(self, request, obj, form, change):
        if not change:
            obj.auteur = request.user # on définit l'auteur à la création
        if obj.online and not obj.date_parution:
            obj.date_parution = datetime.now()
        elif not obj.online:
            obj.date_parution = None
        obj.label = make_link(obj.titre)
        obj.save()
