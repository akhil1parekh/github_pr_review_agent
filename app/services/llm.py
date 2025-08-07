from typing import Dict, List, Any, Optional
import json
from openai import OpenAI
from app.core.config import settings


class LLMService:
    """Service for interacting with LLM API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize LLM service with API key and model."""
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.LLM_MODEL
        self.client = OpenAI(api_key=self.api_key)

    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = settings.LLM_TEMPERATURE,
    ) -> str:
        """Generate a response from the LLM."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=temperature,
        )

        return response.choices[0].message.content

    def create_plan(
        self, pr_details: Dict[str, Any], files_changed: List[Dict[str, Any]]
    ) -> List[str]:
        """Create a plan for analyzing the PR."""
        system_prompt = """
        You are an expert code reviewer. Your task is to create a step-by-step plan for analyzing a GitHub pull request.
        The plan should include steps for analyzing code style, potential bugs, performance issues, and best practices.
        Return the plan as a list of steps in JSON format.
        """

        prompt = f"""
        I need to analyze a GitHub pull request with the following details:
        
        PR Details:
        {json.dumps(pr_details, indent=2)}
        
        Files Changed:
        {json.dumps([{"filename": f["filename"], "status": f["status"], "additions": f["additions"], "deletions": f["deletions"]} for f in files_changed], indent=2)}
        
        Create a step-by-step plan for analyzing this PR. Focus on:
        1. Code style and formatting issues
        2. Potential bugs or errors
        3. Performance improvements
        4. Best practices
        
        Return the plan as a JSON list of strings, where each string is a step in the plan.
        """

        response = self.generate_response(prompt, system_prompt, temperature=0.2)

        try:
            # Try to parse the response as JSON
            plan = json.loads(response)
            if isinstance(plan, list):
                return plan
            elif isinstance(plan, dict) and "plan" in plan:
                return plan["plan"]
            else:
                # If the response is not a list or a dict with a "plan" key, extract lines
                return [step.strip() for step in response.split("\n") if step.strip()]
        except json.JSONDecodeError:
            # If the response is not valid JSON, extract lines
            return [step.strip() for step in response.split("\n") if step.strip()]

    def analyze_code_style(
        self, pr_details: Dict[str, Any], patch: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze code style and formatting issues."""
        system_prompt = """
        You are an expert Python code reviewer, specializing in PEP 8 and common style conventions.
        Analyze the provided code, which is part of a GitHub pull request.
        Identify any style and formatting issues, such as:
        - Naming conventions (snake_case for variables and functions, PascalCase for classes).
        - Improper indentation (must be 4 spaces per level).
        - Line length (should not exceed 88 characters).
        - Incorrect import order.
        - Missing or inconsistent docstrings and comments.
        - Inconsistent use of quotes (single vs. double).

        Return a list of issues in JSON format. Each issue must be a dictionary with the following keys:
        - "line": The line number (int) where the issue occurs.
        - "type": "style" (string).
        - "description": A clear and concise description of the style issue (string).
        - "severity": "low", "medium", or "high" (string).
        - "suggestion": A concrete, actionable suggestion for how to fix the issue. If possible, provide a code snippet using GitHub's suggestion format.

        Example of a suggestion with a code snippet:
        "suggestion": "Rename 'myVar' to 'my_var' to follow snake_case convention.\\n```suggestion\\nmy_var = ...\\n```"

        If no issues are found, return an empty JSON list: [].
        """

        prompt = f"""
        Analyze the following code patch for style and formatting issues, considering the context of the pull request.

        PR Title: {pr_details.get('title', 'N/A')}
        PR Description: {pr_details.get('description', 'N/A')}
        
        Filename: {filename}
        
        Patch (diff format):
        ```diff
        {patch}
        ```
        
        Return a list of issues in JSON format.
        """

        response = self.generate_response(prompt, system_prompt, temperature=0.3)

        try:
            issues = json.loads(response)
            if isinstance(issues, list):
                return issues
            elif isinstance(issues, dict) and "issues" in issues:
                return issues["issues"]
            else:
                return []
        except json.JSONDecodeError:
            return []

    def analyze_bugs(
        self, pr_details: Dict[str, Any], patch: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze potential bugs or errors."""
        system_prompt = """
        You are an expert Python code reviewer with a focus on identifying potential bugs and runtime errors.
        Analyze the provided code, which is part of a GitHub pull request.
        Look for issues such as:
        - Logical errors that could lead to incorrect output.
        - Off-by-one errors in loops or indexing.
        - Null or `None` reference errors.
        - Unhandled exceptions or inadequate error handling.
        - Race conditions or other concurrency issues.
        - Mismatched variable types or unsafe type casting.

        Return a list of issues in JSON format. Each issue must be a dictionary with the following keys:
        - "line": The line number (int) where the bug is likely to occur.
        - "type": "bug" (string).
        - "description": A clear and concise description of the potential bug (string).
        - "severity": "low", "medium", or "high" (string), based on the potential impact.
        - "suggestion": A concrete, actionable suggestion for how to fix the bug. Provide a code snippet with the suggested fix.

        Example of a suggestion:
        "suggestion": "Add a null check before accessing the 'user' object.\\n```suggestion\\nif user:\\n    return user.name\\n```"

        If no issues are found, return an empty JSON list: [].
        """

        prompt = f"""
        Analyze the following code patch for potential bugs and errors, considering the context of the pull request.

        PR Title: {pr_details.get('title', 'N/A')}
        PR Description: {pr_details.get('description', 'N/A')}
        
        Filename: {filename}
        
        Patch (diff format):
        ```diff
        {patch}
        ```
        
        Return a list of issues in JSON format.
        """

        response = self.generate_response(prompt, system_prompt, temperature=0.3)

        try:
            issues = json.loads(response)
            if isinstance(issues, list):
                return issues
            elif isinstance(issues, dict) and "issues" in issues:
                return issues["issues"]
            else:
                return []
        except json.JSONDecodeError:
            return []

    def analyze_performance(
        self, pr_details: Dict[str, Any], patch: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze performance issues."""
        system_prompt = """
        You are an expert Python code reviewer with a deep understanding of performance optimization.
        Analyze the provided code, which is part of a GitHub pull request.
        Identify performance issues such as:
        - Inefficient algorithms or data structures (e.g., using a list for frequent lookups instead of a set or dict).
        - Unnecessary computations inside loops.
        - Redundant database queries or API calls.
        - Memory-intensive operations that could be optimized (e.g., using generators).
        - Blocking I/O operations that could be made asynchronous.

        Return a list of issues in JSON format. Each issue must be a dictionary with the following keys:
        - "line": The line number (int) of the performance bottleneck.
        - "type": "performance" (string).
        - "description": A clear and concise description of the performance issue (string).
        - "severity": "low", "medium", or "high" (string), based on the potential performance gain.
        - "suggestion": A concrete, actionable suggestion for how to optimize the code. Provide a refactored code snippet.

        Example of a suggestion:
        "suggestion": "Using a set for 'items_to_check' will provide much faster lookups than a list.\\n```suggestion\\nitems_to_check = {1, 2, 3}\\nif item in items_to_check:\\n    ...\\n```"

        If no issues are found, return an empty JSON list: [].
        """

        prompt = f"""
        Analyze the following code patch for performance issues, considering the context of the pull request.

        PR Title: {pr_details.get('title', 'N/A')}
        PR Description: {pr_details.get('description', 'N/A')}
        
        Filename: {filename}
        
        Patch (diff format):
        ```diff
        {patch}
        ```
        
        Return a list of issues in JSON format.
        """

        response = self.generate_response(prompt, system_prompt, temperature=0.3)

        try:
            issues = json.loads(response)
            if isinstance(issues, list):
                return issues
            elif isinstance(issues, dict) and "issues" in issues:
                return issues["issues"]
            else:
                return []
        except json.JSONDecodeError:
            return []

    def analyze_best_practices(
        self, pr_details: Dict[str, Any], patch: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze adherence to best practices."""
        system_prompt = """
        You are a senior Python engineer focusing on software architecture and best practices.
        Analyze the provided code, which is part of a GitHub pull request.
        Identify issues related to:
        - Modularity and separation of concerns.
        - Readability and maintainability.
        - Proper use of design patterns.
        - Security vulnerabilities (e.g., hardcoded secrets, injection risks).
        - Adherence to the principle of least astonishment.
        - Testability of the code.

        Return a list of issues in JSON format. Each issue must be a dictionary with the following keys:
        - "line": The line number (int) where the issue is located.
        - "type": "best_practice" (string).
        - "description": A clear and concise description of the best practice violation (string).
        - "severity": "low", "medium", or "high" (string).
        - "suggestion": A concrete, actionable suggestion for how to refactor the code to follow best practices.

        Example of a suggestion:
        "suggestion": "Instead of a hardcoded API key, use a configuration service or environment variable to manage secrets."

        If no issues are found, return an empty JSON list: [].
        """

        prompt = f"""
        Analyze the following code patch for best practices, considering the context of the pull request.

        PR Title: {pr_details.get('title', 'N/A')}
        PR Description: {pr_details.get('description', 'N/A')}

        Filename: {filename}
        
        Patch (diff format):
        ```diff
        {patch}
        ```
        
        Return a list of issues in JSON format.
        """

        response = self.generate_response(prompt, system_prompt, temperature=0.3)

        try:
            issues = json.loads(response)
            if isinstance(issues, list):
                return issues
            elif isinstance(issues, dict) and "issues" in issues:
                return issues["issues"]
            else:
                return []
        except json.JSONDecodeError:
            return []

    def analyze_semantic_issues(
        self, pr_details: Dict[str, Any], patch: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze semantic and logical issues."""
        system_prompt = """
        You are a senior Python developer with strong logical reasoning skills.
        Your task is to analyze the provided code patch in the context of the pull request's goal and identify semantic or logical issues.
        A semantic issue is when the code is syntactically correct but does not do what it is intended to do.
        Use the PR title and description to understand the intended purpose of the code.

        Look for issues like:
        - The code does not correctly implement the feature or fix described in the PR description.
        - The logic contains flaws that will lead to unexpected behavior.
        - Misused variables, functions, or libraries.
        - The code is correct but overly complex and could be simplified.

        Return a list of issues in JSON format. Each issue must be a dictionary with the following keys:
        - "line": The line number (int) where the semantic issue is located.
        - "type": "semantic" (string).
        - "description": A clear and concise description of the semantic issue (string).
        - "severity": "low", "medium", or "high" (string).
        - "suggestion": A concrete, actionable suggestion for how to correct the logic or implement the feature correctly.

        If no issues are found, return an empty JSON list: [].
        """

        prompt = f"""
        Analyze the following code patch for semantic and logical issues, considering the context of the pull request.

        PR Title: {pr_details.get('title', 'N/A')}
        PR Description: {pr_details.get('description', 'N/A')}
        
        Filename: {filename}
        
        Patch (diff format):
        ```diff
        {patch}
        ```
        
        Return a list of issues in JSON format.
        """

        response = self.generate_response(prompt, system_prompt, temperature=0.4)

        try:
            issues = json.loads(response)
            if isinstance(issues, list):
                return issues
            elif isinstance(issues, dict) and "issues" in issues:
                return issues["issues"]
            else:
                return []
        except json.JSONDecodeError:
            return []

    def create_summary(self, analysis_results: Dict[str, List[Dict[str, Any]]]) -> str:
        """Create a summary of the analysis results."""
        system_prompt = """
        You are an expert code reviewer. Your task is to create a summary of the analysis results for a GitHub pull request.
        The summary should be concise but informative, highlighting the most important issues and providing an overall assessment.
        """

        prompt = f"""
        Create a detailed summary of the following analysis results for a GitHub pull request:
        
        Style Issues: {len(analysis_results.get("style_issues", []))}
        Bugs: {len(analysis_results.get("bugs", []))}
        Performance Issues: {len(analysis_results.get("performance_issues", []))}
        Best Practices Issues: {len(analysis_results.get("best_practices", []))}
        
        Here are some examples of the issues found:
        
        Style Issues:
        {json.dumps(analysis_results.get("style_issues", [])[:3], indent=2)}
        
        Bugs:
        {json.dumps(analysis_results.get("bugs", [])[:3], indent=2)}
        
        Performance Issues:
        {json.dumps(analysis_results.get("performance_issues", [])[:3], indent=2)}
        
        Best Practices Issues:
        {json.dumps(analysis_results.get("best_practices", [])[:3], indent=2)}
        
        Create a detailed and informative summary of these results, highlighting the most important issues and providing an overall assessment for every file changes and how it will affect the codebase.
        """

        return self.generate_response(prompt, system_prompt, temperature=0.5)


llm_service = LLMService()
