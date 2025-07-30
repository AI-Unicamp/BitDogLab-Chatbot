from langchain_core.runnables import RunnableLambda

from agents import Qwen25_Coder, Qwen25_VL


class AgentCoordinator:
    """Coordinates the execution of agents based on user input."""

    def __init__(self):
        print("[Coordinator] Initializing Reader agent...")
        self.reader = Qwen25_VL()
        self.reader_runnable = RunnableLambda(self.reader.run)

        print("[Coordinator] Initializing Coder agent...")
        self.coder = Qwen25_Coder()
        self.coder_runnable = RunnableLambda(self.coder.run)

    def handle_input(self, uploaded_file: str | None, pseudocode_text: str):
        """
        Handles user input and calls the appropriate agent.

        Args:
            uploaded_file (str | None): The uploaded image file, if any.
            pseudocode_text (str): The text of the pseudocode, if any.

        Returns:
            str: The generated code or pseudocode.
        """
        if uploaded_file:
            print("[Coordinator] Detected image input, calling Reader agent.")
            pseudocode = self.reader_runnable.invoke(uploaded_file)
            return pseudocode
        elif pseudocode_text.strip():
            print("[Coordinator] Detected pseudocode input, calling Coder agent.")
            code = self.coder_runnable.invoke(pseudocode_text)
            return code

    def generate_code(self, pseudocode: str):
        """
        Generates code from pseudocode.

        Args:
            pseudocode (str): The pseudocode to generate code from.

        Returns:
            str: The generated code.
        """
        print("[Coordinator] Calling Coder agent.")
        code = self.coder_runnable.invoke(pseudocode)
        return code
