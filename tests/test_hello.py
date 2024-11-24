"""Test hello world module."""
from basic_factory.hello import hello_world

def test_hello_world():
    """Test hello_world function."""
    assert hello_world() == "Hello from Basic Factory!"
