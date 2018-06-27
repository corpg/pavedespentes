#*- coding: utf-8 -*-
# Etienne Glossi - Novembre 2009
# etienne.glossi@gmail.com

# Administration de l'application
from django.contrib import admin
from django.contrib.sites.models import Site
from publish import models, Categorie
import article, edito, categorie

# Types de publications autorisées
admin.site.register(models.Article, article.ArticleAdmin)
admin.site.register(models.Edito, edito.EditoAdmin)

admin.site.register(Categorie, categorie.CategorieAdmin)
#admin.site.unregister(Site) # Supression de l'admininistration du site
