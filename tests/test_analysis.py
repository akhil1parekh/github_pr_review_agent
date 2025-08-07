import pytest
from unittest.mock import patch
import json
from app.services.llm import LLMService

@pytest.fixture
def llm_service():
    """Fixture for LLMService."""
    return LLMService(api_key="test_key", model="test_model")

@pytest.fixture
def pr_details():
    """Fixture for sample PR details."""
    return {
        "title": "Fix user authentication bug",
        "description": "This PR fixes a bug where the user's session expires prematurely.",
    }

def test_analyze_style_with_mocked_llm(llm_service, pr_details):
    """Test analyze_code_style with a mocked LLM response."""
    sample_patch = """
--- a/app/main.py
+++ b/app/main.py
@@ -1,5 +1,5 @@
 def my_function( myVar ):
-    if myVar==1:
+    if myVar == 1:
         print("Hello")
"""
    mock_response = [
        {
            "line": 1,
            "type": "style",
            "description": "Function name 'my_function' should be snake_case.",
            "severity": "low",
            "suggestion": "Rename to `my_function`."
        },
        {
            "line": 1,
            "type": "style",
            "description": "Variable name 'myVar' should be snake_case.",
            "severity": "low",
            "suggestion": "Rename to `my_var`."
        }
    ]

    with patch.object(llm_service.client.chat.completions, 'create') as mock_create:
        # Mock the entire response structure
        mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

        issues = llm_service.analyze_code_style(pr_details, sample_patch, "app/main.py")

        assert len(issues) == 2
        assert issues[0]["type"] == "style"
        assert "snake_case" in issues[0]["description"]

def test_analyze_bugs_with_mocked_llm(llm_service, pr_details):
    """Test analyze_bugs with a mocked LLM response."""
    sample_patch = """
--- a/app/utils.py
+++ b/app/utils.py
@@ -10,7 +10,7 @@
 def get_user_name(user):
-    return user.name
+    if user:
+        return user.name
"""
    mock_response = [
        {
            "line": 11,
            "type": "bug",
            "description": "Potential Null reference error if user is None.",
            "severity": "high",
            "suggestion": "Add a check for `user` before accessing `user.name`."
        }
    ]

    with patch.object(llm_service.client.chat.completions, 'create') as mock_create:
        mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

        issues = llm_service.analyze_bugs(pr_details, sample_patch, "app/utils.py")

        assert len(issues) == 1
        assert issues[0]["type"] == "bug"
        assert "Null reference" in issues[0]["description"]

def test_analyze_performance_with_mocked_llm(llm_service, pr_details):
    """Test analyze_performance with a mocked LLM response."""
    sample_patch = """
--- a/app/data.py
+++ b/app/data.py
@@ -20,6 +20,6 @@
 def process_items(items):
-    for i in items:
-        if i in [1, 2, 3]: # Inefficient lookup
+    item_set = {1, 2, 3}
+    for i in items:
+        if i in item_set: # Efficient lookup
             pass
"""
    mock_response = [
        {
            "line": 22,
            "type": "performance",
            "description": "Inefficient lookup in a list inside a loop.",
            "severity": "medium",
            "suggestion": "Convert the list to a set for faster lookups."
        }
    ]

    with patch.object(llm_service.client.chat.completions, 'create') as mock_create:
        mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

        issues = llm_service.analyze_performance(pr_details, sample_patch, "app/data.py")

        assert len(issues) == 1
        assert issues[0]["type"] == "performance"
        assert "Inefficient lookup" in issues[0]["description"]

def test_analyze_semantic_issues_with_mocked_llm(llm_service, pr_details):
    """Test analyze_semantic_issues with a mocked LLM response."""
    sample_patch = """
--- a/app/auth.py
+++ b/app/auth.py
@@ -5,5 +5,5 @@
 def is_authorized(user):
-    # Bug: This should check if the user is an admin
-    return user.is_active
+    return user.is_admin
"""
    pr_details["description"] = "This PR ensures that only admin users are authorized."
    mock_response = [
        {
            "line": 7,
            "type": "semantic",
            "description": "The code checks `is_active` but the PR description says it should check for admin users.",
            "severity": "high",
            "suggestion": "Change `user.is_active` to `user.is_admin` to match the intended logic."
        }
    ]

    with patch.object(llm_service.client.chat.completions, 'create') as mock_create:
        mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

        issues = llm_service.analyze_semantic_issues(pr_details, sample_patch, "app/auth.py")

        assert len(issues) == 1
        assert issues[0]["type"] == "semantic"
        assert "PR description" in issues[0]["description"]
