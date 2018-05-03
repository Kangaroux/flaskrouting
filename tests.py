import flask.views
from unittest.mock import Mock

from routing import endpoint, route


class ViewClass(flask.views.View): pass
def view_func(): pass


def test_no_endpoints():
  m = Mock()

  route("test1", [
    route("test2", [])
  ]).register(m)

  m.add_url_rule.assert_not_called()

def test_root_endpoint():
  m = Mock()

  route("dir", [
    endpoint("endpoint", ViewClass)
  ]).register(m)

  m.add_url_rule.assert_called_once()