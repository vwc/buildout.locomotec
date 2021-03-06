import math
import json
from datetime import datetime
from five import grok
from plone import api
from zope import schema

from Acquisition import aq_inner
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.lifecycleevent import modified
from plone.directives import dexterity, form
from plone.keyring import django_random

from plone.dexterity.utils import createContentInContainer
from plone.app.uuid.utils import uuidToPhysicalPath

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
    clients = schema.List(
        title=_(u"Clients"),
        value_type=schema.TextLine(
            title=_(u"Client"),
        ),
        required=False,
    )
    participants = schema.List(
        title=_(u"Participants"),
        description=_(u"A list of participation UIDs for quick access"),
        value_type=schema.TextLine(
            title=_(u"Participant UID"),
        ),
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
        self.token = self.token_in_session()
        self.locked = self.locked_state_info()
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
            surveydata['pip'] = self.get_client_ip()
            tool = getUtility(ISurveyTool)
            tool.add('survey-state', surveydata)
            session = tool.get()
            current_data = session['survey-state']
            if errorIdx > 0:
                self.errors = formerrors
            else:
                self._processData(current_data)

    def _processData(self, data):
        context = aq_inner(self.context)
        itemdata = {}
        tool = getUtility(ISurveyTool)
        session = tool.get()
        state = session['survey-state']
        if 'puid' not in state:
            code = django_random.get_random_string(length=12)
            state['puid'] = code
            tool.add('survey-state', state)
            survey = tool.get()
        else:
            survey = session
        answers = json.dumps(survey)
        token = django_random.get_random_string(length=24)
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
        #token = django_random.get_random_string(length=24)
        #code = django_random.get_random_string(length=12)
        #results = answers['survey-state']
        token_info = {}
        token_info['idx'] = index
        token_info['token'] = token
        token_info['code'] = code
        token_info['timestamp'] = timestamp
        token_info['ip'] = state['pip']
        tool.add('token', token_info)
        uid = IUUID(item)
        stored_info = self.update_survey_information(uid)
        if stored_info:
            setattr(context, 'clients', stored_info['clients'])
            setattr(context, 'participants', stored_info['participants'])
            modified(context)
        url = context.absolute_url()
        base_url = url + '/@@survey-save?uuid=' + uid
        next_url = base_url + '&token=' + token
        return self.request.response.redirect(next_url)

    def update_survey_information(self, uid):
        context = aq_inner(self.context)
        info = {}
        clients = getattr(context, 'clients')
        participants = getattr(context, 'participants')
        if participants is None:
            updated_participants = []
            updated_participants.append(uid)
        else:
            if uid not in participants:
                participants.append(uid)
            updated_participants = participants
        info['participants'] = updated_participants
        client_ip = self.get_client_ip()
        if clients is None:
            updated_clients = list()
            updated_clients.append(client_ip)
        else:
            if client_ip not in clients:
                clients.append(client_ip)
            updated_clients = clients
        info['clients'] = updated_clients
        return info

    def locked_state_info(self):
        context = aq_inner(self.context)
        client_ip = self.get_client_ip()
        locked = False
        if context.clients:
            if client_ip in context.clients and client_ip != '127.0.0.1':
                locked = True
            elif self.token is True:
                locked = True
            else:
                locked = False
        return locked

    def token_in_session(self):
        tool = getUtility(ISurveyTool)
        token = False
        try:
            session = tool.get()
        except KeyError:
            session = None
        if session is not None and 'token' in session:
            token = True
        return token

    def generate_index(self):
        context = aq_inner(self.context)
        items = getattr(context, 'participants', list())
        if items is not None:
            count = len(items)
            new_index = count + 1
        else:
            new_index = 1
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

    def get_client_ip(self):
        request = self.request
        if "HTTP_X_FORWARDED_FOR" in request.environ:
            ip = request.environ['HTTP_X_FORWARDED_FOR']
        elif "HTTP_HOST" in request.environ:
            ip = request.environ['REMOTE_ADDR']
        else:
            ip = None
        return ip


class SurveySave(grok.View):
    grok.context(ISurvey)
    grok.require('zope2.View')
    grok.name('survey-save')

    def render(self):
        context = aq_inner(self.context)
        base_url = context.absolute_url()
        context = aq_inner(self.context)
        uuid = self.request.get('uuid', None)
        query_token = self.request.get('token', None)
        tool = getUtility(ISurveyTool)
        session = tool.get()
        marker = True
        if 'token' in session:
            tokeninfo = session['token']
            token = tokeninfo['token']
            if token == query_token:
                tool.remove('survey-state')
                marker = False
        if marker is False:
            next_url = base_url + '/@@survey-saved?uuid=' + uuid
        else:
            next_url = base_url + '/@@survey-invalid'
        return self.request.response.redirect(next_url)

    def resolve_item(self, uid):
        context = aq_inner(self.context)
        item_path = uuidToPhysicalPath(uid)
        item = context.unrestrictedTraverse(item_path)
        return item


class SurveySaved(grok.View):
    grok.context(ISurvey)
    grok.require('zope2.View')
    grok.name('survey-saved')

    def update(self):
        self.uuid = self.request.get('uuid', None)
        self.token = self.get_token_info()
        self.initial = False

    def get_token_info(self):
        tool = getUtility(ISurveyTool)
        session = tool.get()
        token_info = session['token']
        return token_info

    def set_participation_marker(self):
        context = aq_inner(self.context)
        uuid = self.request.get('uuid', None)
        catalog = api.portal.get_tool(name='portal_catalog')
        results = catalog.unrestrictedSearchResults(UID=uuid)
        tool = getUtility(ISurveyTool)
        session = tool.get()
        marker = True
        owner = context.getWrappedOwner()
        sm = getSecurityManager()
        newSecurityManager(self.request, owner)
        try:
            item = results[0].getObject()
            if 'token' in session:
                token = session['token']
                if token == self.token:
                    state = {}
                    data = json.loads(item.answers)
                    results = data['survey-state']
                    state['idx'] = results['puid']
                    state['token'] = token
                    state['ip'] = results['pip']
                    tool.add('token', state)
                    tool.remove('survey-state')
                    marker = False
                    self.initial = True
        finally:
            setSecurityManager(sm)
        return marker

    def item_info(self):
        context = aq_inner(self.context)
        uuid = self.request.get('uuid', None)
        if uuid is not None:
            catalog = api.portal.get_tool(name='portal_catalog')
            results = catalog.unrestrictedSearchResults(UID=uuid)
            owner = context.getWrappedOwner()
            sm = getSecurityManager()
            newSecurityManager(self.request, owner)
            try:
                item = results[0].getObject()
                info = {}
                answers = json.loads(item.answers)
                results = answers['survey-state']
                info['code'] = results['puid']
                info['index'] = item.participant
                info['marker'] = self.marker
                return info
            finally:
                setSecurityManager(sm)

    def resolve_item(self, uid):
        context = aq_inner(self.context)
        item_path = uuidToPhysicalPath(uid)
        item = context.unrestrictedTraverse(item_path)
        return item


class SurveyInvalid(grok.View):
    grok.context(ISurvey)
    grok.require('zope2.View')
    grok.name('survey-invalid')


class AutosaveSurvey(grok.View):
    grok.context(ISurvey)
    grok.require('zope2.View')
    grok.name('autosave-survey')

    def update(self):
        self.query = self.request["QUERY_STRING"]

    def render(self):
        form = self.request.form
        data = {}
        unwanted = ('_authenticator', 'form.button.Submit')
        for value in form:
            if value not in unwanted:
                data[value] = form[value]
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
        puid = django_random.get_random_string()
        if not self.has_active_session():
            data['puid'] = puid
        else:
            session = tool.get()
            try:
                current_session = session[name]
                saved_puid = current_session['puid']
                data['puid'] = saved_puid
            except KeyError:
                data['puid'] = puid
        data['pip'] = client_ip
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


class SurveySessionInfo(grok.View):
    grok.context(ISurvey)
    grok.require('cmf.ModifyPortalContent')
    grok.name('survey-session-info')

    def render(self):
        tool = getUtility(ISurveyTool)
        data = tool.get()
        return json.dumps(data)


class ClearSurveySession(grok.View):
    grok.context(ISurvey)
    grok.require('zope2.View')
    grok.name('survey-session-clear')

    def render(self):
        portal = api.portal.get()
        tool = getUtility(ISurveyTool)
        tool.destroy()
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

    def get_client_ip(self):
        request = self.request
        if "HTTP_X_FORWARDED_FOR" in request.environ:
            ip = request.environ['HTTP_X_FORWARDED_FOR']
        elif "HTTP_HOST" in request.environ:
            ip = request.environ['REMOTE_ADDR']
        else:
            ip = None
        return ip
