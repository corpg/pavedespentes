#*- coding: utf-8 -*-
# Etienne Glossi - Janvier 2010
# etienne.glossi@gmail.com
# Contient l'ensemble des tags et filtres utilisés avec les catégories
# TODO: créer un tag pour générer les liens des articles

from django import template
from publish import Categorie
from publish.categorie import NoGirlsException
from publish.models import Article

# Node qui permet d'insérer la variable name dans le context lors de la compilation du template (appel de la méthode render())
class MenuCategorieNode(template.Node):
    """ Permet la génération du menu """
    def __init__(self, name):
        self.name = name
        
    def render(self, context):
        categories = Categorie.objects.get_recursives(limit=1)[1] #on recupère les categories (sans la principale) avec leurs filles
        
        #on transforme notre tableau en dictionnaire {mere: [filles], mere: [filles]}
        categories_fin = list()
        i = 0
        while(i < len(categories)):
            try: #ouh que c'est moche !!! Mais ca fait tellement de bien ^^
                filles = categories[i+1]
                if type(filles) != list:
                    raise NoGirlsException
                categories_fin.append([categories[i], categories[i+1]])
                i+=1 #incrementation car nous avons trouvé des filles
            except Exception: #NoGirlsException, IndexError:
                categories_fin.append([categories[i], list()])
            i+=1
        context[self.name] = categories_fin #insertion dans le context du template, sous le nom name
        return u''     


class CategorieNode(template.Node):        
    def render(self, context):
       categories = Categorie.objects.get_recursives(context['categorie'])
       #context['categorie_arbres'] = categories
       #return u''
       return self.arbre_categorie(context['categorie'], categories)

    def arbre_categorie(self, cat, categories, level=0):
        """ Retourne un arbre HTML des catégories
                cat: Categorie racine
                categories: liste contenant l'ensemble des catégories depuis cat et contenant l'ensemble des catégories filles (du type de Categorie.objects.get_recursives_categories())
                level: niveau relatif (for future use...)
        """
        if level<=0: level = cat.profondeur
        arbre = "<a href='%s'>%s</a>: %s" % (cat.get_absolute_url(), cat.nom, cat.description)
        if categories.has_key(cat):
            arbre += "<ul>"
            for c in categories[cat]:
                arbre += "<li>" + self.arbre_categorie(c, categories, level) + "</li>"
            arbre += "</ul>"
        return arbre

#fonction enregistrée dans la bibliothèque des tags pour générer le menu
def load_menu(parser, token):
    """ Retourne un objet MenuCategorieNode qui rend le menu des catégories disponible via une variable passée en paramètre (ou utilisation de celle par défaut sinon).
    """
    try:
        var_name = token.split_contents()[1] #on recupère le nom de la variable souhaité
    except IndexError:
        var_name = "menu" #par défaut
    return MenuCategorieNode(var_name)

# Fonction qui rend disponible l'accès aux catégories pour le menu
def display_categories_filles(parser, token):
    return CategorieNode()
    
# Retourne les articles d'une catégorie
def get_publications(categorie):
    return Article.objects.filter(online=True, categorie=categorie)
    
register = template.Library()
register.filter('articles', get_publications)   
register.tag("load_menu", load_menu)
