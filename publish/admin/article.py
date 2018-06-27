#*- coding: utf-8 -*-
# Etienne Glossi - Novembre 2009
# etienne.glossi@gmail.com

from publication import PublicationAdmin

#TODO: include in configuration file
ALLOW_FILE_EXT = ('jpg', 'png', 'jpeg', 'gif')

class ArticleAdmin(PublicationAdmin):
    list_display = ('titre', 'categorie', 'auteur', 'date_creation', 'date_modification', 'online')
    fields = ('titre', 'sous_titre', 'categorie', 'illustration', 'contenu', 'online')
    list_filter = ('categorie', 'online')
    #exclude = ('illustration')
    
    # Lors de la sauvegarde d'un article
    def save_model(self, request, obj, form, change):
        if obj.illustration:
            #vérification du type de fichier
            filename = obj.illustration.name.split("/")[-1]
            extension = filename.split(".")[-1]
            if extension not in ALLOW_FILE_EXT:
                raise TypeError("Unauthorized Image Upload: %s" % filename)
            
        #if obj.sous_titre:
        #    obj.sous_titre = obj.sous_titre[0].lower() + obj.sous_titre[1:] #mise en miniscule
        super(ArticleAdmin, self).save_model(request, obj, form, change)
