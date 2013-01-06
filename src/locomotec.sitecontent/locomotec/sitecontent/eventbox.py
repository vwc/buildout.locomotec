from five import grok
from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName

from plone.app.layout.viewlets.interfaces import IPortalFooter
from Products.CMFCore.interfaces import IFolderish
from Products.ATContentTypes.interfaces.document import IATDocument

from locomotec.sitecontent.newsentry import INewsEntry


class EventBoxViewlet(grok.Viewlet):
    grok.context(IFolderish)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalFooter)
    grok.name('locomotec.sitecontent.EventBoxViewlet')

    def update(self):
        self.has_items = len(self.get_items()) > 0

    def get_items(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog(object_provides=INewsEntry.__identifier__,
                         review_state='published',
                         sort_on='start')
        return brains
