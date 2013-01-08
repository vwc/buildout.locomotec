from five import grok
from Acquisition import aq_inner
from zope import schema

from plone import api
from plone.directives import dexterity, form

from plone.namedfile.interfaces import IImageScaleTraversable

from plone.app.textfield import RichText

from plone.app.contentlisting.interfaces import IContentListing

from locomotec.sitecontent import MessageFactory as _


class IContentPage(form.Schema, IImageScaleTraversable):
    """
    A folderish content page with automatic content listing
    """
    teaser = schema.Text(
        title=_(u"Frontpage Teaser"),
        description=_(u"Optional teaser text for the frontpage should this "
                      u"content page be displayed as a preview"),
        required=False,
    )
    text = RichText(
        title=_(u"Text"),
        description=_(u"The main body text of this content page. Will be "
                      u"displayed in automatic subcontent listings or above "
                      u"the subcontents as an optional introduction"),
        required=False,
    )


class ContentPage(dexterity.Container):
    grok.implements(IContentPage)


class View(grok.View):
    grok.context(IContentPage)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_subpages = len(self.subpages()) > 0
        self.anonymous = api.user.is_anonymous()

    def subpages(self):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IContentPage.__identifier__,
                        path=dict(query='/'.join(context.getPhysicalPath()),
                                  depth=1),
                        review_state='published',
                        sort_on='getObjPositionInParent')
        results = IContentListing(items)
        return results
