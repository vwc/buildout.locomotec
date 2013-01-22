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
            CSV_HEADER_I18N = [self.context.translate(_(x))
                               for x in CSV_HEADER]
            writer.writerow(CSV_HEADER_I18N)
            export_data = self.prepare_export_data()
            for entry in export_data:
                result = export_data[entry]
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

    def csv_preview(self):
        out = StringIO()
        writer = UnicodeWriter(out,
                               {'delimiter': ',',
                                'quotechar': '"',
                                'quoting': csv.QUOTE_MINIMAL})
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
            for r in result:
                answers.append(result[r])
            writer.writerow(answers)
        data = out.getvalue()
        return data

    def prepare_export_data(self):
        data = {}
        fieldorder = self.fields_ordered()
        arrays = self.fields_containing_arrays()
        selections = self.fields_containing_selections()
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
                    values = itemdata[item]
                    for token in arrays[item]:
                        if token in values:
                            flattened[token] = '1'
                        else:
                            flattened[token] = '0'
                elif item in selections:
                    value = itemdata[item]
                    splitted_value = value.split('.')
                    flattened[item] = splitted_value[-1]
                elif item == 'pid':
                    flattened[item] = str(index)
                else:
                    try:
                        flattened[item] = str(itemdata[item])
                    except KeyError:
                        flattened[item] = ''
            data[index] = flattened
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
        fileheaders = []
        order = self.fields_ordered()
        titles = self.field_titles()
        for idx in order:
            header = titles[idx]
            fileheaders.append(header)
        return fileheaders

    def fields_containing_arrays(self):
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
            'purchase': ('purchase.1', 'purchase.2', 'purchase.3'),
            'interest': ('interest.1', 'interest.2'),
        }
        return fields

    def fields_containing_selections(self):
        fields = (
            'participant.occupation', 'participant.gender', 'roadwork',
            'training.monitor', 'trainingresource.effect',
            'training.maxprice', 'training.personalization',
            'price.crosstrainer', 'price.bike', 'price.hometrainer',
            'price.club', 'price.trainer', 'price.treadmill',
            'price.mountainbike'
        )
        return fields

    def fields_ordered(self):
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
            'purchase.1',
            'purchase.2',
            'purchase.3',
            'purchase.comment',
            'interest.1',
            'interest.2',
            'email')
        return fields

    def field_titles(self):
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
            u'purchase.1': _(u"Purchase 1"),
            u'purchase.2': _(u"Purchase 2"),
            u'purchase.3': _(u"Purchase 3"),
            u'purchase.comment': _(u"Purchase Comment"),
            u'interest.1': _(u"Interest 1"),
            u'interest.2': _(u"Interest 2"),
            u'email': _(u"E-Mail")}
        return fields
