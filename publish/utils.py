#*- coding: utf-8 -*-
# Etienne Glossi - Janvier 2010
# etienne.glossi@gmail.com

# Contient des fonctions générales

def make_link(nom):
    """ Remplace certains caractères par d'autres afin de rendre la barre d'adresse plus accessible. """
    to_replace = { # caractères à remplacer
        u'é': u'e',
        u'è': u'e',
        u'ê': u'e',
        u'ô': u'o',
        u'à': u'a',
        u' ': u'-',
        u"'": u'-',
        u'"': u'',
        u'î': u'i',
        u'û': u'u',
        u'!': '',
        u'?': '',
        u'.': '',
        u',': '',
        u'’': '-'
    }
    for char in to_replace:
        new_char = to_replace[char]
        nom = nom.replace(char, new_char)        
    return nom.lower()
