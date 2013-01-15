import math
import json
from datetime import datetime
from Acquisition import aq_inner
from AccessControl import Unauthorized
from five import grok
from plone import api
from zope import schema

from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.lifecycleevent import modified
from plone.directives import dexterity, form
from plone.keyring import django_random

from plone.dexterity.utils import createContentInContainer
from plone.app.uuid.utils import uuidToObject

from plone.uuid.interfaces import IUUID
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.app.blob.interfaces import IATBlobImage

from egomotion.sitecontent.surveytool import ISurveyTool
from egomotion.sitecontent.answer import IAnswer

from egomotion.sitecontent import MessageFactory as _


class ISurvey(form.Schema, IImageScaleTraversable):
    """
    A folderish survey holding participant objects
    """
    download = schema.TextLine(
        title=_(u"Last Download"),
        required=False,
    )


class Survey(dexterity.Container):
    grok.implements(ISurvey)


class View(grok.View):
    grok.context(ISurvey)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        context = aq_inner(self.context)
        self.anonymous = api.user.is_anonymous()
        self.has_images = len(self.contained_images()) > 0
        unwanted = ('_authenticator', 'form.button.Submit')
        if 'form.buttons.Submit' in self.request:
            self.errors = {}
            form = self.request.form
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            surveydata = {}
            formerrors = {}
            errorIdx = 0
            for item in form:
                if item not in unwanted:
                    surveydata[item] = form[item]
            if errorIdx > 0:
                self.errors = formerrors
            else:
                self._processData(surveydata)

    def _processData(self, data):
        context = aq_inner(self.context)
        itemdata = {}
        tool = getUtility(ISurveyTool)
        survey_state = tool.get()
        answers = json.dumps(survey_state)
        now = datetime.now()
        timestamp = api.portal.get_localized_time(datetime=now)
        index = self.generate_index()
        new_title = str(index) + ' - ' + timestamp
        itemdata['title'] = new_title
        container = context
        item = createContentInContainer(
            container,
            'egomotion.sitecontent.answer',
            checkConstraints=False, **itemdata)
        setattr(item, 'answers', answers)
        setattr(item, 'participant', index)
        modified(item)
        item.reindexObject(idxs='modified')
        uid = IUUID(item)
        next_url = context.absolute_url() + '/@@survey-saved?uuid=' + uid
        return self.request.response.redirect(next_url)

    def generate_index(self):
        items = self.contained_answers()
        count = len(items)
        new_index = count + 1
        return new_index

    def contained_answers(self):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')
        results = catalog(object_provides=IAnswer.__identifier__,
                          path=dict(query='/'.join(context.getPhysicalPath()),
                                    depth=1))
        return results

    def default_value(self, fieldname):
        tool = getUtility(ISurveyTool)
        value = ''
        try:
            state = tool.get()
        except KeyError:
            state = None
        if state is not None:
            try:
                data = state['survey-state']
                if fieldname in data:
                    value = data[fieldname]
            except KeyError:
                value = ''
        return value

    def contained_images(self):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')
        results = catalog(object_provides=IATBlobImage.__identifier__,
                          path=dict(query='/'.join(context.getPhysicalPath()),
                                    depth=1),
                          sort_on='getObjPositionInParent')
        return results

    def image_list(self):
        images = self.contained_images()
        data = []
        for item in images:
            info = {}
            info['title'] = item.Title
            thumb = self.getImageTag(item, scalename='thumb')
            info['thumb_url'] = thumb['url']
            info['thumb_width'] = thumb['width']
            info['thumb_height'] = thumb['height']
            original = self.getImageTag(item, scalename='original')
            info['original_url'] = original['url']
            info['original_width'] = original['width']
            info['original_height'] = original['height']
            data.append(info)
        return data

    def image_matrix(self):
        items = self.image_list()
        count = len(items)
        rowcount = count / 5.0
        rows = math.ceil(rowcount)
        matrix = []
        for i in range(int(rows)):
            row = []
            for j in range(5):
                index = 5 * i + j
                if index <= int(count - 1):
                    cell = {}
                    cell['item'] = items[index]
                    row.append(cell)
            matrix.append(row)
        return matrix

    def getImageTag(self, item, scalename):
        obj = item.getObject()
        scales = getMultiAdapter((obj, self.request), name='images')
        if scalename == 'thumb':
            scale = scales.scale('image', width=200, height=200)
        else:
            scale = scales.scale('image', width=400, height=400)
        item = {}
        if scale is not None:
            item['url'] = scale.url
            item['width'] = scale.width
            item['height'] = scale.height
        return item


class AutosaveSurvey(grok.View):
    grok.context(ISurvey)
    grok.require('zope2.View')
    grok.name('autosave-survey')

    def update(self):
        self.query = self.request["QUERY_STRING"]

    def render(self):
        data = self.request.form
        tool = getUtility(ISurveyTool)
        now = datetime.now()
        timestamp = api.portal.get_localized_time(datetime=now,
                                                  long_format=True)
        client_ip = self.get_client_ip()
        if client_ip is None:
            userinfo = timestamp
        else:
            userinfo = client_ip + '-' + timestamp
        name = 'survey-state'
        if not self.has_active_session():
            puid = django_random.get_random_string()
            data['puid'] = puid
        else:
            session = tool.get()
            current_session = session[name]
            saved_puid = current_session['puid']
            data['puid'] = saved_puid
        data['pid'] = client_ip
        tool.add(name, data)
        time_info = _(u"Autosave %s") % userinfo
        msg = _(u"Survey state automatically saved")
        results = {'success': True,
                   'message': msg,
                   'timestamp': time_info
                   }
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(results)

    def has_active_session(self):
        active = False
        try:
            session = self.surveytool()
        except KeyError:
            session = None
        if session is not None:
            active = True
        return active

    def surveytool(self):
        tool = getUtility(ISurveyTool)
        return tool.get()

    def get_client_ip(self):
        request = self.request
        if "HTTP_X_FORWARDED_FOR" in request.environ:
            ip = request.environ['HTTP_X_FORWARDED_FOR']
        elif "HTTP_HOST" in request.environ:
            ip = request.environ['REMOTE_ADDR']
        else:
            ip = None
        return ip


class SurveySaved(grok.View):
    grok.context(ISurvey)
    grok.require('zope2.View')
    grok.name('survey-saved')

    def item_info(self):
        item = self.resolve_item()
        info = {}
        answers = json.loads(item.answers)
        results = answers['survey-state']
        info['code'] = results['puid']
        info['index'] = item.participant
        return info

    def resolve_item(self):
        uuid = self.request.get('uuid', None)
        return uuidToObject(uuid)


class ClearSurveySession(grok.View):
    grok.context(ISurvey)
    grok.require('cmf.ModifyPortalContent')
    grok.name('survey-session-clear')

    def render(self):
        tool = getUtility(ISurveyTool)
        portal = api.portal.get()
        tool.destroy(portal)
        portal_url = portal.absolute_url()
        api.portal.show_message(
            message=_(u"Session cleared"), request=self.request)
        return self.request.response.redirect(portal_url)


class SelectFavorite(grok.View):
    grok.context(ISurvey)
    grok.require('zope2.View')
    grok.name('favorite-select')

    def survey_state(self):
        tool = getUtility(ISurveyTool)
        return tool.get()
