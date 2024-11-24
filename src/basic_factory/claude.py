"""Claude integration for code review and generation."""
import os
from typing import List
import anthropic
from dataclasses import dataclass


@dataclass
class CodeReview:
    """Code review results from Claude."""
    summary: str
    suggestions: List[str]
    approval: bool


class Claude:
    """Interface to Claude for code review and generation."""

    def __init__(self, api_key: str | None = None):
        """Initialize Claude client.

        Args:
            api_key: Anthropic API key. If not provided, will look for ANTHROPIC_API_KEY env var.
        """
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ["ANTHROPIC_API_KEY"]
        )

    async def review_changes(self, diff: str, description: str | None = None) -> CodeReview:
        """Review code changes and provide feedback.

        Args:
            diff: Git diff of the changes
            description: Optional PR description or commit message

        Returns:
            CodeReview containing analysis and suggestions
        """
        # Construct prompt for code review
        prompt = f"""You are performing a code review. Please analyze the following code changes:

{diff}

"""
        if description:
            prompt += f"\nContext from the author:\n{description}\n"

        prompt += """
Please provide:
1. A brief summary of the changes
2. Any suggestions for improvements
3. Whether you would approve these changes (true/false)

Keep the review constructive and focused on meaningful improvements."""

        # Get Claude's response
        message = await self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse response into structured review
        # TODO: Improve response parsing to better handle Claude's output format
        response = message.content[0].text

        # Basic parsing - we can make this more sophisticated
        summary = "To be implemented"
        suggestions = ["To be implemented"]
        approval = True

        return CodeReview(
            summary=summary,
            suggestions=suggestions,
            approval=approval
        )