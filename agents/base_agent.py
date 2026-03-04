"""
Base agent loop: handles the Claude streaming tool_use agentic loop.
Yields AgentEvent objects so the UI layer can render them live.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Generator, Literal
import json
import anthropic

from config import get_api_key, MODEL_NAME, MAX_AGENT_ITERATIONS, MAX_TOKENS


@dataclass
class AgentEvent:
    type: Literal["thinking", "tool_call", "tool_result", "complete", "error"]
    data: Any


def run_agent(
    system_prompt: str,
    user_message: str,
    tools: list[dict],
    tool_registry: dict[str, callable],
) -> Generator[AgentEvent, None, None]:
    """
    Runs the Claude agentic loop with tool_use.
    Yields AgentEvent objects for each step so UIs can render live.

    Args:
        system_prompt: The agent's system instructions.
        user_message: The user's input to the agent.
        tools: List of tool definitions (JSON schema format for Claude).
        tool_registry: Dict mapping tool name -> Python callable.

    Yields:
        AgentEvent with types:
            "thinking"    — text chunk from Claude's reasoning
            "tool_call"   — {"name": str, "inputs": dict, "tool_use_id": str}
            "tool_result" — {"name": str, "result": Any, "tool_use_id": str}
            "complete"    — final text response from Claude
            "error"       — error message string
    """
    client = anthropic.Anthropic(api_key=get_api_key())
    messages = [{"role": "user", "content": user_message}]

    for iteration in range(MAX_AGENT_ITERATIONS):
        try:
            # Stream the response
            with client.messages.stream(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                messages=messages,
                tools=tools,
            ) as stream:
                # Yield text chunks as they arrive
                for event in stream:
                    if (
                        event.type == "content_block_delta"
                        and hasattr(event.delta, "type")
                        and event.delta.type == "text_delta"
                    ):
                        yield AgentEvent(type="thinking", data=event.delta.text)

                final_message = stream.get_final_message()

            # Append assistant turn to message history
            messages.append({"role": "assistant", "content": final_message.content})

            # If Claude is done (no more tool calls), yield final text and stop
            if final_message.stop_reason == "end_turn":
                final_text = ""
                for block in final_message.content:
                    if hasattr(block, "text"):
                        final_text = block.text
                        break
                yield AgentEvent(type="complete", data=final_text)
                return

            # Process tool calls
            tool_results = []
            for block in final_message.content:
                if block.type != "tool_use":
                    continue

                tool_name = block.name
                tool_inputs = block.input
                tool_use_id = block.id

                yield AgentEvent(
                    type="tool_call",
                    data={"name": tool_name, "inputs": tool_inputs, "tool_use_id": tool_use_id},
                )

                # Execute the tool
                if tool_name not in tool_registry:
                    result = {"error": f"Unknown tool: {tool_name}"}
                else:
                    try:
                        result = tool_registry[tool_name](**tool_inputs)
                    except Exception as e:
                        result = {"error": str(e)}

                yield AgentEvent(
                    type="tool_result",
                    data={"name": tool_name, "result": result, "tool_use_id": tool_use_id},
                )

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": json.dumps(result, default=str),
                })

            # Send tool results back to Claude
            messages.append({"role": "user", "content": tool_results})

        except anthropic.APIError as e:
            yield AgentEvent(type="error", data=f"API error: {str(e)}")
            return
        except Exception as e:
            yield AgentEvent(type="error", data=f"Unexpected error: {str(e)}")
            return

    yield AgentEvent(type="error", data="Max iterations reached without completion.")
