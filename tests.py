import flask.views
from unittest.mock import Mock, patch

from routing import page, route


class BadViewClass: pass
class ViewClass(flask.views.View): pass
def view_func(): pass

def new_mock():
  mock = Mock()

  return (mock.add_url_rule, mock)


def test_no_endpoints():
  m, mock = new_mock()

  route("test1", [
    route("test2", [])
  ]).register(m)

  assert not m.called

def test_view_class():
  m, mock = new_mock()

  route("dir", [
    page("page", ViewClass)
  ]).register(mock)

  assert m.called
  args, kwargs = m.call_args

  assert args[0] == "/dir/page"
  assert kwargs["endpoint"] == "dir.page"

  assert mock.view_functions.get.call_args[0][1].view_class == ViewClass

def test_view_function():
  m, mock = new_mock()

  route("dir", [
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
  
  route("dir", [
    page("page", view_func)
  ]).register(mock)

  args, _ = m.call_args

  assert args[0] == "/dir/page/"

def test_empty_route():
  m, mock = new_mock()

  route("", [
    page("page", view_func)
  ]).register(mock)

  args, _ = m.call_args

  assert args[0] == "/page"

def test_bad_nested_empty_route():
  m, mock = new_mock()

  try:
    route("dir", [
      route("", [
        page("page", view_func)
      ])
    ]).register(mock)

    assert False
  except ValueError:
    pass

def test_empty_endpoint():
  m, mock = new_mock()

  route("", [
    page("", view_func, name="page")
  ]).register(mock)

  args, kwargs = m.call_args

  assert args[0] == "/"
  assert kwargs["endpoint"] == "page"

def test_bad_empty_endpoint():
  m, mock = new_mock()

  try:
    route("", [
      page("", view_func)
    ]).register(mock)

    assert False
  except TypeError:
    pass

def test_all_methods():
  m, mock = new_mock()

  route("", [
    page("page", view_func)
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["methods"] == ["GET", "POST", "PUT", "PATCH", "DELETE"]

def test_some_methods():
  m, mock = new_mock()

  route("", [
    page("page", view_func, methods=["GET", "POST"])
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["methods"] == ["GET", "POST"]

def test_bad_view_class():
  m, mock = new_mock()

  try:
    route("", [
      page("page", BadViewClass)
    ]).register(mock)

    assert False
  except TypeError:
    pass

def test_bad_route_child():
  m, mock = new_mock()

  try:
    route("", [
      "page"
    ]).register(mock)

    assert False
  except TypeError:
    pass

def test_leading_slash():
  m, mock = new_mock()

  route("dir", [
    page("/page", view_func)
  ]).register(mock)

  args, _ = m.call_args

  assert args[0] == "/dir/page"

def test_explicit_trailing_slash():
  m, mock = new_mock()

  route("dir", [
    page("/page/", view_func)
  ]).register(mock)

  args, _ = m.call_args

  assert args[0] == "/dir/page/"