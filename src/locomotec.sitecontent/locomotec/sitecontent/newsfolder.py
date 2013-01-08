from Acquisition import aq_inner
from five import grok
from plone import api
from plone.directives import dexterity, form

from plone.app.textfield import RichText

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.app.contentlisting.interfaces import IContentListing

from locomotec.sitecontent.newsentry import INewsEntry

from locomotec.sitecontent import MessageFactory as _


class INewsFolder(form.Schema, IImageScaleTraversable):
    """
    A folder for a unified news and events type
    """
    text = RichText(
        title=_(u"Introductional text"),
        description=_(u"Optional introductional text for the news and event "
                      u"archive view"),
        required=False,
    )


class NewsFolder(dexterity.Container):
    grok.implements(INewsFolder)


class View(grok.View):
    grok.context(INewsFolder)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_news = len(self.contained_news()) > 0

    def contained_news(self):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=INewsEntry.__identifier__,
                        path=dict(query='/'.join(context.getPhysicalPath()),
                                  depth=1),
                        review_state='published',
                        sort_on='start',
                        sort_order='reverse')
        results = IContentListing(items)
        return results
