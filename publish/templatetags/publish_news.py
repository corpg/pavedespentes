#*- coding: utf-8 -*-
# Etienne Glossi - Février 2010
# etienne.glossi@gmail.com
# Génère la liste des dernières news à publier sur le site (colonne de gauche)

from django import template
from publish import models, Publication

class LastNewsNode(template.Node):
    """ Recense les dernières news """
    def __init__(self, name, number, for_last=None):
        self.name = name
        self.number = number

    def render(self, context):
        # Recuperation de self.number articles
        publications = list()
        try:
            typepub = getattr(models, "Article")
        except AttributeError, e:
            pass
        else:
            publications.extend(typepub.objects.filter(online=True))
        #On trie le tableau
        publications.sort(cmp=lambda x,y: cmp(y.date_parution, x.date_parution)) #reverse !
        #Insertion dans le contexte
        context[self.name] = publications[:self.number]
        return u''


#fonction enregistrée dans la bibliothèque des tags pour générer le menu
def load_ln(parser, token):
    """ Retourne un objet MenuCategorieNode qui rend le menu des catégories disponible via une variable passée en paramètre (ou utilisation de celle par défaut sinon).
    """
    args = token.split_contents()
    try:
        number = int(args[1])
        var_name = args[2] #on recupère le nom de la variable souhaité
    except IndexError:
        number = 5
        var_name = "last_news" #par défaut
    return LastNewsNode(var_name, number)
    
register = template.Library() 
register.tag("get_last_news", load_ln)
