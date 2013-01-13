import csv
import json
import tempfile
import time

from Acquisition import aq_inner
from AccessControl import Unauthorized

from five import grok
from plone import api

from zope.component import getMultiAdapter

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

    def exportResults(self):
        """Returns a CSV file with all newsletter subscribers.
        """
        context = aq_inner(self.context)
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
            index = r.participant
            answers = json.loads(r.answers)
            itemdata.append(answers)
            data[index] = itemdata
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

    def csv_headers(self):
        HEADER = [_(u"salutation"), _(u"fullname"), _(u"email"),
                  _(u"organization"), ]
        return HEADER
