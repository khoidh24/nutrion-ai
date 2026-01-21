"""
Core AI Agent implementation with multi-provider LLM support.
"""

import json
import re
import httpx
from typing import AsyncGenerator, Optional
from dataclasses import dataclass, field

from config import LLMConfig, LLMProvider, get_system_prompt, SEARCH_CONFIG
from .exceptions import LLMException, ToolException, ParseException
from .tools import WebSearchTool, NutritionCalculator, AVAILABLE_TOOLS


@dataclass
class Message:
    """Represents a chat message"""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: list = field(default_factory=list)
    tool_call_id: Optional[str] = None


@dataclass 
class ToolCall:
    """Represents a tool call request"""
    id: str
    name: str
    arguments: dict


class FoodNutritionAgent:
    """
    AI Agent specialized in food and nutrition analysis.
    
    Features:
    - Multi-provider LLM support (Deepseek, Claude, OpenAI)
    - Web search capability
    - Nutrition calculation and lookup
    - Conversational interface
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.conversation_history: list[Message] = []
        
        # Initialize tools
        self.search_tool = WebSearchTool(
            api_key=SEARCH_CONFIG.get("serper_api_key"),
            max_results=SEARCH_CONFIG.get("max_results", 5)
        )
        self.nutrition_tool = NutritionCalculator()
        
        # Load system prompt
        self.system_prompt = get_system_prompt()
        
    def _get_headers(self) -> dict:
        """Get API headers based on provider"""
        headers = {"Content-Type": "application/json"}
        
        if self.config.provider == LLMProvider.CLAUDE:
            headers["x-api-key"] = self.config.api_key
            headers["anthropic-version"] = "2023-06-01"
        else:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
            
        return headers
    
    def _build_messages_from_history(self) -> list[dict]:
        """Build messages array for API call from conversation history.
        
        Only includes user and assistant messages (no tool interactions)
        to maintain compatibility across different LLM providers.
        """
        messages = []
        
        for msg in self.conversation_history:
            # Only include user and assistant messages (skip tool-related)
            if msg.role in ("user", "assistant") and not msg.tool_calls:
                messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })
        
        return messages
    
    def _build_tools_spec(self) -> list[dict]:
        """Build tools specification for API call"""
        tools = []
        
        for tool_info in AVAILABLE_TOOLS.values():
            if self.config.provider == LLMProvider.CLAUDE:
                tools.append({
                    "name": tool_info["name"],
                    "description": tool_info["description"],
                    "input_schema": tool_info["parameters"],
                })
            else:
                # OpenAI/Deepseek format
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool_info["name"],
                        "description": tool_info["description"],
                        "parameters": tool_info["parameters"],
                    }
                })
        
        return tools
    
    def _build_request_body(self, messages: list[dict], include_tools: bool = True) -> dict:
        """Build request body based on provider"""
        tools = self._build_tools_spec() if include_tools else []
        
        if self.config.provider == LLMProvider.CLAUDE:
            body = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "system": self.system_prompt,
                "messages": messages,
            }
            if tools:
                body["tools"] = tools
            return body
        else:
            # OpenAI/Deepseek format
            full_messages = [
                {"role": "system", "content": self.system_prompt}
            ] + messages
            
            body = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": full_messages,
            }
            if tools:
                body["tools"] = tools
                body["tool_choice"] = "auto"
            return body
    
    def _get_api_url(self) -> str:
        """Get API endpoint URL"""
        if self.config.provider == LLMProvider.CLAUDE:
            return f"{self.config.base_url}/messages"
        else:
            return f"{self.config.base_url}/chat/completions"
    
    def _parse_response(self, data: dict) -> tuple[str, list[ToolCall]]:
        """Parse API response and extract content and tool calls"""
        tool_calls = []
        content = ""
        
        if self.config.provider == LLMProvider.CLAUDE:
            # Claude format
            for block in data.get("content", []):
                if block["type"] == "text":
                    content += block["text"]
                elif block["type"] == "tool_use":
                    tool_calls.append(ToolCall(
                        id=block["id"],
                        name=block["name"],
                        arguments=block["input"],
                    ))
        else:
            # OpenAI/Deepseek format
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "") or ""
            
            for tc in message.get("tool_calls", []):
                func = tc.get("function", {})
                try:
                    args = json.loads(func.get("arguments", "{}"))
                except json.JSONDecodeError:
                    args = {}
                    
                tool_calls.append(ToolCall(
                    id=tc["id"],
                    name=func["name"],
                    arguments=args,
                ))
        
        return content, tool_calls
    
    async def _execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a tool and return result"""
        try:
            if tool_call.name == "web_search":
                query = tool_call.arguments.get("query", "")
                response = await self.search_tool.search(query)
                return self.search_tool.format_results(response)
                
            elif tool_call.name == "nutrition_lookup":
                food_name = tool_call.arguments.get("food_name", "")
                portion = tool_call.arguments.get("portion_grams", 100)
                
                data = self.nutrition_tool.lookup(food_name)
                if data:
                    return self.nutrition_tool.format_nutrition(food_name, data, portion)
                else:
                    return f"Không tìm thấy thông tin dinh dưỡng cho '{food_name}' trong cơ sở dữ liệu. Hãy sử dụng web_search để tìm kiếm thêm thông tin."
            
            else:
                return f"Unknown tool: {tool_call.name}"
                
        except Exception as e:
            return f"Tool error: {str(e)}"
    
    async def _call_llm(self, messages: list[dict], include_tools: bool = True) -> tuple[str, list[ToolCall]]:
        """Make API call to LLM"""
        url = self._get_api_url()
        headers = self._get_headers()
        body = self._build_request_body(messages, include_tools=include_tools)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=body,
                    timeout=60.0,
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    raise LLMException(
                        f"API error: {response.status_code} - {error_text}",
                        provider=self.config.provider.value,
                        status_code=response.status_code,
                    )
                
                data = response.json()
                return self._parse_response(data)
                
        except httpx.RequestError as e:
            raise LLMException(
                f"Request failed: {str(e)}",
                provider=self.config.provider.value,
            )
    
    async def chat(self, user_message: str, use_tools: bool = True) -> str:
        """
        Process a user message and return the agent's response.
        
        Tool interactions are handled within a single turn and NOT saved to history
        to avoid API compatibility issues with some providers.
        """
        # Save history length to rollback on error
        history_checkpoint = len(self.conversation_history)
        
        try:
            # Add user message to history
            self.conversation_history.append(Message(
                role="user",
                content=user_message,
            ))
            
            # Build base messages from history (user/assistant only)
            base_messages = self._build_messages_from_history()
            
            # Working messages for this turn (may include tool interactions)
            working_messages = list(base_messages)
            
            # Call LLM (with or without tools)
            content, tool_calls = await self._call_llm(working_messages, include_tools=use_tools)
            
            # Process tool calls if any (within this turn only)
            max_iterations = 5
            iteration = 0
            tool_context = []  # Collect tool results as context
            
            while tool_calls and iteration < max_iterations:
                iteration += 1
                
                # Execute tools and collect results
                for tc in tool_calls:
                    result = await self._execute_tool(tc)
                    tool_context.append(f"[Tool: {tc.name}]\n{result}")
                
                # Build context message with tool results
                context_msg = "\n\n".join(tool_context)
                
                # Create new messages with tool context injected
                enhanced_messages = list(base_messages)
                # Inject tool results as system context in the last user message
                if enhanced_messages and enhanced_messages[-1]["role"] == "user":
                    original_content = enhanced_messages[-1]["content"]
                    enhanced_messages[-1] = {
                        "role": "user",
                        "content": f"{original_content}\n\n---\n📊 Thông tin tra cứu được:\n{context_msg}"
                    }
                
                # Call LLM again without tools (to get final response)
                content, tool_calls = await self._call_llm(enhanced_messages, include_tools=False)
            
            # Add final assistant response to history
            self.conversation_history.append(Message(
                role="assistant",
                content=content,
            ))
            
            return content
            
        except LLMException as e:
            # Rollback history on error
            self.conversation_history = self.conversation_history[:history_checkpoint]
            
            # If tools caused error, retry without tools
            if use_tools and "tool" in str(e).lower():
                return await self.chat(user_message, use_tools=False)
            raise
            
        except Exception as e:
            # Rollback history on error to keep it clean
            self.conversation_history = self.conversation_history[:history_checkpoint]
            raise
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self) -> list[dict]:
        """Get conversation history as list of dicts"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
            if msg.role in ("user", "assistant")
        ]
