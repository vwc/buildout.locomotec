from five import grok
from zope import schema
from plone.directives import dexterity, form

from plone.namedfile.interfaces import IImageScaleTraversable

from egomotion.sitecontent import MessageFactory as _


class IAnswer(form.Schema, IImageScaleTraversable):
    """
    A single survey participation
    """
    answers = schema.TextLine(
        title=_(u"Answers"),
        required=False,
    )
    participant = schema.TextLine(
        title=_(u"Participant number"),
        required=False,
    )
    claimed = schema.Bool(
        title=_(u"Sweepstake code claimed?"),
        required=False,
    )


class Answer(dexterity.Item):
    grok.implements(IAnswer)


class View(grok.View):
    grok.context(IAnswer)
    grok.require('zope2.View')
    grok.name('view')
