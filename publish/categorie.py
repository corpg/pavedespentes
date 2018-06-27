#*- coding: utf-8 -*-
# Etienne Glossi - Novembre 2009
# etienne.glossi@gmail.com
# Modèle de la classe 'Categorie', dans laquelle sont organisées les publications.

from django.db import models

# Profondeur maximale d'une catégorie
# TODO: intégrer dans un fichier de settings de l'application
PROFONDEUR_MAX = 3;

#Exception
class NoGirlsException(Exception):
    pass


# Gestionnaire des catégories
class CategorieManager(models.Manager):
    # --- hiérarchie générale des catégories ---
    def get_recursives(self, object=None, limit=PROFONDEUR_MAX):
        """ Méthode qui retourne toute les catégories filles d'une catégorie donnée, sous la forme:
        [
            'Mere',
            [
                'Fille_1', 
                [
                    'Fille_1_1',
                    'Fille_1_2'
                ],
                'Fille_2'
            ]
        ]
        """
        if object is None:
            object = super(CategorieManager, self).get_query_set().get(profondeur=0) #si pas d'objet, on recupère la catégorie principale
            limit += 1
        elif not isinstance(object, Categorie):
            raise TypeError("Object must be type of 'Categorie', not %s" % type(object))
        cats = [object, list()] #ajout de la catégorie mère
        if object.profondeur == PROFONDEUR_MAX: #aucune filles !
            return cats 
        for c in self.get_filles(object):
            if (limit-1) < 0: #limite la recursivité de la fonction
                break
            filles = self.get_recursives(c, limit-1) #ajout des filles
            if len(filles[1]) == 0:
                filles = [filles[0],]
            cats[1] += filles
        return cats
        
    def get_parentes(self, object):
        """ Retourne les catégories parentes à une catégorie passée en paramètre, sous la forme:    
        [parent_parent_object, parent_object, ..., object]
        """
        if not isinstance(object, Categorie):
            raise TypeError("Object must be type of 'Categorie', not %s" % type(object))
        parents = list()
        c = object
        for i in range(0, object.profondeur):
            parents.append(c)
            c = c.cat_parent
        parents.reverse()
        return parents
            
    def get_filles(self, object, recursive=False):
        """ Retourne une liste des categories filles de la catégorie passée en paramètre, sous la forme:
        [fille, filles, ...]
        """
        if object.profondeur == PROFONDEUR_MAX:
            return None
        qs = super(CategorieManager, self).get_query_set()
        filles = list()
        for c in qs.filter(cat_parent=object).order_by('display_pos', 'nom'):
            if c == object:
                continue
            if recursive:
                filles.append(self.get_filles(c, recursive))
            else:    
                filles.append(c) # la catégorie principale est sa propre mère !!!
        return filles
    
    # --- hiérarchie suivant l'utilisateur des catégories ---
    # TODO: cat ?              
    def get_by_user(self, user, cat=None):
        """ Méthode qui retourne toutes les catégories auquel un utilisateur a accès, sauf la catégorie passée en paramètre. """
        qs = super(CategorieManager, self).get_query_set()
        if user.is_superuser:
            return qs.all() #si super utilisateur, on visualise tout
        categories = list() # liste des objets 'Categorie' à afficher
        try:
            allow_cat = qs.filter(admin_users=user)
        except Categorie.DoesNotExist:
            return qs.none()
        for c in allow_cat:
            categories += self.get_filles(c, True) #on recupère les catégories filles
        id_cat = [c.id for c in categories if cat is None or (isinstance(cat, Categorie) and c.id != cat.id)]
        return super(CategorieManager, self).get_query_set().filter(pk__in=id_cat)
        
            
# Class Categorie principale
class Categorie(models.Model):
    """
    Chaque publication est dépendante d"une catégorie. Cette classe décrit l'implentation de ces catégories, hierarchisées selon une topologie site/catégorie mère/catégorie fille.
    Une "super-"catégorie racine portant le nom du projet est créée lors de l'initialisation de la base de données.
    """
    
    # --- Champs --- #
    nom = models.CharField("Nom", max_length=30)
    link = models.CharField("Lien", max_length=30)
    description = models.TextField("Description")
    cat_parent = models.ForeignKey("self", limit_choices_to={"profondeur__lt": PROFONDEUR_MAX}, verbose_name="Catégorie mère")
    profondeur = models.PositiveSmallIntegerField(default=1, editable=False)
    admin_users = models.ManyToManyField("auth.User", db_table="allow_user_categorie", help_text="Utilisateurs ayant la permission d'ajouter/supprimer/éditer des publications dans cette catégorie, et toute ses catégories filles\n.", verbose_name="Utilisateurs", blank=True, null=True, limit_choices_to={"is_superuser__exact": 0})
    display_pos = models.IntegerField("Position", default=0, blank=True, null=False, help_text="Position à donner à la catégorie lors de son affichage (relatif aux catégories de même profondeur).")
    
    # --- Manager --- #
    objects = CategorieManager()

    # --- Constructeurs --- #
    def __unicode__(self):
        return u'%s' % self.__str__()
        
    def __str__(self):
        return self.nom
        
    # --- Méthodes --- #
    # L'URL absolue de la catégorie        
    def get_absolute_url(self):
        # "/[categorie_parente]/[categorie]"
        cat = list()
        c = self
        for i in range(0, self.profondeur):
            cat.append(c.link)
            c = c.cat_parent
        cat.reverse()
        return "/" + "/".join(cat)
        
    # L'URL complète de la catégorie
    def get_complete_url(self):
        # "http://www.pavedespentes.fr/[categorie]"
        return "%s%s" % (settings.WEBSITE_URL, self.get_absolute_url())
        
    # Retourne les filles de la catégorie
    def get_filles(self):
        return Categorie.objects.get_filles(self)
        
    # Retourne les catégories parentes de la catégorie
    def get_parentes(self):
        return Categorie.objects.get_parentes(self)
        
    # --- Classes interne --- #
    # Classe interne Meta pour attribuer quelques options à la classe
    class Meta:
        ordering = ["nom"] # afficher les catégories suivant leur nom croissant
        unique_together = (("nom", "cat_parent"), ) # les catégories filles doivent-être unique (permet ainsi des catégories de même nom dans des catégories différentes, mais pas dans la même catégorie).
