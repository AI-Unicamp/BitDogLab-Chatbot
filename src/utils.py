import re
from typing import Tuple


def split_code_fences(code: str) -> Tuple[str | None, str, str | None]:
    """
    Splits a string into three parts: text before the code fence, the code block, and text after.

    Returns:
        A tuple (prefix, code, suffix), where prefix and suffix are None if not present.
    """
    pattern = re.compile(r"^(.*?)```[a-zA-Z]*\n?(.*?)\n?```(.*)$", re.DOTALL)
    match = pattern.match(code.strip())
    if not match:
        # No code fence found — return full string as code
        return (None, code.strip(), None)

    before, code_block, after = match.groups()

    prefix = before.strip() or None
    code = code_block.strip()
    suffix = after.strip() or None

    return (prefix, code, suffix)
