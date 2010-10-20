from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import users
import logging


class Resource(db.Model):
	url = db.StringProperty()
	content_type = db.StringProperty()
	body = db.TextProperty()
	updated = db.DateTimeProperty(auto_now=True)


class BaseHandler(webapp.RequestHandler):

	def context(self):
		return {
			"request": self.request,
			"user": users.get_current_user(),
		}

	def not_found(self):
		self.error(404)
		self.render("404.html")

	def forbidden(self):
		self.error(403)
		self.render("403.html")

	def render(self, tpl, context={}):
		self.response.out.write(template.render("templates/" + tpl, dict(self.context(), **context)))
	

class ResourceHandler(BaseHandler):

	def find_resource(self, path=None):
		if path == None:
			path = self.request.path
		return Resource.all().filter("url = ", path).order("-updated").get()

	def get(self, path):
		resource = self.find_resource()
		if self.request.get("edit", None) != None and users.is_current_user_admin():
			if not resource:
				resource = Resource(url=path, content_type="text/html", body="")
			self.render("edit.html", { "resource": resource })
		elif resource:
			self.response.headers["Content-Type"] = resource.content_type
			self.response.out.write(resource.body)
		else:
			self.not_found()

	def post(self, path):
		if users.is_current_user_admin():
			#resource = self.find_resource()
			#if not resource:
			resource = Resource()
			resource.url = self.request.get("url", path)
			resource.content_type = self.request.get("content_type", "text/html")
			resource.body = self.request.get("body", "")
			resource.put()
			self.redirect(resource.url)
		else:
			self.forbidden()


class LoginHandler(BaseHandler):
	def get(self):
		go = self.request.get("go", "/")
		self.redirect(users.create_login_url(go))


def main():
    application = webapp.WSGIApplication([
    	('/login', LoginHandler),
    	('(.+)', ResourceHandler),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
