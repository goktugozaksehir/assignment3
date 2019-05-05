from google.appengine.ext import ndb
from tweets import tweets

class MyUser(ndb.Model):
    username= ndb.StringProperty()
    name=ndb.StringProperty()
    bio=ndb.StringProperty()
    email_address = ndb.StringProperty()
    tweet=ndb.StructuredProperty(tweets, repeated = True)
    follower=ndb.StringProperty(repeated = True)
    following=ndb.StringProperty(repeated = True)