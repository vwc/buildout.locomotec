from five import grok
from plone.directives import dexterity, form

from plone.namedfile.interfaces import IImageScaleTraversable

from plone.app.textfield import RichText

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
