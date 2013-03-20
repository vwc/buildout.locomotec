from five import grok
from Acquisition import aq_inner

from zope.component import getMultiAdapter

from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.interfaces import IFolderish

from egomotion.sitecontent.interfaces import IEgomotionSite


class FrontpageView(grok.View):
    grok.context(INavigationRoot)
    grok.layer(IEgomotionSite)
    grok.require('zope2.View')
    grok.name('frontpage-view')

    def current_lang(self):
        context = aq_inner(self.context)
        pstate = getMultiAdapter((context, self.request),
                                 name=u"plone_portal_state")
        lang = pstate.language()
        return lang


class FrontpageFolder(grok.View):
    grok.context(IFolderish)
    grok.layer(IEgomotionSite)
    grok.require('zope2.View')
    grok.name('frontpage-folder-view')
