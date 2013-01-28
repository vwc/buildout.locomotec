import csv
import json
import time

from StringIO import StringIO
from Acquisition import aq_inner

from five import grok
from plone import api

from Products.CMFPlone.utils import safe_unicode

from egomotion.sitecontent.surveytool import UnicodeWriter

from egomotion.sitecontent.surveytool import survey_fields_ordered
from egomotion.sitecontent.surveytool import survey_fields_datacollection
from egomotion.sitecontent.surveytool import survey_fields_select
from egomotion.sitecontent.surveytool import survey_fields_multiselect
from egomotion.sitecontent.surveytool import survey_fields_i18n

from egomotion.sitecontent.survey import ISurvey
from egomotion.sitecontent.answer import IAnswer

from egomotion.sitecontent import MessageFactory as _


class ExportSurveyResults(grok.View):
    grok.context(ISurvey)
    grok.require('cmf.ModifyPortalContent')
    grok.name('export-survey-results')

    def update(self):
        self.anonymous = api.user.is_anonymous()

    def render(self):
        out = StringIO()
        #writer = UnicodeWriter(out,
        #                       {'delimiter': ';',
        #                        'quotechar': '"',
        #                        'quoting': csv.QUOTE_ALL})
        writer = UnicodeWriter(out, delimiter=';', quoting=csv.QUOTE_ALL)
        #writer = csv.writer(out)
        CSV_HEADER = self.csv_headers()
        # Create CSV file
        CSV_HEADER_I18N = [self.context.translate(_(x))
                           for x in CSV_HEADER]
        writer.writerow(CSV_HEADER_I18N)
        export_data = self.prepare_export_data()
        for entry in export_data:
            result = export_data[entry]
            answers = []
            for r in survey_fields_ordered():
                value = result[r]
                answers.append(value.decode('utf-8'))
            writer.writerow(answers)
        data = out.getvalue()
        prefix = 'surveyresults'
        timemarker = int(round(time.time() * 1000))
        ext = '.csv'
        filename = "%s-%s%s" % (prefix, timemarker, ext)
        c_control = "must-revalidate, post-check=0, pre-check=0, public"
        # Create response
        self.request.response.setHeader('Content-Length', "%d" % len(data))
        self.request.response.setHeader('Pragma', "no-cache")
        self.request.response.setHeader('Cache-Control', c_control)
        self.request.response.setHeader('Expires', "0")
        # Return CSV data
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader('Content-Disposition',
                                        'attachment; filename=%s'
                                        % filename)
        return out.getvalue()

    def prepare_export_data(self):
        data = {}
        fieldorder = survey_fields_datacollection()
        arrays = survey_fields_multiselect()
        selections = survey_fields_select()
        results = self.survey_answers()
        for r in results:
            obj = r.getObject()
            index = obj.participant
            answers = json.loads(obj.answers)
            if 'survey-state' in answers:
                itemdata = answers['survey-state']
            else:
                itemdata = {}
            flattened = {}
            for item in fieldorder:
                if item in arrays:
                    try:
                        values = itemdata[item]
                    except KeyError:
                        value = ''
                    for token in arrays[item]:
                        if token in values:
                            flattened[token] = '1'
                        else:
                            flattened[token] = '0'
                elif item in selections:
                    try:
                        value = itemdata[item]
                    except KeyError:
                        value = ''
                    splitted_value = value.split('.')
                    flattened[item] = splitted_value[-1]
                elif item == 'pid':
                    flattened[item] = str(index)
                else:
                    try:
                        value = safe_unicode(itemdata[item]).encode('utf-8')
                        flattened[item] = str(value)
                    except KeyError:
                        flattened[item] = ''
            data[index] = flattened
        return data

    def survey_answers(self):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')
        results = catalog(object_provides=IAnswer.__identifier__,
                          path=dict(query='/'.join(context.getPhysicalPath()),
                                    depth=1),
                          sort_on='getObjPositionInParent')
        return results

    def csv_headers(self):
        fileheaders = []
        order = survey_fields_ordered()
        titles = survey_fields_i18n()
        for idx in order:
            header = titles[idx]
            fileheaders.append(header)
        return fileheaders
