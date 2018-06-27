#*- coding: cp1252 -*-
# Etienne Glossi - Novembre 2009
# etienne.glossi@gmail.com

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import direct_to_template
from publish import Categorie, Publication
import models

def detail_categorie(request, categorie_link):
    """ Obtenir le contenu d'une catégorie """
    # Recupération de la categorie
    categorie = get_object_or_404(Categorie, link=categorie_link)
    # Récupération des différentes publication de la categorie
    try:
        typepub = getattr(models, "Article")
    except AttributeError, e:
        publications = ""
    else:
        publications = typepub.objects.filter(categorie=categorie.id, online=True)
    # Création du contexte        
    contexte = {
        "categorie"      : categorie,
        "articles"       : publications,
        "categorie_arbre": Categorie.objects.get_recursives(categorie)
    }
    return direct_to_template(request, 'detail.html', contexte)
    
def view_publication(request, categorie_link, publication_label):
    cat = Categorie.objects.get(link=categorie_link)
    pub = get_object_or_404(models.Article, label=publication_label, categorie=cat)
    if (pub.auteur.first_name and pub.auteur.last_name):
        auteur = "%s %s" % (pub.auteur.first_name, pub.auteur.last_name)
    else:
        auteur = pub.auteur.username
    if pub.auteur.email:
        auteur = "<a href='mailto:%s' title=\"Contacter l'auteur\">%s</a>" % (pub.auteur.email, auteur) 
    # Création du contexte
    contexte = {
        "categorie"  :  cat,
        "publication":  pub,
        "contenu"    :  pub.contenu,
        "auteur"     :  auteur
    }
    return direct_to_template(request, 'view_publication.html', contexte)


