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

def endpoint(url, view, methods=None):
  """ Creates a new endpoint. An endpoint points to a specific view or view class.
  Example:

  route("api", [
    endpoint("/myendpoint", MyView, methods=["GET", "POST"])
  ])

  Creates an endpoint at "/api/myendpoint" which uses the view MyView, and only
  accepts the HTTP methods "GET" and "POST"
  """
  return Endpoint(url, view, methods)


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
        raise TypeError("Route must be a subclass of BaseRoute (is %s)", r)

      if not parts:
        parts = []

      r.register(app, parts + [self.name])


class Endpoint(BaseRoute):
  def __init__(self, url, view, methods=None):
    self.view = view
    self.url = url

    if methods:
      self.methods = methods
    else:
      self.methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

  def register(self, app, parts):
    """ Registers the endpoint with the app with the given name for lookups """
    parts += [self.url]
    name = ".".join(parts)
    url = "/%s" % "/".join(parts)

    if TRAILING_SLASHES:
      url += "/"

    try:
      is_class_view = issubclass(self.view, flask.views.View)
    except TypeError:
      is_class_view = False

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