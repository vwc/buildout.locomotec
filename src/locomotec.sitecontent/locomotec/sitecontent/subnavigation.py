from five import grok
from Acquisition import aq_inner
from plone import api

from zope.interface import Interface

from Products.CMFCore.utils import getToolByName

from plone.app.layout.viewlets.interfaces import IPortalFooter

from locomotec.sitecontent.contentpage import IContentPage


class SubnavigationViewlet(grok.Viewlet):
    grok.context(IContentPage)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalFooter)
    grok.name('locomotec.sitecontent.SubnavigationViewlet')

    def update(self):
        self.has_items = len(self.contained_items()) > 0

    def contained_items(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog(object_provides=IContentPage.__identifier__,
                         path=dict(query='/'.join(context.getPhysicalPath()),
                                   depth=1),
                         review_state='published')
        return brains


class LanguageSwitch(grok.Viewlet):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalFooter)
    grok.name('locomotec.sitecontent.LanguageSwitch')

    def switcher_base_url(self):
        return api.portal.get().absolute_url()
