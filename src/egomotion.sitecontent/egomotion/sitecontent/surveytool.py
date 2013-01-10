from five import grok
from plone import api

from zope.interface import Interface
from zope.globalrequest import getRequest
from zope.component.hooks import getSite

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
