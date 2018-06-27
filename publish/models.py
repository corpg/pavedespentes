#*- coding: utf-8 -*-

# Modèle de l'application Publish
# Contient les classes nécessaires à la publication sur le site d'articles et de dossiers, classés en catégories !
from django.db import models
from publication import Publication

#TODO: ajouter un model pour l'image d'illustration !
# Types de publication
# Pensez à ajouter admin.site.register(models.MaClasse) dans le fichier admin.py      
class Article(Publication):
    """
        Les articles forment le coeur du site ! Ceux-ci sont publiés dans des catégories bien distinctes.
    """
    Publication.register("Article") # on enregistre son type
    
    # --- Champs ---
    sous_titre = models.CharField('Sous titre', max_length=100, blank=True, null=True, help_text="Sous-titre d'accroche à l'article.")
    categorie = models.ForeignKey('Categorie', limit_choices_to={"profondeur__gt": 0})
    illustration = models.ImageField('Image d\'illustration', upload_to="upload/articles/%Y/%m/%d", help_text="Image qui apparaîtra à côté de l'article pour le représenter.", blank=True, null=True)
    mot_cles = models.CharField('Mot clés associés à l\'article', max_length=200, blank=True, null=True, help_text="Liste de mot clés facilitant la recherche d'articles/dossiers liés.", db_index=True)
    
    # L'URL absolue de l'article
    def get_absolute_url(self):
        # "/[categorie...]/[label]"
        return u"%s/%s.html" % (self.categorie.get_absolute_url(), self.label)
        
    # L'arborescence de l'article (les catégories pour y accéder
    def get_arbo(self):
        return " > ".join([c.nom for c in self.categorie.get_parentes()])
       
    # Classe interne Meta pour attribuer quelques options à la classe 
    class Meta:
        unique_together = (("titre", "categorie"), ("label", "categorie")) #le titre doit-être unique dans chaque categorie, de même que son label => autorise deux articles du même nom dans deux catégories différentes


class Edito(Publication):
    """
        Les Editos apparaissent sur la page d'accueil du site.
    """
    Publication.register("Edito") # on enregistre son type
