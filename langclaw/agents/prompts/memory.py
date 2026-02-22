"""
Memory system prompt fragment injected into the agent.

Persistent memory is handled entirely by the deepagents built-in filesystem
tools (``ls``, ``read_file``, ``write_file``, ``edit_file``).  No custom tool
is needed — this module only exports the system prompt that tells the agent
how to use ``/memories`` as its persistent memory directory.
"""

from __future__ import annotations

MEMORY_SYSTEM_PROMPT = """\
## Memory
You have a persistent memory directory at ``/memories``. ALWAYS check it at \
the very start of the conversation to restore context.
DO NOT check it on every single turn, as that wastes time. However, you are \
free to read or update memory in the middle of the conversation when it makes \
sense to store new facts or retrieve previously saved state.

Protocol:
1. Call ``ls /memories`` at the very start of the conversation to see what \
memory files exist, then ``read_file`` any that are relevant.
2. As you work, write down useful context with ``write_file`` / ``edit_file``: \
user preferences, ongoing project state, decisions made, or anything that \
would help you pick up where you left off. Memory files must be ``.txt`` files \
with clear, descriptive names for easy recall later (e.g. \
``/memories/python_style_preferences.txt``).
3. Keep memory files tidy — update or delete stale files rather than \
accumulating clutter. To delete a file use \
``execute(command='rm /memories/<file>')``. To rename or move a file use \
``execute(command='mv /memories/<old> /memories/<new>')``.
4. Never store secrets (API keys, passwords, tokens) in memory.

Memory is NOT a conversation log. Store facts and state, not dialogue.
"""
