import os
import re

import jinja2
import webapp2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
  loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_username(username):
    return USERNAME_RE.match(username)


def valid_password(password):
    return password and PASS_RE.match(password)


def valid_email(email):
    return not email or EMAIL_RE.match(email)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def get(self):
        items = self.request.get_all("food")
        self.render("shopping_list.html", items=items)


class FizzBuzzHandler(Handler):
    def get(self):
        n = self.request.get('n', 0)
        n = n and int(n)
        self.render('fizzbuzz.html', n=n)


class Rot (Handler):
    def get(self):
        self.render('rot.html')

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')
        self.render('rot.html', text=rot13)


class Signup(Handler):

    def get(self):
        self.render("signup.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username=username,
                      email=email)

        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup.html', **params)
        else:
            self.redirect('/welcome?username=' + username)


class Welcome(Handler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username=username)
        else:
            self.redirect('/signup')

# class SignUp (Handler):
#     def get(self):
#         self.render('signup.html', errors={})

#     def post(self):
#         username = self.request.get('username')
#         password = self.request.get('password')
#         verify_password = self.request.get('verify_password')
#         errors = {
#             "username": False,
#             "password": False
#         }

#         if not valid_username(username):
#             errors["username"] = True

#         if password != verify_password:
#             errors["password"] = True

#         if errors["username"] or errors["password"]:
#             return self.render('signup.html',
#                                username=username,
#                                password=password, errors=errors)
#         self.response.set_cookie('username', username, max_age=360, path='/',
#                                  domain=None)
#         self.redirect('/welcome')


# class Welcome (Handler):
#     def get(self):
#         username = self.request.cookies.get('username')
#         self.render('welcome.html', username=username)

class Content(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class NewPost (Handler):
    def render_front(self, subject="", content="", error=""):
        contents = db.GqlQuery("SELECT * FROM Content "
                               "ORDER BY created DESC ")

        self.render("newpost.html", subject=subject, content=content,
                    error=error, contents=contents)

    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            c = Content(subject=subject, content=content)
            c.put()

            self.redirect('/blog')
        else:
            error = "We need both a subject and some content!"
            self.render_front(subject, content, error)


class Blog (Handler):
    def render_blog(self, subject="", content="", error=""):
        contents = db.GqlQuery("SELECT * FROM Content "
                               "ORDER BY created DESC ")

        self.render("blog.html", subject=subject, content=content,
                    error=error, contents=contents)

    def get(self):
        self.render_blog()

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/fizzbuzz', FizzBuzzHandler),
    ('/rot13', Rot),
    ('/signup', Signup),
    ('/welcome', Welcome),
    ('/blog/newpost', NewPost),
    ('/blog', Blog)
], debug=True)
