__author__ = 'hstrauss'

from google.appengine.ext import ndb

#The concept class capture the general concepts of things we care about (bubbls, media, people)
class AlertRequests(ndb.Model):
    #: Creation date.
    created = ndb.DateTimeProperty(auto_now_add=True)
    #: Modification date.
    updated = ndb.DateTimeProperty(auto_now=True)
    #email
    email = ndb.StringProperty()
    #user agent string
    uastring = ndb.StringProperty()
    #requesting ip
    ip = ndb.StringProperty()

    @classmethod
    def get_concept_by_name(cls, concept_name):
        return cls.query(cls.name == concept_name).fetch()

    @classmethod
    def get_all_emails(cls):
        return cls.query().fetch()

    @classmethod
    def get_email_by_email(cls, email):
        return cls.query(cls.email == email).fetch()