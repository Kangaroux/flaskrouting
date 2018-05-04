import flask.views
from unittest.mock import Mock

from routing import endpoint, route


class ViewClass(flask.views.View): pass
def view_func(): pass


def test_no_endpoints():
  mock = Mock()
  m = mock.add_url_rule

  route("test1", [
    route("test2", [])
  ]).register(m)

  assert not m.called

def test_view_class():
  mock = Mock()
  m = mock.add_url_rule

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
  mock = Mock()
  m = mock.add_url_rule

  route("dir", [
    endpoint("endpoint", view_func)
  ]).register(mock)

  assert m.called
  args, kwargs = m.call_args

  assert args[0] == "/dir/endpoint"
  assert kwargs["endpoint"] == "dir.endpoint"
  assert kwargs["methods"] == ["GET", "POST", "PUT", "PATCH", "DELETE"]

  assert mock.view_functions.get.call_args[0][1] == view_func