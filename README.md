# flask-routing

Writing routes in flask is cumbersome. There is a lot of boilerplate code and duplication. flask-routing lets you quickly define your site's routes with as little code as possible.

# Getting Started

Install flask-routing with `pip install flask-routing`

Here's some routing for a simple blog site:

```python
from flaskrouting import var, page, path

path("", [
  page("", HomeView, name="home"),
  page("blogs", BlogListView),

  path("blog", [
    var("<int:blog_id>", [
      page("", BlogView),
      page("edit", EditBlogView)
    ])
  ])
])
```

We've defined 4 pages by using `var`, `page`, and `path`. The URLs for each page are built up one piece at a time. As a result, related URLs are implicitly grouped together and you don't need to duplicate any code. Here are the reverse lookups for each route:

```python
url_for("home")                   => "/"
url_for("blogs")                  => "/blogs"
url_for("blog", blog_id=12)       => "/blog/12"
url_for("blog.edit", blog_id=12)  => "/blog/12/edit"
```

# Reference

### path(name, routes)

Creates a path definition with `name` applied to `routes`.

- `name`: The name of the path. This is used when building the URL as well as generating the reverse lookup name. If this path is at the root level, this can be set to `""`, in which case it's not used in the URL or the reverse lookup name, and merely acts as a container.
- `routes`: A list containing `var`, `page`, and/or `path` objects. If set to `[]`, the path is discarded.

### page(url, view, name=None, methods=None)

Creates a page definition at `url` which forwards requests to `view`. For reverse lookups, `url` is used by default unless `name` is set. If neither `url` or `name` are set, the name of the page is omitted from the reverse lookup. You can also specify a list of HTTP verbs for `methods` if you want to restrict the view to only serve certain requests (by default it accepts everything).

- `url`: The URL of the page. If set to `""`, nothing is appended to the full URL or the reverse lookup name.
- `view`: A view function or a subclass of `flask.views.View`.
- `name` *(optional)*: If set, this will be used for the reverse lookup name instead of `url`. This must be set if the page is located at `/` (otherwise it won't have a reverse lookup name). If `url` is `""`, no page name will be used in the reverse lookup unless this is set.
- `methods` *(optional)*: If set, the view will only accept requests that were made with the HTTP verbs provided. If this is not set, the view accepts requests made from any of the verbs: `["GET", "POST", "PUT", "PATCH", "DELETE"]`

### var(var, routes, name=None)

Creates a new variable rule in the route. By default a variable defintion does not include itself as part of the reverse lookup of a route, however you can set `name` to override this.

- `var`: The variable definition. This is a dynamic part of the URL that will be passed to the view as a parameter. See the [flask documentation for variable rules](http://flask.pocoo.org/docs/1.0/quickstart/#variable-rules) for information on formatting.
- `routes`: A list containing `var`, `page`, and/or `path` objects
- `name` *(optional)*: If set, uses `name` as part of a route's reverse lookup.

# Examples

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