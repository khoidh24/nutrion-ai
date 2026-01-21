"""
Tools for AI Agent including web search capability.
"""

import json
import httpx
from typing import Optional
from dataclasses import dataclass

from .exceptions import SearchException, ToolException


@dataclass
class SearchResult:
    """Represents a single search result"""
    title: str
    link: str
    snippet: str
    position: int


@dataclass
class SearchResponse:
    """Represents the complete search response"""
    query: str
    results: list[SearchResult]
    

class WebSearchTool:
    """
    Web search tool using Serper API (Google Search).
    
    Get your API key at: https://serper.dev/
    """
    
    SERPER_URL = "https://google.serper.dev/search"
    
    def __init__(self, api_key: str, max_results: int = 5):
        self.api_key = api_key
        self.max_results = max_results
        
    async def search(self, query: str, num_results: Optional[int] = None) -> SearchResponse:
        """
        Perform a web search.
        
        Args:
            query: Search query string
            num_results: Number of results to return (default: max_results)
            
        Returns:
            SearchResponse with list of results
        """
        if not self.api_key:
            raise SearchException(
                "SERPER_API_KEY is not configured. "
                "Get your API key at https://serper.dev/"
            )
        
        num = num_results or self.max_results
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        
        payload = {
            "q": query,
            "num": num,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.SERPER_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                
        except httpx.HTTPStatusError as e:
            raise SearchException(f"Search API error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise SearchException(f"Search request failed: {str(e)}")
        except json.JSONDecodeError:
            raise SearchException("Failed to parse search response")
        
        # Parse results
        results = []
        organic = data.get("organic", [])
        
        for i, item in enumerate(organic[:num], 1):
            results.append(SearchResult(
                title=item.get("title", ""),
                link=item.get("link", ""),
                snippet=item.get("snippet", ""),
                position=i,
            ))
        
        return SearchResponse(query=query, results=results)
    
    def format_results(self, response: SearchResponse) -> str:
        """Format search results as readable text for the LLM"""
        if not response.results:
            return f"No results found for: {response.query}"
        
        lines = [f"🔍 Search results for: {response.query}\n"]
        
        for result in response.results:
            lines.append(f"**{result.position}. {result.title}**")
            lines.append(f"   URL: {result.link}")
            lines.append(f"   {result.snippet}")
            lines.append("")
        
        return "\n".join(lines)


class NutritionCalculator:
    """
    Tool for calculating nutritional information of foods.
    Uses a basic database + web search for unknown foods.
    """
    
    # Basic nutrition data per 100g (calories, protein_g, fat_g, carbs_g)
    FOOD_DATABASE = {
        "cơm trắng": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
        "thịt gà": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
        "thịt bò": {"calories": 250, "protein": 26, "fat": 15, "carbs": 0},
        "thịt heo": {"calories": 242, "protein": 27, "fat": 14, "carbs": 0},
        "cá hồi": {"calories": 208, "protein": 20, "fat": 13, "carbs": 0},
        "trứng gà": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
        "đậu phụ": {"calories": 76, "protein": 8, "fat": 4.8, "carbs": 1.9},
        "rau muống": {"calories": 19, "protein": 2.6, "fat": 0.2, "carbs": 3.1},
        "cà chua": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
        "phở bò": {"calories": 215, "protein": 15, "fat": 5, "carbs": 28},
        "bánh mì": {"calories": 265, "protein": 9, "fat": 3.2, "carbs": 49},
        "bún chả": {"calories": 350, "protein": 20, "fat": 15, "carbs": 35},
    }
    
    def lookup(self, food_name: str) -> dict | None:
        """Look up nutrition info from database"""
        food_lower = food_name.lower().strip()
        
        # Direct match
        if food_lower in self.FOOD_DATABASE:
            return self.FOOD_DATABASE[food_lower]
        
        # Partial match
        for key, value in self.FOOD_DATABASE.items():
            if key in food_lower or food_lower in key:
                return value
        
        return None
    
    def format_nutrition(self, food_name: str, data: dict, portion_grams: int = 100) -> str:
        """Format nutrition info as readable text"""
        multiplier = portion_grams / 100
        
        return f"""
📊 **Thông tin dinh dưỡng: {food_name}** (khẩu phần {portion_grams}g)

| Chỉ số | Giá trị |
|--------|---------|
| 🔥 Calories | {data['calories'] * multiplier:.1f} kcal |
| 💪 Protein (Chất đạm) | {data['protein'] * multiplier:.1f} g |
| 🧈 Fat (Chất béo) | {data['fat'] * multiplier:.1f} g |
| 🍚 Carbs (Tinh bột) | {data['carbs'] * multiplier:.1f} g |
"""


# Tool registry
AVAILABLE_TOOLS = {
    "web_search": {
        "name": "web_search",
        "description": "Tìm kiếm thông tin trên web. Sử dụng khi cần thông tin cập nhật về món ăn, công thức, hoặc dinh dưỡng.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Từ khóa tìm kiếm"
                }
            },
            "required": ["query"]
        }
    },
    "nutrition_lookup": {
        "name": "nutrition_lookup", 
        "description": "Tra cứu thông tin dinh dưỡng của món ăn từ cơ sở dữ liệu.",
        "parameters": {
            "type": "object",
            "properties": {
                "food_name": {
                    "type": "string",
                    "description": "Tên món ăn cần tra cứu"
                },
                "portion_grams": {
                    "type": "integer",
                    "description": "Khẩu phần tính bằng gram (mặc định 100g)"
                }
            },
            "required": ["food_name"]
        }
    }
}


def get_tools_prompt() -> str:
    """Generate tools description for system prompt"""
    tools_desc = ["## Công cụ có sẵn:\n"]
    
    for tool_name, tool_info in AVAILABLE_TOOLS.items():
        tools_desc.append(f"### {tool_name}")
        tools_desc.append(f"{tool_info['description']}\n")
    
    return "\n".join(tools_desc)
