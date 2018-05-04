import flask.views


TRAILING_SLASHES = False


def route(name, routes):
  """ Creates a new route. A route is everything in the url up until the final
  endpoint. Example:

  route("api", [
    endpoint("/myendpoint", MyView)
  ])

  Creates an endpoint at "/api/myendpoint" which uses the view MyView
  """
  return Route(name, routes)

def endpoint(url, view, methods=None, name=None):
  """ Creates a new endpoint. An endpoint points to a specific view or view class.
  Example:

  route("api", [
    endpoint("/myendpoint", MyView, methods=["GET", "POST"])
  ])

  Creates an endpoint at "/api/myendpoint" which uses the view MyView, and only
  accepts the HTTP methods "GET" and "POST"
  """
  return Endpoint(url, view, methods=methods, name=name)


class BaseRoute:
  def register(self, app, parts):
    pass


class Route(BaseRoute):
  def __init__(self, name, routes):
    self.name = name
    self.routes = routes

  def register(self, app, parts=None):
    for r in self.routes:
      if not isinstance(r, BaseRoute):
        raise TypeError("Route must be a subclass of BaseRoute (is %s)" % r)

      if not parts:
        parts = []
      elif not self.name:
        raise ValueError("Nested route cannot have an empty name")

      if self.name:
        parts += [self.name]

      r.register(app, parts)


class Endpoint(BaseRoute):
  def __init__(self, url, view, methods=None, name=None):
    self.view = view
    self.url = url

    if not url and not name:
      raise TypeError("An endpoint without a url must have a name")

    self.name = name or self.url
    self.methods = methods or ["GET", "POST", "PUT", "PATCH", "DELETE"]

  def register(self, app, parts):
    """ Registers the endpoint with the app with the given name for lookups """
    name = ".".join(parts + [self.name])
    url = "/%s" % "/".join(parts + [self.url])

    if TRAILING_SLASHES:
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

    app.add_url_rule(url,
      endpoint=name,
      view_func=view,
      methods=self.methods)
