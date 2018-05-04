import flask.views
from unittest.mock import Mock, patch

from routing import endpoint, route


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
    endpoint("endpoint", ViewClass)
  ]).register(mock)

  assert m.called
  args, kwargs = m.call_args

  assert args[0] == "/dir/endpoint"
  assert kwargs["endpoint"] == "dir.endpoint"
  assert kwargs["methods"] == ["GET", "POST", "PUT", "PATCH", "DELETE"]

  assert mock.view_functions.get.call_args[0][1].view_class == ViewClass

def test_view_function():
  m, mock = new_mock()

  route("dir", [
    endpoint("endpoint", view_func)
  ]).register(mock)

  assert m.called
  args, kwargs = m.call_args

  assert args[0] == "/dir/endpoint"
  assert kwargs["endpoint"] == "dir.endpoint"
  assert kwargs["methods"] == ["GET", "POST", "PUT", "PATCH", "DELETE"]

  assert mock.view_functions.get.call_args[0][1] == view_func

@patch("routing.TRAILING_SLASHES", True)
def test_trailing_slashes():
  m, mock = new_mock()
  
  route("dir", [
    endpoint("endpoint", view_func)
  ]).register(mock)

  args, _ = m.call_args

  assert args[0] == "/dir/endpoint/"

def test_empty_route():
  m, mock = new_mock()

  route("", [
    endpoint("endpoint", view_func)
  ]).register(mock)

  args, _ = m.call_args

  assert args[0] == "/endpoint"

def test_bad_nested_empty_route():
  m, mock = new_mock()

  try:
    route("dir", [
      route("", [
        endpoint("endpoint", view_func)
      ])
    ]).register(mock)

    assert False
  except ValueError:
    pass
