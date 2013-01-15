import csv
import json
import tempfile
import time

from DateTime import DateTime
from Acquisition import aq_inner
from AccessControl import Unauthorized

from five import grok
from plone import api

from zope.component import getMultiAdapter
from zope.lifecycleevent import modified

from egomotion.sitecontent.surveytool import UnicodeWriter
from egomotion.sitecontent.survey import ISurvey
from egomotion.sitecontent.answer import IAnswer

from egomotion.sitecontent import MessageFactory as _


class SurveyResults(grok.View):
    grok.context(ISurvey)
    grok.require('cmf.ModifyPortalContent')
    grok.name('survey-results')

    def update(self):
        context = aq_inner(self.context)
        self.anonymous = api.user.is_anonymous()
        self.has_answers = self.answers_idx() > 0
        if 'form.buttons.Submit' in self.request:
            self.errors = {}
            form = self.request.form
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            self.exportResults(form)

    def exportResults(self, data):
        """Returns a CSV file with all newsletter subscribers.
        """
        context = aq_inner(self.context)
        now = DateTime()
        timestamp = str(now)
        setattr(context, 'download', timestamp)
        modified(context)
        CSV_HEADER = self.csv_headers()

        # Create CSV file
        filename = tempfile.mktemp()
        file = open(filename, 'wb')
        csvWriter = UnicodeWriter(file,
                                  {'delimiter': ',',
                                   'quotechar': '"',
                                   'quoting': csv.QUOTE_MINIMAL})
        CSV_HEADER_I18N = [self.context.translate(_(x)) for x in CSV_HEADER]
        csvWriter.writerow(CSV_HEADER_I18N)
        export_data = self.prepare_export_data()
        for entry in export_data:
            obj = entry
            csvWriter.writerow([obj.salutation,
                                obj.fullname,
                                obj.email,
                                obj.organization])
        file.close()
        data = open(filename, "r").read()
        prefix = 'surveyresults'
        ext = ''
        name = "%s-%s%s" % (prefix, time.time(), ext)
        cache_control = "must-revalidate, post-check=0, pre-check=0, public"
        # Create response
        response = context.REQUEST.response
        response.addHeader('Content-Disposition',
                           "attachment; filename=%s") % name
        response.addHeader('Content-Type', 'text/csv')
        response.addHeader('Content-Length', "%d" % len(data))
        response.addHeader('Pragma', "no-cache")
        response.addHeader('Cache-Control', cache_control)
        response.addHeader('Expires', "0")

        # Return CSV data
        return data

    def prepare_export_data(self):
        data = {}
        results = self.survey_answers()
        for r in results:
            itemdata = list()
            obj = r.getObject()
            index = obj.participant
            answers = json.loads(obj.answers)
            itemdata.append(answers)
            data[index] = itemdata
        return data

    def get_item_details(self, item):
        answers = json.loads(item.answers)
        mapping = self.survey_data_mappings()
        data = []
        if len(answers) > 0:
            results = answers['survey-state']
            for r in mapping:
                item = {}
                try:
                    item['value'] = results[r]
                except KeyError:
                    item['value'] = _(u"No value given or not callable")
                try:
                    title = mapping[r]
                except KeyError:
                    title = r
                item['title'] = title
                data.append(item)
        return data

    def answers_idx(self):
        answers = self.survey_answers()
        return len(answers)

    def survey_answers(self):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')
        results = catalog(object_provides=IAnswer.__identifier__,
                          path=dict(query='/'.join(context.getPhysicalPath()),
                                    depth=1),
                          sort_on='getObjPositionInParent')
        return results

    def latest_answer(self):
        context = aq_inner(self.context)
        items = context.restrictedTraverse('@@folderListing')(
            portal_type='egomotion.sitecontent.answer',
            sort_on='modified',
            sort_order='reverse')
        return items[0]

    def csv_headers(self):
        HEADER = [_(u"salutation"), _(u"fullname"), _(u"email"),
                  _(u"organization"), ]
        return HEADER

    def survey_data_mappings(self):
        MAP = {
            u'accessory.additional': _(u"Accessory Additional"),
            u'accessory.one': _(u"Accessory One"),
            u'accessory.three': _(u"Accessory Three"),
            u'accessory.two': _(u"Accessory Two"),
            u'benefit.one': _(u"Benefit One"),
            u'benefit.three': _(u"Benefit Three"),
            u'benefit.two': _(u"Benefit Two"),
            u'dislikes.one': _(u"Dislike One"),
            u'dislikes.two': _(u"Dislike Two"),
            u'dislikes.three': _(u"Dislike Three"),
            u'email': _(u"E-Mail"),
            u'favorite1': _(u"Favorite 1"),
            u'favorite1.dislikes.one': _(u"Favorite 1 - Dislike 1"),
            u'favorite1.dislikes.three': _(u"Favorite 1 - Dislike 3"),
            u'favorite1.dislikes.two': _(u"Favorite 1 - Dislike 2"),
            u'favorite1.likes.one': _(u"Favorite 1 - Like 1"),
            u'favorite1.likes.three': _(u"Favorite 1 - Like 3"),
            u'favorite1.likes.two': _(u"Favorite 1 - Like 2"),
            u'favorite2': _(u"Favorite 2"),
            u'favorite2.dislikes.one': _(u"Favorite 2 - Dislike 1"),
            u'favorite2.dislikes.three': _(u"Favorite 2 - Dislike 3"),
            u'favorite2.dislikes.two': _(u"Favorite 2 - Dislike 2"),
            u'favorite2.likes.one': _(u"Favorite 2 - Like 1"),
            u'favorite2.likes.three': _(u"Favorite 2 - Like 3"),
            u'favorite2.likes.two': _(u"Favorite 2 - Like 2"),
            u'favorite3': _(u"Favorite 3"),
            u'favorite3.dislikes.one': _(u"Favorite 3 - Dislike 1"),
            u'favorite3.dislikes.three': _(u"Favorite 3 - Dislike 3"),
            u'favorite3.dislikes.two': _(u"Favorite 3 - Dislike 2"),
            u'favorite3.likes.one': _(u"Favorite 3 - Like 1"),
            u'favorite3.likes.three': _(u"Favorite 3 - Like 3"),
            u'favorite3.likes.two': _(u"Favorite 3 - Like 2"),
            u'functionality.additional': _(u"Functionality Additional"),
            u'functionality.four': _(u"Functionality 4"),
            u'functionality.one': _(u"Functionality 1"),
            u'functionality.three': _(u"Functionality 3"),
            u'functionality.two': _(u"Functionality 2"),
            u'functionality.five': _(u"Functionality 5"),
            u'functionality.six': _(u"Functionality 6"),
            u'functionality.seven': _(u"Functionality 7"),
            u'participant.gender': _(u"Participant Gender"),
            u'participant.investment': _(u"Participant Investment"),
            u'participant.investment.five': _(u"Participant Investment 5"),
            u'participant.investment.four': _(u"Participant Investment 4"),
            u'participant.investment.one': _(u"Participant Investment 1"),
            u'participant.investment.three': _(u"Participant Investment 3"),
            u'participant.investment.two': _(u"Participant Investment 2"),
            u'participant.occupation': _(u"Participant Occupation"),
            u'pid': _(u"Participant ID"),
            u'price.bike': _(u"Price Bike"),
            u'price.crosstrainer': _(u"Price Crosstrainer"),
            u'price.hometrainer': _(u"Price Hometrainer"),
            u'price.mountainbike': _(u"Price Mountainbike"),
            u'price.trainer': _(u"Price Personal Trainer"),
            u'price.treadmill': _(u"Price Treadmill"),
            u'puid': _(u"Participant Code"),
            u'roadwork': _(u"Roadwork"),
            u'training.maxprice': _(u"Training Maximum Price"),
            u'training.monitor': _(u"Training Monitor"),
            u'training.personalization': _(u"Training Personalization"),
            u'trainingresource.effect': _(u"Training Resource Effect"),
            u'trainingresource.eight': _(u"Training Resource 8"),
            u'trainingresource.five': _(u"Training Resource 5"),
            u'trainingresource.four': _(u"Training Resource 4"),
            u'trainingresource.nine': _(u"Training Resource 9"),
            u'trainingresource.one': _(u"Training Resource 1"),
            u'trainingresource.seven': _(u"Training Resource 7"),
            u'trainingresource.six': _(u"Training Resource 6"),
            u'trainingresource.ten': _(u"Training Resource 10"),
            u'trainingresource.three': _(u"Training Resource 3"),
            u'trainingresource.two': _(u"Training Resource 2")}
        return MAP
