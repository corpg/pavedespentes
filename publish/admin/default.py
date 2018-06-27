#*- coding: utf-8 -*-
# Etienne Glossi - Novembre 2009
# etienne.glossi@gmail.com

# Définit deux nouvelles classes: 
#       * PublishAdminForm, qui permet de modifier le queryset d'un objet de type Field
#       * PublishAdmin, qui modifie le formulaire d'administration par défaut

from django.contrib.admin import ModelAdmin, helpers
from django.contrib.admin.util import unquote
from django.forms.models import ModelForm
from django.forms.forms import BoundField
from django.forms.util import ErrorList
from django.forms.formsets import all_valid
from django.db import models, transaction
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


class PublishAdminForm(ModelForm):
    " Formulaire par défaut de l'application. Surcharger la méthode queryset(self, field, name) dans les classes filles."
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList, label_suffix=':', empty_permitted=False, instance=None, user=None):
        self.user = user # notre formulaire connait l'utilisateur
        super(PublishAdminForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance)
                
    def __getitem__(self, name):
        "Returns a BoundField with the given name."
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError('Key %r not found in Form' % name)
        self._field_queryset(field, name) # nouveau queryset
        return BoundField(self, field, name)
                
    def _field_queryset(self, field, name):
        "Méthode qui modifie le queryset de l'élément Field"
        queryset = self.queryset(field, name)
        if queryset is not None and isinstance(queryset, models.query.QuerySet): 
            field.queryset = queryset
                
    def queryset(self, field, name):
        "Méthode à surcharger qui retourne un nouveau queryset et ainsi modifier celui par défaut de l'élément Field"
        return None
                

class PublishAdmin(ModelAdmin):
    "Nouveau modèle d'administration qui permet de modifier la formulaire d'administration. Par défaut, le formulaire utilisé est PublishAdminForm."
    # --- Constructeur --- #
    def __init__(self, model, admin_site, form=PublishAdminForm):
        self.form = form # formulaire d'admin
        super(PublishAdmin, self).__init__(model, admin_site)
                
    # --- Méthodes surchargés --- #
    # Lors de la création d'un enregistrement       
    def add_view(self, request, form_url='', extra_context=None):
        "The 'add' admin view for this model."
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        ModelForm = self.get_form(request)
        formsets = []
        if request.method == 'POST':
            # on précise l'utilisateur dans le formulaire
            form = ModelForm(request.POST, request.FILES, user=request.user)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=False)
            else:
                form_validated = False
                new_object = self.model()
            prefixes = {}
            for FormSet in self.get_formsets(request):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                                  instance=new_object,
                                  save_as_new=request.POST.has_key("_saveasnew"),
                                  prefix=prefix)
                formsets.append(formset)
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=False)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=False)

                self.log_addition(request, new_object)
                return self.response_add(request, new_object)
        else:
            # Prepare the dict of initial data from the request.
            # We have to special-case M2Ms as a list of comma-separated PKs.
            initial = dict(request.GET.items())
            for k in initial:
                try:
                    f = opts.get_field(k)
                except models.FieldDoesNotExist:
                    continue
                if isinstance(f, models.ManyToManyField):
                    initial[k] = initial[k].split(",")
            # on précise l'utilisateur dans le formulaire
            form = ModelForm(initial=initial, user=request.user)
            prefixes = {}
            for FormSet in self.get_formsets(request):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=self.model(), prefix=prefix)
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)), self.prepopulated_fields)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': request.REQUEST.has_key('_popup'),
            'show_delete': False,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url, add=True)
    add_view = transaction.commit_on_success(add_view)
        
        # Lors de la modification d'un enregistrement
    def change_view(self, request, object_id, extra_context=None):
        "The 'change' admin view for this model."
        model = self.model
        opts = model._meta

        try:
            obj = self.queryset(request).get(pk=unquote(object_id))
        except model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST' and request.POST.has_key("_saveasnew"):
            return self.add_view(request, form_url='../add/')

        ModelForm = self.get_form(request, obj)
        formsets = []
        if request.method == 'POST':
            # on précise l'utilisateur dans le formulaire
            form = ModelForm(request.POST, request.FILES, instance=obj, user=request.user)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            prefixes = {}
            for FormSet in self.get_formsets(request, new_object):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix)
                formsets.append(formset)

            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                change_message = self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object)

        else:
            # on précise l'utilisateur dans le formulaire
            form = ModelForm(instance=obj, user=request.user)
            prefixes = {}
            for FormSet in self.get_formsets(request, obj):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix)
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj), self.prepopulated_fields)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': request.REQUEST.has_key('_popup'),
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=obj)
    change_view = transaction.commit_on_success(change_view)
