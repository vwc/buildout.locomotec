from five import grok
from plone import api
from Acquisition import aq_inner

from zope.interface import Interface
from zope.component import getMultiAdapter

from plone.app.layout.viewlets.interfaces import IPortalFooter

from egomotion.sitecontent.interfaces import IEgomotionSite


class NavBarViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.layer(IEgomotionSite)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalFooter)
    grok.name('egomotion.sitecontent.NavBarViewlet')

    def update(self):
        self.portal_url = api.portal.get().absolute_url()

    def current_lang(self):
        context = aq_inner(self.context)
        pstate = getMultiAdapter((context, self.request),
                                 name=u"plone_portal_state")
        lang = pstate.language()
        return lang
