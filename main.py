import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images
import os
from user import MyUser
from Fuser import *
from Ftweets import *

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        url=''
        url_string=''
        user = users.get_current_user()
        myuser=None
        if user:
            url = users.create_logout_url(self.request.uri)
            url_string = 'logout'
            myuser_key = ndb.Key('MyUser', user.user_id())
            myuser = myuser_key.get()
            if myuser==None:
                self.redirect('/login')
            else:
                getusers= MyUser.query().fetch()
                gettweets=[]
                for x in getusers:
                    temuser=x.key.id()
                    if temuser ==myuser.key.id():
                        gettweets= gettweets+ x.tweet
                    if temuser in myuser.follower:
                        gettweets= gettweets+ x.tweet
                posttweets=[]
                posttweets=sorted(gettweets,key=lambda x: x.date,reverse= True)
                #posttweets=posttweets.LIMIT[50]
                #include first num except last
                posttweets=posttweets[0:50]
                numoftweet=len(posttweets)
                numofusertweet=len(myuser.tweet)
                numoffollower=len(myuser.follower)
                numoffollowing=len(myuser.following)                 
                getimg=[]
                for x in posttweets:    
                    if x.image != None:
                        link=images.get_serving_url( x.image, size=150, crop=True, secure_url=True)
                    else:
                        link= None
                    getimg.append(link)
                template_values = {
                    'url': url,
                    'url_string': url_string,
                    'myuser': myuser,
                    'tweets': posttweets,
                    'totaltweets': numoftweet,
                    'image': getimg,
                    'numoftweet': numofusertweet,
                    'follower' : numoffollower,
                    'following': numoffollowing,
                    'upload_url' : blobstore.create_upload_url('/tweet')
                }
                template = JINJA_ENVIRONMENT.get_template('main.html')
                self.response.write(template.render(template_values))
        else:
            url = users.create_login_url(self.request.uri)
            url_string = 'login'
            self.redirect(url) 

class Search(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curuser=users.get_current_user()
        myuser_key = ndb.Key('MyUser', curuser.user_id())
        myuser = myuser_key.get()
        search= self.request.get('search')
        getusers=MyUser.query().fetch()
        getuser=[]
        gettweet=[]
        for x in getusers:
            if search in x.username:
                getuser.append(x.username)
            for y in x.tweet:
                if search in y.tweet:
                    gettweet.append(y)
        numoftweet=len(gettweet)
        template_values={
            'myuser' : myuser,
            'userfound': getuser,
            'tweetfound' :gettweet,
            'numtweet' : numoftweet
        }
        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))        

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/login', SUser),
    ('/perinf', UUser),
    ('/profile', PUser),
    ('/follow', FUser),
    ('/search',Search),
    ('/tweet', ATweet),
    ('/edittweet/(.*?)', ETweet),
    ('/tweet/delete', DTweet)  
], debug = True)