#*- coding: utf-8 -*-
# Etienne Glossi - Février 2010
# etienne.glossi@gmail.com
# Filtres et Tags génériques pour l'application

from django import template

#Retourne le nom d'une url passé en paramètre
def get_filename(url):
    """ Nom du fichier dont l'url est passé en paramètre """
    filename = url.split("/")[-1]
    return " ".join(filename.split(".")[:-1]) #on retourne sans l'extension
    
register = template.Library() 
register.filter("filename", get_filename)
