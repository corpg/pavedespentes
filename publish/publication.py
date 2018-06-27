#*- coding: utf-8 -*-
# Etienne Glossi - Novembre 2009
# etienne.glossi@gmail.com

# Modèle de la classe abstraite 'Publication'. Les classes 'Articles' et 'Dossiers' héritent de celle-ci.
from datetime import date
from django.db import models
from django.conf import settings

# Manager des Publications
class PublicationManager(models.Manager):
    #TODO: ne fonctionne pas tip-top. Cause à un cache ?
    def get_latest_publication(self):
        """ Retourne la dernière publication publiée ! """
        #return super(PublicationManager, self).get_query_set().filter(online=True).latest()
        latest = super(PublicationManager, self).get_query_set().filter(online=True).order_by('-date_modification')
        try:
            latest = latest[0]
        except IndexError:
            latest = None
        return latest

class Publication(models.Model):
    """
    Gère les publications en général.
    """
    
    # --- Champs --- #
    titre = models.CharField('Titre', max_length=100)
    label = models.SlugField('Adresse', max_length=130, help_text="Adresse permettant de visualiser l'article: www.lepavedespentes.fr/.../[label]/.")
    auteur = models.ForeignKey('auth.User', editable=False)
    contenu = models.TextField('Contenu')
    date_parution = models.DateTimeField('Date de publication', blank=True, null=True, editable=False)
    date_creation = models.DateTimeField('Date de creation', auto_now=False, auto_now_add=True, editable=False)
    date_modification = models.DateTimeField('Date de derniere modification', auto_now=True, editable=False)
    online = models.BooleanField('Publier')
    
    # --- Enregistre les différents types de publication créés --- #
    types = list()
    
    # --- Manager --- #
    objects = PublicationManager()
    
    # --- Constructeurs --- #
    def __unicode__(self):
        return u'%s' % self.__str__()
        
    def __str__(self):
        return self.titre
    
    # --- Méthodes --- #
    # Enregistre dans un tuple le nom de la classe -- méthode statique
    def register(class_name):
        if class_name not in Publication.types:
            Publication.types.append(class_name)
    register = staticmethod(register)
        
    # Retourne le type de la publication (nom de classe)
    def get_type(self):
        return self.__class__.__name__.lower()
    
    # L'URL absolue de l'article    
    def get_absolute_url(self):
        return str(self)
    
    # L'URL complète de la publication     
    def get_complete_url(self):
        # "http://www.pavedespentes.fr/[categorie...]/[label_publication]"
        return "%s%s" % (settings.WEBSITE_URL, self.get_absolute_url())
        
    # Retourne un booléen indiquant si l'article a été publié aujourd'hui
    def is_paru_today(self):
        return self.date_parution.date() == date.today()

    # Classe interne Meta pour attribuer quelques options à la classe
    class Meta:
        abstract = True # classe abstraite (il faut l'hériter pour l'utiliser)
        get_latest_by = 'date_modification' # dernière publication modifiée
        ordering = ['-date_parution'] # afficher les publication suivant leur date de parution décroissant
