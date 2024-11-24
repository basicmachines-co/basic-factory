"""Tests for Claude integration."""
import pytest
from basic_factory.claude import Claude, CodeReview


@pytest.mark.asyncio
async def test_review_changes():
    """Test basic code review functionality."""
    claude = Claude("test-key")  # We'll need to mock the API calls

    diff = """
diff --git a/src/basic_factory/hello.py b/src/basic_factory/hello.py
new file mode 100644
--- /dev/null
+++ b/src/basic_factory/hello.py
@@ -0,0 +1,5 @@
+
+def hello_world() -> str:
+    return "Hello from Basic Factory!"
"""

    description = "Add hello world function with tests"

    review = await claude.review_changes(diff, description)

    assert isinstance(review, CodeReview)
    assert isinstance(review.summary, str)
    assert isinstance(review.suggestions, list)
    assert isinstance(review.approval, bool)