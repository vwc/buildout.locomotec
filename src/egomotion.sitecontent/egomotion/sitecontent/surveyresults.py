import csv
import json
import time

from StringIO import StringIO
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
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            now = DateTime()
            timestamp = str(now)
            setattr(context, 'download', timestamp)
            modified(context)
            out = StringIO()
            writer = UnicodeWriter(out,
                                   {'delimiter': ',',
                                    'quotechar': '"',
                                    'quoting': csv.QUOTE_MINIMAL})
            #writer = csv.writer(out)
            CSV_HEADER = self.csv_headers()
            # Create CSV file
            CSV_HEADER_I18N = [(self.context.translate(_(x))).encode('utf-8')
                               for x in CSV_HEADER]
            writer.writerow(CSV_HEADER_I18N)
            export_data = self.prepare_export_data()
            cleaned_data = self.prettify_export_data(export_data)
            for entry in cleaned_data:
                result = cleaned_data[entry]
                answers = []
                for r in result:
                    answers.append(result[r])
                writer.writerow(answers)
            data = out.getvalue()
            prefix = 'surveyresults'
            ext = ''
            name = "%s-%s%s" % (prefix, time.time(), ext)
            c_control = "must-revalidate, post-check=0, pre-check=0, public"
            disposition = "attachment; filename=%s" % name
            # Create response
            response = self.request.response
            response.setHeader('Content-Disposition', disposition)
            response.setHeader('Content-Type', 'text/csv')
            response.setHeader('Content-Length', "%d" % len(data))
            response.setHeader('Pragma', "no-cache")
            response.setHeader('Cache-Control', c_control)
            response.setHeader('Expires', "0")
            # Return CSV data
            return data

    def prepare_export_data(self):
        data = {}
        results = self.survey_answers()
        for r in results:
            obj = r.getObject()
            index = obj.participant
            answers = json.loads(obj.answers)
            if 'survey-state' in answers:
                itemdata = answers['survey-state']
            else:
                itemdata = {}
            data[index] = itemdata
        return data

    def prettify_export_data(self, data):
        cleaned = {}
        for x in data:
            index = x
            results = data[x]
            if len(results) > 0:
                item = {}
                for r in results:
                    cleaned_value = self.prettify_value(r, results[r])
                    item[r] = cleaned_value
                cleaned[index] = item
        return cleaned

    def prettify_value(self, name, value):
        try:
            token = name.split('.')
        except:
            token = name
        if name in self.survey_array_fields():
            import pdb; pdb.set_trace( )
        return value

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
        fileheaders = []
        mappings = self.survey_data_mappings()
        for entry in mappings:
            header = mappings[entry]
            fileheaders.append(header)
        return fileheaders

    def survey_array_fields(self):
        fields = ('interest', 'participant.investment', 'functionality',
                  'purchase', 'accessory', 'trainingresource', 'benefit')
        return fields

    def survey_data_mappings(self):
        MAP = {
            u'pid': _(u"Participant ID"),
            u'puid': _(u"Participant Code"),
            u'email': _(u"E-Mail"),
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
            u'frequency': _(u"Training Frequency"),
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
            u'price.bike': _(u"Price Bike"),
            u'price.crosstrainer': _(u"Price Crosstrainer"),
            u'price.hometrainer': _(u"Price Hometrainer"),
            u'price.mountainbike': _(u"Price Mountainbike"),
            u'price.trainer': _(u"Price Personal Trainer"),
            u'price.treadmill': _(u"Price Treadmill"),
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

    def field_list(self):
        fields = {
            'functionality.additional': 'Funktion Freitext',
            'interest': ['interest.1', 'interest.2'],
            'participant.occupation': 'participant.occupation10',
            'price.bike': 'option1',
            'favorite2.dislikes.three': 'Disike 2-3',
            'favorite1.dislikes.three': 'Disike 1-3',
            'favorite3.dislikes.two': 'Disike 3-2',
            'trainingresource.effect': 'trainingresource.effect.2',
            'frequency': 'frequency.3',
            'favorite1': '1',
            'favorite3': '3',
            'favorite2': '2',
            'favorite3.likes.two': 'Like 3-2',
            'favorite3.dislikes.three': 'Disike 3-3',
            'training.maxprice': 'option1',
            'participant.investment': ['100', 'participant.investment.1',
                                       'participant.investment.2',
                                       'participant.investment.3',
                                       'participant.investment.4',
                                       'participant.investment.5'],
            'training.personalization': 'very important',
            'functionality': ['functionality.1', 'functionality.2',
                              'functionality.3', 'functionality.4',
                              'functionality.5', 'functionality.6',
                              'functionality.7'],
            '_authenticator': 'f23699363177c25c8b4d7a0a77b4806be52668d3',
            'dislikes.one': 'Hate 1',
            'favorite1.likes.two': 'Like 1-2',
            'accessory.additional': 'Zubeh\xc3\xb6r Freitext',
            'dislikes.three': 'Hate 3',
            'email': 'test@example.tld',
            'favorite1.likes.one': 'Like 1-1',
            'favorite1.dislikes.one': 'Disike 1-1',
            'participant.gender': 'option1',
            'purchase': ['purchase.1', 'purchase.2', 'purchase.3'],
            'favorite3.likes.three': 'Like 3-3',
            'favorite3.dislikes.one': 'Disike 3-1',
            'favorite3.likes.one': 'Like 3-1',
            'accessory': ['accessory.1', 'accessory.2', 'accessory.3'],
            'price.crosstrainer': 'option1',
            'favorite2.likes.two': 'Like 2-2',
            'price.hometrainer': 'option1',
            'favorite1.likes.three': 'Like 1-3',
            'favorite2.dislikes.two': 'Disike 2-2',
            'favorite2.likes.three': 'Like 2-3',
            'price.club': 'option1',
            'trainingresource': ['trainingresource.1', 'trainingresource.2',
                                 'trainingresource.3', 'trainingresource.4',
                                 'trainingresource.5', 'trainingresource.6',
                                 'trainingresource.7', 'trainingresource.8',
                                 'trainingresource.9', 'trainingresource.10'],
            'price.mountainbike': 'option1',
            'trainingresource.additional': 'Hilfsmittel Freitext',
            'training.monitor': 'good',
            'price.trainer': 'option1',
            'favorite2.dislikes.one': 'Disike 2-1',
            'favorite2.likes.one': 'Like 2-1',
            'benefit': ['benefit.1', 'benefit.2', 'benefit.3'],
            'price.treadmill': 'option1',
            'favorite1.dislikes.two': 'Disike 1-2',
            'form.buttons.Submit': '',
            'roadwork': 'roadwork.1'}
        return fields
