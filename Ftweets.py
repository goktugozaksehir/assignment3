import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from user import MyUser
from tweets import tweets

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True
)

class ATweet(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curuser=users.get_current_user()
        myuser_key = ndb.Key('MyUser', curuser.user_id())
        myuser = myuser_key.get()
        tweet=self.request.get('tweet')
        img= None
        if self.get_uploads():
            upload = self.get_uploads()[0] 
            blobinfo = blobstore.BlobInfo(upload.key())
            img=upload.key()
        newtweet=tweets(username=myuser.username,tweet=tweet,image=img)
        myuser.tweet.append(newtweet)
        myuser.put()
        template_values = {
            'myuser': myuser
        }
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.redirect('/')

class ETweet(webapp2.RequestHandler):
    def get(self,param):
        self.response.headers['Content-Type'] = 'text/html'
        curuser=users.get_current_user()
        myuser_key = ndb.Key('MyUser', curuser.user_id())
        myuser = myuser_key.get()
        sup=-99
        getdate=str(param)
        for forsup,tweet in enumerate(myuser.tweet):
            if str(tweet.date)==getdate:
                sup=forsup
                break
        suptweet=myuser.tweet[sup]        
        template_values = {
            'myuser' : myuser,
            'tweet' : suptweet,
            'tweetnum' : sup           
        }
        template = JINJA_ENVIRONMENT.get_template('edittweet.html')
        self.response.write(template.render(template_values))
    
    def post(self, param):
        self.response.headers['Content-Type'] = 'text/html'
        curuser=users.get_current_user()
        myuser_key = ndb.Key('MyUser', curuser.user_id())
        myuser = myuser_key.get()
        sup=int(param)
        suptweet= self.request.get('tweet')
        myuser.tweet[sup].tweet = suptweet
        myuser.put()
        self.redirect('/profile') 

class DTweet(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curuser=users.get_current_user()
        myuser_key = ndb.Key('MyUser', curuser.user_id())
        myuser = myuser_key.get()
        sup=-99
        getdate=self.request.get('date')
        for forsup,tweet in enumerate(myuser.tweet):
            if str(tweet.date)==str(getdate):
                sup=forsup
                break

        del myuser.tweet[sup]
        myuser.put()                
        self.redirect('/profile')

         