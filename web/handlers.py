__author__ = 'hstrauss'

import webapp2
from webapp2_extras import jinja2
import json

from google.appengine.api import urlfetch

from models import *

def jinja2_factory(app):
    j = jinja2.Jinja2(app)
    j.environment.filters.update({
        # Set filters.
        # ...
    })
    j.environment.globals.update({
        # Set global variables.
        'uri_for': webapp2.uri_for,
        'getattr': getattr,
        'str': str,
        })
    j.environment.tests.update({
        # Set test.
        # ...
    })
    return j

def get_cookies(request):
    cookies = {}
    raw_cookies = request.headers.get("Cookie")
    if raw_cookies:
        for cookie in raw_cookies.split(";"):
            name, value = cookie.split("=")
            cookies[name] = value
    return cookies

class BaseHandler(webapp2.RequestHandler):
    """
        BaseHandler for all requests

        Holds the auth and session properties so they
        are reachable for all requests
    """

    def __init__(self, request, response):
        """ Override the initialiser in order to set the language.
        """
        self.initialize(request, response)

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(factory=jinja2_factory, app=self.app)

    def render_template(self, filename, **kwargs):

        # make all self.view variables available in jinja2 templates
        if hasattr(self, 'view'):
            kwargs.update(self.view.__dict__)

        # set or overwrite special vars for jinja templates
        kwargs.update({
            'google_analytics_domain': self.app.config.get('google_analytics_domain'),
            'google_analytics_code': self.app.config.get('google_analytics_code'),
            'app_name': self.app.config.get('app_name'),
            'url': self.request.url,
            'path': self.request.path,
            'query_string': self.request.query_string,
            'enable_federated_login': self.app.config.get('enable_federated_login'),
        })
        kwargs.update()
        if hasattr(self, 'form'):
            kwargs['form'] = self.form

        self.response.headers.add_header('X-UA-Compatible', 'IE=Edge,chrome=1')
        self.response.write(self.jinja2.render_template(filename, **kwargs))

class AddEmailAlertHandler(BaseHandler):
    def post(self):
        self.return_json ={}

        self.email = self.request.get('email')
        self.uastring=self.request.user_agent
        self.ip=self.request.remote_addr

        user_email = AlertRequests.get_email_by_email(self.email)



        #Add to Google Datastore
        if len(user_email) == 0:
            new_beta_signup = AlertRequests()

            new_beta_signup.email = self.email
            new_beta_signup.uastring = self.uastring
            new_beta_signup.ip = self.ip

            new_beta_signup_key = new_beta_signup.put()

            #Add to MailChimp
            posts_url = "http://us7.api.mailchimp.com/1.3/?method=listSubscribe&apikey=%s&id=62b491e9f9&email_address=%s" % (self.app.config.get('mailchimp_api_key'), self.email)

            result = urlfetch.fetch(url=posts_url, method=urlfetch.GET)

            if result.status_code == 200:
                out_json = json.loads(result.content)
                self.return_json['message'] = "successfully added"
                self.return_json['add_id'] = new_beta_signup_key.id()
                self.return_json['stat_code'] = 0
                self.response.set_cookie('signup', 'yes', path='/', domain='localhost')

            else:
                self.return_json['message'] = "error"
                self.return_json['stat_code'] = 1

        else:
            self.return_json['message'] = "email_exists"
            self.return_json['stat_code'] = 2


        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(self.return_json))


class HomeRequestHandler(BaseHandler):
    """
    Handler to show the home page
    """

    def get(self):
        """ Returns a simple HTML form for home """
        cookies = get_cookies(self.request)
        try:
            if cookies['signup']=='yes':
                params = {}
        except:
            params = {}
        return self.render_template('base.html', **params)