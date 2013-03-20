from five import grok

from plone.app.layout.navigation.interfaces import INavigationRoot

from egomotion.sitecontent.interfaces import IEgomotionSite


class FrontpageView(grok.View):
    grok.context(INavigationRoot)
    grok.layer(IEgomotionSite)
    grok.require('zope2.View')
    grok.name('frontpage-view')


class FrontpageEN(grok.View):
    grok.context(INavigationRoot)
    grok.layer(IEgomotionSite)
    grok.require('zope2.View')
    grok.name('frontpage-en-view')
