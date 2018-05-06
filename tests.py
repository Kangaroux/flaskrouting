import flask.views
from unittest.mock import Mock, patch

from flaskrouting import var, page, path


class BadViewClass: pass
class ViewClass(flask.views.View): pass
def view_func(): pass

def new_mock():
  mock = Mock()

  return (mock.add_url_rule, mock)


def test_no_pages():
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
  _, kwargs = m.call_args

  assert kwargs["rule"] == "/dir/page"
  assert kwargs["endpoint"] == "dir.page"

  assert mock.view_functions.get.call_args[0][1].view_class == ViewClass

def test_view_function():
  m, mock = new_mock()

  path("dir", [
    page("page", view_func)
  ]).register(mock)

  assert m.called
  _, kwargs = m.call_args

  assert kwargs["rule"] == "/dir/page"
  assert kwargs["endpoint"] == "dir.page"

  assert mock.view_functions.get.call_args[0][1] == view_func

@patch("flaskrouting.TRAILING_SLASHES", True)
def test_trailing_slashes():
  m, mock = new_mock()
  
  path("dir", [
    page("page", view_func)
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["rule"] == "/dir/page/"

def test_empty_route():
  m, mock = new_mock()

  path("", [
    page("page1", view_func),
    page("page2", view_func)
  ]).register(mock)

  _, kwargs = m.call_args_list[0]
  assert kwargs["rule"] == "/page1"
  assert kwargs["endpoint"] == "page1"

  _, kwargs = m.call_args_list[1]
  assert kwargs["rule"] == "/page2"
  assert kwargs["endpoint"] == "page2"

def test_bad_nested_empty_route():
  m, mock = new_mock()

  try:
    path("dir", [
      path("", [
        page("page", view_func)
      ])
    ]).register(mock)

    assert 0
  except ValueError:
    pass

def test_page_with_name_no_path():
  m, mock = new_mock()

  path("", [
    page("", view_func, name="page")
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["rule"] == "/"
  assert kwargs["endpoint"] == "page"

def test_page_slash_with_path():
  m, mock = new_mock()

  path("dir", [
    page("/page/", view_func)
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["rule"] == "/dir/page/"
  assert kwargs["endpoint"] == "dir.page"

def test_empty_path_empty_page_with_slash():
  m, mock = new_mock()

  path("", [
    page("/", view_func, name="home")
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["rule"] == "/"
  assert kwargs["endpoint"] == "home"

def test_empty_page_with_slash():
  m, mock = new_mock()

  path("dir", [
    page("/", view_func, name="home")
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["rule"] == "/dir/"
  assert kwargs["endpoint"] == "dir.home"

def test_bad_empty_page():
  m, mock = new_mock()

  try:
    path("", [
      page("", view_func)
    ]).register(mock)

    assert 0
  except Exception:
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

    assert 0
  except TypeError:
    pass

def test_bad_route_child():
  m, mock = new_mock()

  try:
    path("", [
      "page"
    ]).register(mock)

    assert 0
  except TypeError:
    pass

def test_leading_slash():
  m, mock = new_mock()

  path("dir", [
    page("/page", view_func)
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["rule"] == "/dir/page"

def test_explicit_trailing_slash():
  m, mock = new_mock()

  path("dir", [
    page("/page/", view_func)
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["rule"] == "/dir/page/"

def test_variable():
  m, mock = new_mock()

  path("dir", [
    var("<int:var>", [
      page("page", view_func)
    ])
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["rule"] == "/dir/<int:var>/page"
  assert kwargs["endpoint"] == "dir.page"

def test_named_variable():
  m, mock = new_mock()

  path("dir", [
    var("<int:var>", name="var", routes=[
      page("page", view_func)
    ])
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["rule"] == "/dir/<int:var>/page"
  assert kwargs["endpoint"] == "dir.var.page"

def test_bad_variable():
  m, mock = new_mock()

  try:
    path("dir", [
      var("/<int:var>/", [
        page("page", view_func)
      ])
    ]).register(mock)

    assert 0
  except ValueError:
    pass

def test_root_variable():
  m, mock = new_mock()

  try:
    var("<int:var>", [
      page("page", view_func)
    ]).register(mock)

    assert 0
  except Exception:
    pass

def test_bad_variable_child():
  m, mock = new_mock()

  try:
    path("dir", [
      var("<int:var>", [
        view_func
      ])
    ]).register(mock)

    assert 0
  except TypeError:
    pass

def test_leading_slash_path():
  m, mock = new_mock()
  
  path("/dir", [
    page("/page", view_func)
  ]).register(mock)

  _, kwargs = m.call_args

  assert kwargs["rule"] == "/dir/page"
  assert kwargs["endpoint"] == "dir.page"

def test_bad_path_trailing_slash():
  m, mock = new_mock()

  try:
    path("dir/", [
      page("page", view_func)
    ]).register(mock)

    assert 0
  except ValueError:
    pass

def test_url_defaults():
  m, mock = new_mock()
  
  path("dir", [
    page("", view_func, defaults={ "var": 1 }),
    var("<int:var>", [
      page("", view_func),
    ])
  ]).register(mock)

  _, kwargs = m.call_args_list[0]

  assert kwargs["rule"] == "/dir"
  assert kwargs["endpoint"] == "dir"
  assert kwargs["defaults"] == { "var": 1 }

  _, kwargs = m.call_args_list[1]

  assert kwargs["rule"] == "/dir/<int:var>"
  assert kwargs["endpoint"] == "dir"
  assert "defaults" not in kwargs