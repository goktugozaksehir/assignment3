from google.appengine.ext import ndb

class tweets(ndb.Model):
    username=ndb.StringProperty()
    tweet=ndb.StringProperty()
    image=ndb.BlobKeyProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)