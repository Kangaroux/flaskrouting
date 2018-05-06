import flask.views


__all__ = ["path", "page", "var", "TRAILING_SLASHES"]


TRAILING_SLASHES = False


def path(name, routes):
  """ Creates a new path definition. A path is considered the part of the URL
  that comes before the last forward slash. For example, `/user/account/` has a
  path of `/user/account` and the page is `/`. If the trailing slash is missing,
  the path would be `/user` and the page would be `/account`
  """
  return Path(name, routes)

def var(param, routes, name=None):
  """ Creates a new variable definition. An variable is a dynamic part of the
  URL that gets passed to the view as a parameter. For example,
  `/user/<int:userid>` has an variable variable `userid`.
  """
  return Variable(param, routes, name) 

def page(url, view, name=None, methods=None, **options):
  """ Creates a new page definition. A page points to the actual view that will
  process the request. 
  """
  return Page(url, view, methods=methods, name=name, **options)


class BaseRouteComponent:
  def register(self, app, url_parts, name_parts):
    pass


class Path(BaseRouteComponent):
  def __init__(self, name, routes):
    if name.endswith("/"):
      raise ValueError("Path name cannot end in a trailing slash")

    self.name = name.lstrip("/")
    self.routes = routes

  def register(self, app, url_parts=None, name_parts=None):
    if url_parts is not None and not self.name:
      raise ValueError("Nested path cannot have an empty name")

    if url_parts is None:
      url_parts = []

    if name_parts is None:
      name_parts = []

    for r in self.routes:
      if not isinstance(r, BaseRouteComponent):
        raise TypeError("Child must be a subclass of BaseRouteComponent (is %s)" % r)

      if self.name:
        r.register(app, url_parts + [self.name], name_parts + [self.name])
      else:
        r.register(app, url_parts, name_parts)


class Variable(BaseRouteComponent):
  def __init__(self, param, routes, name=None):
    if param.startswith("/") or param.endswith("/"):
      raise ValueError("A variable parameter cannot start or end with a slash")

    self.name = name
    self.param = param
    self.routes = routes

  def register(self, app, url_parts=None, name_parts=None):
    if url_parts is None or name_parts is None:
      raise Exception("A variable parameter must be wrapped in a path")

    for r in self.routes:
      if not isinstance(r, BaseRouteComponent):
        raise TypeError("Child must be a subclass of BaseRouteComponent (is %s)" % r)

      if self.name:
        r.register(app, url_parts + [self.param], name_parts + [self.name])
      else:
        r.register(app, url_parts + [self.param], name_parts)


class Page(BaseRouteComponent):
  def __init__(self, url, view, methods=None, name=None, **options):
    self.view = view

    if url == "/":
      self.url = url
    else:
      self.url = url.lstrip("/")

    if name is not None:
      self.name = name
    else:
      self.name = self.url.strip("/") or None

    self.methods = methods or ["GET", "POST", "PUT", "PATCH", "DELETE"]
    self.options = options

  def register(self, app, url_parts, name_parts):
    """ Registers the page with the app with the given name for lookups """
    if self.name:
      name_parts = name_parts.copy() + [self.name]

    if self.url:
      url_parts = url_parts.copy() + [self.url]

    if not name_parts:
      raise Exception("A page or parent path must have a name")

    name = ".".join(name_parts)
    url = "/%s" % "/".join(url_parts).rstrip("/")

    # Append a trailing slash to the URL if we're doing that for every URL or if
    # this path was defined explicitly with a trailing slash
    if TRAILING_SLASHES or self.url.endswith("/"):
      url += "/"

    try:
      is_class_view = issubclass(self.view, flask.views.View)
    except TypeError:
      is_class_view = False
    else:
      if not is_class_view:
        raise TypeError("View must be a view class or a view function (is %s)" % self.view)

    # Use an existing view function otherwise flask gets upset because it thinks
    # we're trying to overwrite it
    if is_class_view:
      view = app.view_functions.get(name, self.view.as_view(name))
    else:
      view = app.view_functions.get(name, self.view)

    app.add_url_rule(rule=url,
      endpoint=name,
      view_func=view,
      methods=self.methods,
      **self.options)
