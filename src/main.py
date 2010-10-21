import datetime
import os.path

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from django.conf import settings
try:
	settings.configure(
		DEBUG=False,
		TEMPLATE_DEBUG=False,
		TEMPLATE_LOADERS = (
			'django.template.loaders.filesystem.load_template_source',
			'main.load_template_source',
		),
	)
except (EnvironmentError, RuntimeError):
	pass
  
from google.appengine.ext.webapp import template
from django.template import Template, Context
from django.template import TemplateDoesNotExist
	
def load_template_source(template_name, template_dirs=None):
	resource = Resource.get_latest(template_name)
	if resource == None:
		raise TemplateDoesNotExist, template_name
	else:
		return (resource.body, template_name)
load_template_source.is_usable = True


PRIVATE_CONTENT_TYPES = ["text/x-django-template"]


class Resource(db.Model):
	url = db.StringProperty()
	content_type = db.StringProperty()
	template = db.StringProperty()
	body = db.TextProperty()
	updated = db.DateTimeProperty()
	latest = db.BooleanProperty(default=True)

	@classmethod
	def get_latest(cls, path):
		return Resource.all().filter("url = ", path).filter("latest = ", True).get()
	
	def put(self, *args, **kwargs):
		previous = None
		if self.latest == True:
			self.updated = datetime.datetime.now()
			if not self.content_type:
				self.content_type = self.guess_content_type()
			previous = Resource.get_latest(self.url)
		super(Resource, self).put(*args, **kwargs)
		# flag previous as non-latest after new latest succesfully saved
		if previous:
			previous.latest = False
			previous.put()
		
	def guess_content_type(self):
		types = { ".css": "text/css",
		          ".js": "text/javascript",
		          ".txt": "text/plain",
		          ".tpl": "text/x-django-template" }
		suffix = os.path.splitext(self.url)[1]
		return types.get(suffix, "text/html")
		
	def get_versions(self):
		return Resource.all().filter("url = ", self.url).order("-updated").fetch(500)
	
	def get_templates(self):
		return Resource.all() \
			.filter("content_type = ", "text/x-django-template") \
			.filter("latest = ", True).order("url").fetch(500)


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
	def get(self, path):
		if users.is_current_user_admin() and self.request.get("edit", None) != None:
			version = self.request.get("version", None)
			if version:
				resource = Resource.get(version)
			else:
				resource = Resource.get_latest(path)
			resource_list = Resource.all().filter("latest = ", True).order("url").fetch(500)
			if not resource:
				resource = Resource(url=path, body="")
				resource_list.append(resource)
			self.render("edit.html", { "resource": resource,
			                           "resource_list": resource_list })
		else:
			resource = Resource.get_latest(path)
			if resource and resource.content_type not in PRIVATE_CONTENT_TYPES:
				self.response.headers["Content-Type"] = resource.content_type + "; charset=UTF-8"
				if resource.template:
					tpl_source = "{%% extends \"%s\" %%}\n%s" % (resource.template, resource.body)
					tpl = Template(tpl_source)
					self.response.out.write(tpl.render(Context(self.context())))
				else:
					self.response.out.write(resource.body)
			else:
				self.not_found()

	def post(self, path):
		if users.is_current_user_admin():
			resource = Resource()
			resource.url = self.request.get("url", path)
			resource.body = self.request.get("body", "")
			resource.template = self.request.get("template", None)
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
