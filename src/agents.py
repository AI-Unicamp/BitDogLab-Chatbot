import os
from abc import ABC, abstractmethod

import torch
from PIL import Image
from qwen_vl_utils import process_vision_info
from transformers import (
    AutoModelForCausalLM,
    AutoProcessor,
    AutoTokenizer,
    Qwen2_5_VLForConditionalGeneration,
)

from prompt_loader import PromptLoader

# Workaround for torch.classes
torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)]

READER_SYS_PROMPT = PromptLoader.load_prompt("flowchart_reader", "v1-en")
CODER_SYS_PROMPT = PromptLoader.load_prompt("coder", "v1-pt-bih")


# === Abstract Agent Base ===
class Agent(ABC):
    """Abstract base class for defining agents."""

    @abstractmethod
    def run(self, **kwargs) -> str:
        """Run the agent with the given input and return the output."""
        pass


# === Reader agent: image -> pseudocode ===
class Qwen25_VL(Agent):
    """
    Reader agent for generating pseudocode from an image.

    Uses model Qwen2.5-VL with 3B parameters for inference.
    """

    def __init__(self):
        model_name = "Qwen/Qwen2.5-VL-3B-Instruct"

        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name, torch_dtype="bfloat16", device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained(model_name)

    def run(self, image_path: str) -> str:
        """
        Runs the Reader agent with the given image (flowchart) and return the generated pseudocode.

        Args:
            image_path (str): The path to the flowchart image file.

        Returns:
            str: The generated pseudocode.
        """
        image = Image.open(image_path)
        prompt = [
            {"type": "image", "image": image},
        ]
        messages = [
            {"role": "system", "content": READER_SYS_PROMPT},
            {"role": "user", "content": prompt},
        ]

        # Preparation for inference
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to("cuda")

        # Inference: Generation of the output
        generated_ids = self.model.generate(**inputs, max_new_tokens=1024)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :]
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )[0]
        return output_text


# === Coder agent: pseudocode -> code ===
class Qwen25_Coder(Agent):
    """
    Coder agent for generating code from pseudocode or natural language input.

    Uses model Qwen2.5-Coder with 7B parameters for inference.
    """

    def __init__(self):
        model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype="bfloat16", device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def run(self, prompt: str) -> str:
        """
        Runs the Coder agent with the given prompt and return the generated code.

        Args:
            prompt (str): The prompt (e.g., pseudocode) to generate code from.

        Returns:
            str: The generated code.
        """
        messages = [
            {"role": "system", "content": CODER_SYS_PROMPT},
            {"role": "user", "content": prompt},
        ]
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to("cuda")

        generated_ids = self.model.generate(**model_inputs, max_new_tokens=1024)
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0]
        return response
