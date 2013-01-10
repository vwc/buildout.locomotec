from Acquisition import aq_inner
from five import grok
from plone import api

from zope.interface import Interface

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import NavtreeStrategyBase
from plone.app.layout.navigation.navtree import buildFolderTree

from plone.app.layout.viewlets.interfaces import IPortalFooter

from locomotec.sitecontent.interfaces import ILocomotecSite


class NavbarViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.layer(ILocomotecSite)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalFooter)
    grok.name('locomotec.sitecontent.NavbarViewlet')

    def sections(self):
        context = aq_inner(self.context)
        portal = api.portal.get()
        en_root = portal['en']
        root = getNavigationRoot(context)
        type_interface = 'locomotec.sitecontent.contentpage.IContentPage'
        path = {'query': '/'.join(en_root.getPhysicalPath()),
                'navtree': 2,
                'navtree_start': 2}
        query = {'path': path,
                 'review_state': 'published',
                 'object_provides': type_interface,
                 'sort_on': 'getObjPositionInParent'}
        root_obj = context.unrestrictedTraverse(root)
        tree = buildFolderTree(root_obj, root_obj, query,
                               strategy=NavtreeStrategyBase())
        items = []
        for c in tree['children']:
            item = {}
            item['item'] = c['item']
            item['children'] = c.get('children', '')
            items.append(item)
        return items

    def isActiveItem(self, itemid):
        context = aq_inner(self.context)
        context_id = context.getId()
        if itemid == context_id:
            return 'navitem active'
        else:
            return 'navitem'

    def en_base_url(self):
        portal_url = api.portal.get().absolute_url()
        portal_url_en = portal_url + '/en'
        return portal_url_en
