from five import grok
from Acquisition import aq_inner

from plone.app.layout.viewlets.interfaces import IPortalFooter
from Products.CMFCore.interfaces import IFolderish


class SubnavigationViewlet(grok.Viewlet):
    grok.context(IFolderish)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalFooter)
    grok.name('locomotec.sitecontent.SubnavigationViewlet')

    def contained_items(self):
        context = aq_inner(self.context)
        items = context.getFolderContents()
        return items
