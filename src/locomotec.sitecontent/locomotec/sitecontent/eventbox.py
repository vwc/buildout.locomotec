from five import grok
from Acquisition import aq_inner
from plone import api

from Products.CMFCore.utils import getToolByName

from plone.app.layout.viewlets.interfaces import IPortalFooter
from Products.CMFCore.interfaces import IFolderish

from locomotec.sitecontent.newsfolder import INewsFolder
from locomotec.sitecontent.newsentry import INewsEntry


class EventBoxViewlet(grok.Viewlet):
    grok.context(IFolderish)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalFooter)
    grok.name('locomotec.sitecontent.EventBoxViewlet')

    def update(self):
        self.has_newsfolder = len(self.get_newsfolders()) > 0
        self.has_items = len(self.get_items()) > 0

    def get_items(self):
        context = aq_inner(self.context)
        if self.has_newsfolder:
            archive = self.news_archive()
            navroot = archive.getObject()
        else:
            navroot = api.portal.get_navigation_root(context)
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog(object_provides=INewsEntry.__identifier__,
                         path=dict(query='/'.join(navroot.getPhysicalPath()),
                                   depth=3),
                         review_state='published',
                         sort_on='start',
                         sort_order='reverse',
                         sort_limit=3)[:3]
        return brains

    def news_archive(self):
        folders = self.get_newsfolders()
        return folders[0]

    def get_newsfolders(self):
        context = aq_inner(self.context)
        navroot = api.portal.get_navigation_root(context)
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog(object_provides=INewsFolder.__identifier__,
                         path=dict(query='/'.join(navroot.getPhysicalPath()),
                                   depth=1),
                         review_state='published')
        return brains
