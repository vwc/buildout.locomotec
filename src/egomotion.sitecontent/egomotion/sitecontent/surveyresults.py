import csv
import json

from StringIO import StringIO
from DateTime import DateTime
from Acquisition import aq_inner
from AccessControl import Unauthorized

from five import grok
from plone import api

from zope.component import getMultiAdapter
from zope.lifecycleevent import modified

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
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            now = DateTime()
            timestamp = str(now)
            setattr(context, 'download', timestamp)
            modified(context)
            base_url = context.absolute_url()
            next_url = base_url + '/@@export-survey-results'
            return self.request.response.redirect(next_url)

    def csv_preview(self):
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
        return data

    def prepare_export_data(self):
        data = {}
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
            for item in survey_fields_datacollection():
                if item in arrays:
                    try:
                        values = itemdata[item]
                    except KeyError:
                        values = ''
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

    def pretty_title(self, key):
        pretty_titles = self.field_titles()
        return pretty_titles[key]

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
        fileheaders = []
        order = survey_fields_ordered()
        titles = survey_fields_i18n()
        for idx in order:
            header = titles[idx]
            fileheaders.append(header)
        return fileheaders
