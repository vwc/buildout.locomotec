from DateTime import DateTime
from five import grok

from zope import schema

from plone.directives import dexterity, form
from plone.indexer import indexer

from plone.app.textfield import RichText

from plone.namedfile.interfaces import IImageScaleTraversable

from locomotec.sitecontent import MessageFactory as _


class INewsEntry(form.Schema, IImageScaleTraversable):
    """
    News or event anouncement
    """
    location = schema.TextLine(
        title=_(u"Location"),
        required=True,
    )
    start = schema.Datetime(
        title=_(u"Date"),
        description=_(u"Please enter a date like either the event date or "
                      u"the release date of the news entry"),
        required=True,
    )
    text = RichText(
        title=_(u"Summary"),
        required=True,
    )


@indexer(INewsEntry)
def startIndexer(obj):
    if obj.start is None:
        return None
    return DateTime(obj.start.isoformat())
grok.global_adapter(startIndexer, name="start")


class NewsEntry(dexterity.Item):
    grok.implements(INewsEntry)


class View(grok.View):
    grok.context(INewsEntry)
    grok.require('zope2.View')
    grok.name('view')
