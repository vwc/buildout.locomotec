import csv
import codecs
import cStringIO
from five import grok

from zope.interface import Interface
from zope.globalrequest import getRequest

from collective.beaker.interfaces import ISession

from egomotion.sitecontent import MessageFactory as _

SESSION_KEY = 'Uh53dAfH2JPzI/lIhBvN72RJzZVv6zk5'


class ISurveyTool(Interface):
    """ Survey processing tool that stores data inside a beaker session
        storage. The data is then saved as survey participation result
    """

    def get(context):
        """ Get active survey session

            @param uuid: optional catalog uuid of active participation
        """

    def destroy(context):
        """ Destroy a survey session on submitting or by user
            interaction
        """

    def add(context):
        """ Add answers to a survey session or update existing data

            @param uuid: catalog uuid of participation object
            @param answers: serialized form data of survey answers
        """

    def update(context):
        """ Update potentially autosaved form data in session
            storage

            @param uuid: catalog uuid of participation object
            @param answers: serialized survey form data
        """

    def remove(context):
        """ Remove answers from the session

            @param uuid: catalog uuid of participation object
        """


class SurveyTool(grok.GlobalUtility):
    grok.provides(ISurveyTool)

    def get(self, key=None):
        survey_id = 'survey.%s' % SESSION_KEY
        if key is not None:
            survey_id = 'survey.%s' % key
        session = ISession(getRequest())
        if survey_id not in session:
            session[survey_id] = dict()
            session.save()
        return session[survey_id]

    def destroy(self, key=None):
        survey_id = 'survey.%s' % SESSION_KEY
        if key is not None:
            survey_id = 'survey.%s' % key
        session = ISession(getRequest())
        if survey_id in session:
            del session[survey_id]
            session.save()

    def add(self, uuid, answers=None):
        """
            Add item to survey session
        """
        survey = self.get()
        item = self.update(uuid, answers)
        if not item:
            survey[uuid] = answers
            return survey[uuid]

    def update(self, uuid, answers):
        survey = self.get()
        item_id = uuid
        if item_id in survey:
            survey[item_id] = answers
            return survey[item_id]
        return None

    def remove(self, uuid):
        survey = self.get()
        if uuid in survey:
            del survey[uuid]
            return uuid


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def survey_fields_ordered():
        fields = (
            'pid',
            'pip',
            'puid',
            'favorite1',
            'favorite1.likes.one',
            'favorite1.likes.two',
            'favorite1.likes.three',
            'favorite1.dislikes.one',
            'favorite1.dislikes.two',
            'favorite1.dislikes.three',
            'favorite2',
            'favorite2.likes.one',
            'favorite2.likes.two',
            'favorite2.likes.three',
            'favorite2.dislikes.one',
            'favorite2.dislikes.two',
            'favorite2.dislikes.three',
            'favorite3',
            'favorite3.likes.one',
            'favorite3.likes.two',
            'favorite3.likes.three',
            'favorite3.dislikes.one',
            'favorite3.dislikes.two',
            'favorite3.dislikes.three',
            'dislikes.one',
            'dislikes.two',
            'dislikes.three',
            'functionality.1',
            'functionality.2',
            'functionality.3',
            'functionality.4',
            'functionality.5',
            'functionality.6',
            'functionality.7',
            'functionality.additional',
            'accessory.1',
            'accessory.2',
            'accessory.3',
            'accessory.additional',
            'benefit.1',
            'benefit.2',
            'benefit.3',
            'benefit.additional',
            'frequency',
            'roadwork',
            'trainingresource.1',
            'trainingresource.2',
            'trainingresource.3',
            'trainingresource.4',
            'trainingresource.5',
            'trainingresource.6',
            'trainingresource.7',
            'trainingresource.8',
            'trainingresource.9',
            'trainingresource.10',
            'trainingresource.additional',
            'trainingresource.effect',
            'training.monitor',
            'training.personalization',
            'training.maxprice',
            'participant.age',
            'participant.gender',
            'participant.occupation',
            'investment',
            'participant.investment.1',
            'participant.investment.2',
            'participant.investment.3',
            'participant.investment.4',
            'participant.investment.5',
            'price.hometrainer',
            'price.treadmill',
            'price.crosstrainer',
            'price.bike',
            'price.mountainbike',
            'price.trainer',
            'price.club',
            'purchase',
            'purchase.comment',
            'interest.1',
            'interest.2',
            'email')
        return fields


def survey_fields_datacollection():
        fields = (
            'pid',
            'pip',
            'puid',
            'favorite1',
            'favorite1.likes.one',
            'favorite1.likes.two',
            'favorite1.likes.three',
            'favorite1.dislikes.one',
            'favorite1.dislikes.two',
            'favorite1.dislikes.three',
            'favorite2',
            'favorite2.likes.one',
            'favorite2.likes.two',
            'favorite2.likes.three',
            'favorite2.dislikes.one',
            'favorite2.dislikes.two',
            'favorite2.dislikes.three',
            'favorite3',
            'favorite3.likes.one',
            'favorite3.likes.two',
            'favorite3.likes.three',
            'favorite3.dislikes.one',
            'favorite3.dislikes.two',
            'favorite3.dislikes.three',
            'dislikes.one',
            'dislikes.two',
            'dislikes.three',
            'functionality',
            'functionality.additional',
            'accessory',
            'accessory.additional',
            'benefit',
            'benefit.additional',
            'frequency',
            'roadwork',
            'trainingresource',
            'trainingresource.additional',
            'trainingresource.effect',
            'training.monitor',
            'training.personalization',
            'training.maxprice',
            'participant.age',
            'participant.gender',
            'participant.occupation',
            'investment',
            'participant.investment',
            'price.hometrainer',
            'price.treadmill',
            'price.crosstrainer',
            'price.bike',
            'price.mountainbike',
            'price.trainer',
            'price.club',
            'purchase',
            'purchase.comment',
            'interest',
            'email')
        return fields


def survey_fields_multiselect():
        fields = {
            'interest': ('interest.1', 'interest.2'),
            'benefit': ('benefit.1', 'benefit.2', 'benefit.3'),
            'accessory': ('accessory.1', 'accessory.2', 'accessory.3'),
            'participant.investment': ('participant.investment.1',
                                       'participant.investment.2',
                                       'participant.investment.3',
                                       'participant.investment.4',
                                       'participant.investment.5'),
            'functionality': ('functionality.1', 'functionality.2',
                              'functionality.3', 'functionality.4',
                              'functionality.5', 'functionality.6',
                              'functionality.7'),
            'trainingresource': ('trainingresource.1', 'trainingresource.2',
                                 'trainingresource.3', 'trainingresource.4',
                                 'trainingresource.5', 'trainingresource.6',
                                 'trainingresource.7', 'trainingresource.8',
                                 'trainingresource.9', 'trainingresource.10'),
            'interest': ('interest.1', 'interest.2'),
        }
        return fields


def survey_fields_select():
    fields = (
        'participant.occupation', 'participant.gender', 'roadwork',
        'frequency', 'purchase',
        'training.monitor', 'trainingresource.effect',
        'training.maxprice', 'training.personalization',
        'price.crosstrainer', 'price.bike', 'price.hometrainer',
        'price.club', 'price.trainer', 'price.treadmill',
        'price.mountainbike'
    )
    return fields


def survey_fields_i18n():
        fields = {
            u'pid': _(u"Participant ID"),
            u'pip': _(u"Participant IP"),
            u'puid': _(u"Participant Code"),
            u'favorite1': _(u"Favorite 1"),
            u'favorite1.likes.one': _(u"Favorite 1 - Like 1"),
            u'favorite1.likes.two': _(u"Favorite 1 - Like 2"),
            u'favorite1.likes.three': _(u"Favorite 1 - Like 3"),
            u'favorite1.dislikes.one': _(u"Favorite 1 - Dislike 1"),
            u'favorite1.dislikes.two': _(u"Favorite 1 - Dislike 2"),
            u'favorite1.dislikes.three': _(u"Favorite 1 - Dislike 3"),
            u'favorite2': _(u"Favorite 2"),
            u'favorite2.likes.one': _(u"Favorite 2 - Like 1"),
            u'favorite2.likes.two': _(u"Favorite 2 - Like 2"),
            u'favorite2.likes.three': _(u"Favorite 2 - Like 3"),
            u'favorite2.dislikes.one': _(u"Favorite 2 - Dislike 1"),
            u'favorite2.dislikes.two': _(u"Favorite 2 - Dislike 2"),
            u'favorite2.dislikes.three': _(u"Favorite 2 - Dislike 3"),
            u'favorite3': _(u"Favorite 3"),
            u'favorite3.likes.one': _(u"Favorite 3 - Like 1"),
            u'favorite3.likes.two': _(u"Favorite 3 - Like 2"),
            u'favorite3.likes.three': _(u"Favorite 3 - Like 3"),
            u'favorite3.dislikes.one': _(u"Favorite 3 - Dislike 1"),
            u'favorite3.dislikes.two': _(u"Favorite 3 - Dislike 2"),
            u'favorite3.dislikes.three': _(u"Favorite 3 - Dislike 3"),
            u'dislikes.one': _(u"Dislike One"),
            u'dislikes.two': _(u"Dislike Two"),
            u'dislikes.three': _(u"Dislike Three"),
            u'functionality.1': _(u"Functionality 1"),
            u'functionality.2': _(u"Functionality 2"),
            u'functionality.3': _(u"Functionality 3"),
            u'functionality.4': _(u"Functionality 4"),
            u'functionality.5': _(u"Functionality 5"),
            u'functionality.6': _(u"Functionality 6"),
            u'functionality.7': _(u"Functionality 7"),
            u'functionality.additional': _(u"Functionality Additional"),
            u'accessory.1': _(u"Accessory One"),
            u'accessory.2': _(u"Accessory Two"),
            u'accessory.3': _(u"Accessory Three"),
            u'accessory.additional': _(u"Accessory Additional"),
            u'benefit.1': _(u"Benefit One"),
            u'benefit.2': _(u"Benefit Two"),
            u'benefit.3': _(u"Benefit Three"),
            u'benefit.additional': _(u"Benefit Additional"),
            u'frequency': _(u"Training Frequency"),
            u'roadwork': _(u"Roadwork"),
            u'trainingresource.1': _(u"Training Resource 1"),
            u'trainingresource.2': _(u"Training Resource 2"),
            u'trainingresource.3': _(u"Training Resource 3"),
            u'trainingresource.4': _(u"Training Resource 4"),
            u'trainingresource.5': _(u"Training Resource 5"),
            u'trainingresource.6': _(u"Training Resource 6"),
            u'trainingresource.7': _(u"Training Resource 7"),
            u'trainingresource.8': _(u"Training Resource 8"),
            u'trainingresource.9': _(u"Training Resource 9"),
            u'trainingresource.10': _(u"Training Resource 10"),
            u'trainingresource.additional': _(u"Training Resource Additional"),
            u'trainingresource.effect': _(u"Training Resource Effect"),
            u'training.monitor': _(u"Training Monitor"),
            u'training.personalization': _(u"Training Personalization"),
            u'training.maxprice': _(u"Training Maximum Price"),
            u'participant.age': _(u"Participant Age"),
            u'participant.gender': _(u"Participant Gender"),
            u'participant.occupation': _(u"Participant Occupation"),
            u'investment': _(u"Investment Maximum"),
            u'participant.investment.1': _(u"Participant Investment 1"),
            u'participant.investment.2': _(u"Participant Investment 2"),
            u'participant.investment.3': _(u"Participant Investment 3"),
            u'participant.investment.4': _(u"Participant Investment 4"),
            u'participant.investment.5': _(u"Participant Investment 5"),
            u'price.hometrainer': _(u"Price Hometrainer"),
            u'price.treadmill': _(u"Price Treadmill"),
            u'price.crosstrainer': _(u"Price Crosstrainer"),
            u'price.bike': _(u"Price Bike"),
            u'price.mountainbike': _(u"Price Mountainbike"),
            u'price.trainer': _(u"Price Personal Trainer"),
            u'price.club': _(u"Price Club"),
            u'purchase': _(u"Purchase"),
            u'purchase.comment': _(u"Purchase Comment"),
            u'interest.1': _(u"Interest 1"),
            u'interest.2': _(u"Interest 2"),
            u'email': _(u"E-Mail")}
        return fields
