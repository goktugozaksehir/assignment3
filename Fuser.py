import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images
import os
from user import MyUser
from tweets import *

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class SUser(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        user = users.get_current_user()
        myuser_key = ndb.Key('MyUser', user.user_id())
        myuser = myuser_key.get()
        template_values= {
            'user' : user,
            'myuser' : myuser
        }
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render(template_values))
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        myuser=users.get_current_user()
        newuser=None
        username=None
        username=self.request.get('username')
        cntrluser=MyUser.query(MyUser.username==username).fetch()
        if not cntrluser:
            newuser=MyUser(id=myuser.user_id(),username=username,email_address=myuser.email())
            newuser.put()
            template=JINJA_ENVIRONMENT.get_template('profile.html')
        else:
            template = JINJA_ENVIRONMENT.get_template('login.html')
        numoftweet=0
        template_values = {
            'myuser': myuser,
            'numtweets': numoftweet
        }
        self.response.write(template.render(template_values))

class UUser(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        curuser=users.get_current_user()
        myuser_key = ndb.Key('MyUser', curuser.user_id())
        myuser = myuser_key.get()
        numtweet=len(myuser.tweet)
        numoffollower=len(myuser.follower)
        numoffollowing=len(myuser.following) 
        template_values={
            'myuser':myuser,
            'numtweet':numtweet,
            'numfollower': numoffollower,
            'numfollowing':numoffollowing
        }
        template = JINJA_ENVIRONMENT.get_template('perinf.html')
        self.response.write(template.render(template_values))
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curuser=users.get_current_user()
        myuser_key = ndb.Key('MyUser', curuser.user_id())
        myuser = myuser_key.get()
        ubutton=self.request.get('button')
        bbutton=self.request.get('bio')
        getname=self.request.get('name')
        strupdate='update'
        strbio='bio'
        if ubutton==str(strupdate):
            myuser.bio=bbutton
            myuser.name=getname
            myuser.put()
        if ubutton==str(strbio):
            myuser.bio=bbutton
            myuser.put()
        self.redirect('/')

class PUser(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        curuser=users.get_current_user()
        myuser_key = ndb.Key('MyUser', curuser.user_id())
        myuser = myuser_key.get()
        gettweets=myuser.tweet
        getfolwer=myuser.follower
        getfolwing=myuser.following
        gettweets=sorted(gettweets,key=lambda x: x.date,reverse= True)
        gettweets=gettweets[0:50]
        numoftweet=len(gettweets)
        numoffollower=len(getfolwer)
        numoffollowing=len(getfolwing)  
        getimg=[]
        for x in gettweets:
            link=None                    
            if x.image != None:
                link=images.get_serving_url( x.image, size=150, crop=True, secure_url=True)
            getimg.append(link)
        template_values = {
            'myuser' : myuser,
            'guest': False,
            'tweets':gettweets,
            'images':getimg,
            'numtweets': numoftweet,
            'follower' : numoffollower,
            'following': numoffollowing,
            'upload_url' : blobstore.create_upload_url('/tweet')
        }
        template = JINJA_ENVIRONMENT.get_template('profile.html')
        self.response.write(template.render(template_values))
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curuser=users.get_current_user()
        myuser_key = ndb.Key('MyUser', curuser.user_id())
        myuser = myuser_key.get()
        myuserid=myuser_key.id()
        username=self.request.get('button')
        curser=MyUser.query(MyUser.username==username).fetch()
        gettweets=curser[0].tweet
        gettweets=sorted(gettweets,key=lambda x: x.date,reverse= True)
        gettweets=gettweets[0:50]
        numoftweet=len(gettweets)
        numoffollower=len(myuser.follower)
        numoffollowing=len(myuser.following)  
        getimg=[]
        for x in gettweets:
            link=None                    
            if x.image != None:
                link=images.get_serving_url( x.image, size=150, crop=True, secure_url=True)
            getimg.append(link)
        if myuserid in curser[0].follower:
            identify='Unfollow'
        else:
            identify='Follow'
        template_values={
            'myuser': curser[0],
            'guest': True,
            'identify' : identify,
            'tweets':gettweets,
            'images':getimg,
            'numtweets': numoftweet,
            'follower' : numoffollower,
            'following': numoffollowing,
            'upload_url' : ""
        }
        template = JINJA_ENVIRONMENT.get_template('profile.html')
        self.response.write(template.render(template_values))


class FUser(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curuser=users.get_current_user()
        myuser_key = ndb.Key('MyUser', curuser.user_id())
        myuser = myuser_key.get()
        myuserid=myuser_key.id()
        identify=self.request.get('identification')
        if myuserid != identify:
            guest_key=ndb.Key('MyUser',identify)
            guest=guest_key.get()
            if identify in myuser.follower:
                myuser.follower.remove(identify)
                guest.following.remove(myuserid)
            else:
                myuser.following.append(identify)
                guest.follower.append(myuserid)
                myuser.put()
                guest.put()
            self.redirect('/')

class LUser(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curuser=users.get_current_user()
        myuser_key = ndb.Key('user', curuser.user_id())
        myuser = myuser_key.get()
        getusers=user.query().fetch()
        follist=self.request.get('list')
        listfol=[]
        wer='follower'
        wing='following'
        if follist==wer:
            for x in getusers:
                listfol.append(x.follower)
        else:
            for x in getusers:
                listfol.append(x.following)
        template_values={
            'myuser':myuser,
            'listfol': listfol
        }
        template = JINJA_ENVIRONMENT.get_template('followlist.html')
        self.response.write(template.render(template_values))

