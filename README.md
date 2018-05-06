# flask-routing

Writing routes in flask is cumbersome. There is a lot of boilerplate code and duplication. flask-routing lets you quickly define your site's routes how you want with as little code as possible.

## Getting Started

Install flask-routing with `pip install flask-routing`

Here's some routing for a simple blog site:

```python
from flaskrouting import var, page, path

routes = path("", [
  page("", HomeView, name="home"),
  page("blogs", BlogListView),

  path("blog", [
    var("<int:blog_id>", [
      page("", BlogView),
      page("edit", EditBlogView)
    ])
  ])
])

# Register the routes with the flask app instance
routes.register(app)
```

We've defined 4 pages by using `var`, `page`, and `path`. The URLs for each page are built up one piece at a time. As a result, related URLs are implicitly grouped together and you don't need to duplicate any code. Here are the reverse lookups for each route:

```python
url_for("home")                   => "/"
url_for("blogs")                  => "/blogs"
url_for("blog", blog_id=12)       => "/blog/12"
url_for("blog.edit", blog_id=12)  => "/blog/12/edit"
```

To register the routes, simply call `register()` and provide the flask application instance. The easiest way to do this is to define your routes in a separate file, then import them and register with the application instance when it is created.


## Configuration

#### flaskrouting.TRAILING_SLASHES

Default: `False`

If `TRAILING_SLASHES = False`, flask-routing will not append a trailing slash to URLs unless you explicitly define them with one. To always append a trailing slash, set `flaskrouting.TRAILING_SLASHES = True` before calling the `register()` method.

# Reference

#### flaskrouting.path(name, routes)

Creates a path definition with `name` applied to `routes`. Every routing definition must be wrapped with a `path()`. To register a route definition, call `.register(app)` on the object that is returned

- `name`: The name of the path. This is used when building the URL as well as generating the reverse lookup name. If this path is at the root level, this can be set to `""`, in which case it's not used in the URL or the reverse lookup name, and merely acts as a container.
- `routes`: A list containing `var`, `page`, and/or `path` objects. If set to `[]`, the path is discarded.

#### flaskrouting.page(url, view, name=None, methods=None, \*\*options)

Creates a page definition at `url` which forwards requests to `view`. For reverse lookups, `url` is used by default unless `name` is set. If neither `url` or `name` are set, the name of the page is omitted from the reverse lookup. You can also specify a list of HTTP verbs for `methods` if you want to restrict the view to only serve certain requests (by default it accepts everything).

- `url`: The URL of the page. If set to `""`, nothing is appended to the full URL or the reverse lookup name.
- `view`: A view function or a subclass of `flask.views.View`.
- `name` *(optional)*: If set, this will be used for the reverse lookup name instead of `url`. This must be set if the page is located at `/` (otherwise it won't have a reverse lookup name). If `url` is `""`, no page name will be used in the reverse lookup unless this is set.
- `methods` *(optional)*: If set, the view will only accept requests that were made with the HTTP verbs provided. If this is not set, the view accepts requests made from any of the verbs: `["GET", "POST", "PUT", "PATCH", "DELETE"]`
- `**options` *(optional)*: Additional keyword options accepted by [add_url_rule()](http://flask.pocoo.org/docs/1.0/api/#flask.Flask.add_url_rule). You would most likely use this to pass a `defaults` argument (see the [flask docs](http://flask.pocoo.org/docs/1.0/api/#url-route-registrations) for more info).

#### flaskrouting.var(var, routes, name=None)

Creates a new variable rule in the route. By default a variable definition does not include itself as part of the reverse lookup of a route, however you can set `name` to override this.

- `var`: The variable definition. This is a dynamic part of the URL that will be passed to the view as a parameter. See the [flask docs](http://flask.pocoo.org/docs/1.0/quickstart/#variable-rules) on variable rules for information on formatting.
- `routes`: A list containing `var`, `page`, and/or `path` objects
- `name` *(optional)*: If set, uses `name` as part of a route's reverse lookup.

## Examples

### An index page at `/`

Use a blank path and page name to create a route at `/`. The page must be defined with a `name` otherwise there is nothing that can be used to do a reverse lookup on the URL.

```python
path("", [
  page("", IndexView, name="index")
])
```

### REST API

Use the `methods` argument to specify which HTTP methods a certain endpoint should be responsible for.

```python
path("api", [
  path("user", [
    page("", UserAPI, methods=["GET", "POST"]),
    var("<int:user_id>", [
      page("", UserAPI, methods=["PUT", "PATCH", "DELETE"])
    ])
  ])
])
```

### Partial route definitions

Depending on the size of your site, you may wish to split up your route definitions by package or view files. If your folder structure looks like this:

```
api/
  __init__.py
  blog.py
  comment.py
  user.py
```

You could import your view functions/classes into `__init__.py` and handle all of the routing there, or define partial routes in `blog.py`, `comment.py`, and `user.py`, and then combine them in `__init__.py`.

```python
# blog.py

routes = path("blog", [
  page("page1", view1),
  page("page2", view2),
])


# __init__.py

from .blog import routes as blog_routes

routes = path("api", [
  blog_routes
])
```

You can omit the `path()` and just define the partial route as a list as well:

```python
# blog.py

routes = [
  page("page1", view1),
  page("page2", view2),
]


# __init__.py

from .blog import routes as blog_routes

routes = path("api", [
  path("blog", blog_routes)
])
```