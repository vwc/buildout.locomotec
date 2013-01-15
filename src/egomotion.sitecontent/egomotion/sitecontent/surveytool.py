import csv
import codecs
import cStringIO
from five import grok

from zope.interface import Interface
from zope.globalrequest import getRequest

from collective.beaker.interfaces import ISession

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
