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
        self, file_content: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze code style and formatting issues."""
        system_prompt = """
        You are an expert code reviewer focusing on code style and formatting. 
        Analyze the provided code and identify style issues such as:
        - Inconsistent naming conventions
        - Improper indentation
        - Line length issues
        - Missing or inconsistent comments
        - Inconsistent formatting
        
        Return a list of issues in JSON format, where each issue has:
        - line: the line number (int)
        - issue: description of the issue (string)
        - severity: "low", "medium", or "high" (string)
        - suggestion: how to fix the issue (string)
        
        If no issues are found, return an empty list.
        """

        prompt = f"""
        Analyze the following code for style and formatting issues:
        
        Filename: {filename}
        
        ```
        {file_content}
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

    def analyze_bugs(self, file_content: str, filename: str) -> List[Dict[str, Any]]:
        """Analyze potential bugs or errors."""
        system_prompt = """
        You are an expert code reviewer focusing on identifying potential bugs and errors. 
        Analyze the provided code and identify issues such as:
        - Logical errors
        - Off-by-one errors
        - Null/undefined references
        - Race conditions
        - Memory leaks
        - Exception handling issues
        
        Return a list of issues in JSON format, where each issue has:
        - line: the line number (int)
        - issue: description of the issue (string)
        - severity: "low", "medium", or "high" (string)
        - suggestion: how to fix the issue (string)
        
        If no issues are found, return an empty list.
        """

        prompt = f"""
        Analyze the following code for potential bugs and errors:
        
        Filename: {filename}
        
        ```
        {file_content}
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
        self, file_content: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze performance issues."""
        system_prompt = """
        You are an expert code reviewer focusing on performance optimization. 
        Analyze the provided code and identify issues such as:
        - Inefficient algorithms
        - Unnecessary computations
        - Redundant operations
        - Inefficient data structures
        - Resource leaks
        
        Return a list of issues in JSON format, where each issue has:
        - line: the line number (int)
        - issue: description of the issue (string)
        - severity: "low", "medium", or "high" (string)
        - suggestion: how to fix the issue (string)
        
        If no issues are found, return an empty list.
        """

        prompt = f"""
        Analyze the following code for performance issues:
        
        Filename: {filename}
        
        ```
        {file_content}
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
        self, file_content: str, filename: str
    ) -> List[Dict[str, Any]]:
        """Analyze adherence to best practices."""
        system_prompt = """
        You are an expert code reviewer focusing on best practices. 
        Analyze the provided code and identify issues such as:
        - Lack of modularity
        - Poor abstraction
        - Inadequate error handling
        - Security vulnerabilities
        - Maintainability issues
        
        Return a list of issues in JSON format, where each issue has:
        - line: the line number (int)
        - issue: description of the issue (string)
        - severity: "low", "medium", or "high" (string)
        - suggestion: how to fix the issue (string)
        
        If no issues are found, return an empty list.
        """

        prompt = f"""
        Analyze the following code for adherence to best practices:
        
        Filename: {filename}
        
        ```
        {file_content}
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
