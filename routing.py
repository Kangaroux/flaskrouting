import flask.views


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
  return Endpoint(view, url, methods)


class BaseRoute:
  def register(self, app, names):
    pass


class Route(BaseRoute):
  def __init__(self, name, routes):
    self.name = name
    self.routes = routes

  def register(self, app, names=None):
    for r in self.routes:
      if not isinstance(r, BaseRoute):
        raise TypeError("Route must a subclass of BaseRoute (is %s)", r)

      if not names:
        names = []

      r.register(app, names + [self.name])


class Endpoint(BaseRoute):
  def __init__(self, view, url, methods=None):
    self.view = view
    self.url = url

    if methods:
      self.methods = methods
    else:
      self.methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

  def register(self, app, names):
    """ Registers the endpoint with the app with the given name for lookups """
    url = "/%s%s" % ("/".join(names), self.url)
    name = ".".join(names)

    # Use an existing view function otherwise flask gets upset because it thinks
    # we're trying to overwrite it
    if issubclass(self.view, flask.views.View):
      view = app.view_functions.get(name, self.view.as_view(name))
    else:
      view = app.view_functions.get(name, self.view)

    app.add_url_rule(url,
      endpoint=name,
      view_func=view,
      methods=self.methods)
