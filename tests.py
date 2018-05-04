import flask.views
from unittest.mock import Mock, patch

from routing import instance, page, path


class BadViewClass: pass
class ViewClass(flask.views.View): pass
def view_func(): pass

def new_mock():
  mock = Mock()

  return (mock.add_url_rule, mock)


def test_no_endpoints():
  m, mock = new_mock()

  path("test1", [
    path("test2", [])
  ]).register(m)

  assert not m.called

def test_view_class():
  m, mock = new_mock()

  path("dir", [
    page("page", ViewClass)
  ]).register(mock)

  assert m.called
  args, kwargs = m.call_args

  assert args[0] == "/dir/page"
  assert kwargs["endpoint"] == "dir.page"

  assert mock.view_functions.get.call_args[0][1].view_class == ViewClass

def test_view_function():
  m, mock = new_mock()

  path("dir", [
    page("page", view_func)
  ]).register(mock)

  assert m.called
  args, kwargs = m.call_args

  assert args[0] == "/dir/page"
  assert kwargs["endpoint"] == "dir.page"

  assert mock.view_functions.get.call_args[0][1] == view_func

@patch("routing.TRAILING_SLASHES", True)
def test_trailing_slashes():
  m, mock = new_mock()
  
  path("dir", [
    page("page", view_func)
  ]).register(mock)

  args, _ = m.call_args

  assert args[0] == "/dir/page/"

def test_empty_route():
  m, mock = new_mock()

  path("", [
    page("page", view_func)
  ]).register(mock)

  args, _ = m.call_args

  assert args[0] == "/page"

def test_bad_nested_empty_route():
  m, mock = new_mock()

  try:
    path("dir", [
      path("", [
        page("page", view_func)
      ])
    ]).register(mock)

    assert False
  except ValueError:
    pass

def test_empty_endpoint():
  m, mock = new_mock()

  path("", [
    page("", view_func, name="page")
  ]).register(mock)

  args, kwargs = m.call_args

  assert args[0] == "/"
  assert kwargs["endpoint"] == "page"

def test_bad_empty_endpoint():
  m, mock = new_mock()

  try:
    path("", [
      page("", view_func)
    ]).register(mock)

    assert False
  except TypeError:
    pass

def test_all_methods():
  m, mock = new_mock()

  path("", [
    page("page", view_func)
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["methods"] == ["GET", "POST", "PUT", "PATCH", "DELETE"]

def test_some_methods():
  m, mock = new_mock()

  path("", [
    page("page", view_func, methods=["GET", "POST"])
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["methods"] == ["GET", "POST"]

def test_bad_view_class():
  m, mock = new_mock()

  try:
    path("", [
      page("page", BadViewClass)
    ]).register(mock)

    assert False
  except TypeError:
    pass

def test_bad_route_child():
  m, mock = new_mock()

  try:
    path("", [
      "page"
    ]).register(mock)

    assert False
  except TypeError:
    pass

def test_leading_slash():
  m, mock = new_mock()

  path("dir", [
    page("/page", view_func)
  ]).register(mock)

  args, _ = m.call_args

  assert args[0] == "/dir/page"

def test_explicit_trailing_slash():
  m, mock = new_mock()

  path("dir", [
    page("/page/", view_func)
  ]).register(mock)

  args, _ = m.call_args

  assert args[0] == "/dir/page/"

def test_instance():
  m, mock = new_mock()

  path("dir", [
    instance("<int:instanceid>", [
      page("page", view_func)
    ])
  ]).register(mock)

  args, kwargs = m.call_args

  assert args[0] == "/dir/<int:instanceid>/page"
  assert kwargs["endpoint"] == "dir.page"

def test_named_instance():
  m, mock = new_mock()

  path("dir", [
    instance("<int:instanceid>", name="instance", routes=[
      page("page", view_func)
    ])
  ]).register(mock)

  args, kwargs = m.call_args

  assert args[0] == "/dir/<int:instanceid>/page"
  assert kwargs["endpoint"] == "dir.instance.page"