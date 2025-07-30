import os

AVAILABLE_AGENTS = ["coder", "flowchart_reader"]


class PromptLoader:
    """A class for loading prompts for different agents."""

    @staticmethod
    def load_prompt(agent_name: str, prompt_version: str = "v1") -> str:
        """
        Loads a prompt for a specific agent and prompt version.

        Args:
            agent_name (str): The name of the agent ("coder" or "flowchart_reader").
            prompt_version (str): The version of the prompt.

        Returns:
            str: The prompt text.
        """
        # Check if agent name is valid
        if agent_name not in AVAILABLE_AGENTS:
            raise ValueError(f"Unknown agent: '{agent_name}'")

        # Check if prompt version is valid for that agent
        prompt_path = f"prompts/{agent_name}/{prompt_version}.txt"
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(
                f"Prompt file '{prompt_version}' not found for agent '{agent_name}'"
            )

        # Load and return prompt
        with open(f"prompts/{agent_name}/{prompt_version}.txt") as f:
            return f.read()
