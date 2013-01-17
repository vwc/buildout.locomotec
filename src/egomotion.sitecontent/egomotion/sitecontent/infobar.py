from five import grok
from plone import api

from zope.interface import Interface

from plone.app.layout.viewlets.interfaces import IPortalFooter

from egomotion.sitecontent.interfaces import IEgomotionSite


class InfoBarViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.layer(IEgomotionSite)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalFooter)
    grok.name('egomotion.sitecontent.InfoBarViewlet')

    def update(self):
        self.portal_url = api.portal.get().absolute_url()
