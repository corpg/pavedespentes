#*- coding: utf-8 -*-
# Etienne Glossi - Novembre 2009
# etienne.glossi@gmail.com

# Modèle de la classe 'CategorieAdmin' qui sert de base à l'administration des catégorie (admin.site.register(Categorie, CategorieAdmin).
from default import PublishAdminForm, PublishAdmin
from publish import Categorie
from publish.utils import make_link

class CategorieAdmin(PublishAdmin):
    # --- Options --- #
    list_display = ('nom', 'cat_parent', 'display_pos', 'description')
    exclude = ('admin_users', 'link')
    list_filter = ('cat_parent',)

    # --- Méthodes surchargées --- #
    # Lors de l'enregistrement d'une catégorie
    def save_model(self, request, obj, form, change):
        obj.profondeur = obj.cat_parent.profondeur + 1 # on définit la profondeur
        obj.link = make_link(obj.nom)
        obj.save()

    # Retourne les catégories visualisables dans l'administration
    def queryset(self, request):
        return self.model.objects.exclude(profondeur = 0)
        #return Categorie.objects.get_categories(request.user)
       
