"""
Custom exceptions for AI Agent.
"""


class AgentException(Exception):
    """Base exception for agent-related errors"""
    pass


class LLMException(AgentException):
    """Exception raised when LLM API call fails"""
    def __init__(self, message: str, provider: str = None, status_code: int = None):
        self.provider = provider
        self.status_code = status_code
        super().__init__(message)


class ToolException(AgentException):
    """Exception raised when a tool execution fails"""
    def __init__(self, message: str, tool_name: str = None):
        self.tool_name = tool_name
        super().__init__(message)


class ConfigException(AgentException):
    """Exception raised for configuration errors"""
    pass


class SearchException(ToolException):
    """Exception raised when web search fails"""
    def __init__(self, message: str):
        super().__init__(message, tool_name="web_search")


class ParseException(AgentException):
    """Exception raised when parsing LLM response fails"""
    pass
