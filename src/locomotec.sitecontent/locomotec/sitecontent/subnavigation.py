from five import grok
from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName

from plone.app.layout.viewlets.interfaces import IPortalFooter
from Products.CMFCore.interfaces import IFolderish
from Products.CMFDefault.interfaces import IDocument


class SubnavigationViewlet(grok.Viewlet):
    grok.context(IFolderish)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalFooter)
    grok.name('locomotec.sitecontent.SubnavigationViewlet')

    def update(self):
        self.has_items = len(self.contained_items()) > 0

    def contained_items(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog(object_provides=IDocument.__identifier__,
                         path=dict(query='/'.join(context.getPhysicalPath()),
                                   depth=1),
                         review_state='published')
        return brains
