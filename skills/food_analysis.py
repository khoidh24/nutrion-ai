"""
Food Analysis Skills - Specialized skills for food and nutrition analysis.
"""

from .registry import registry


@registry.register(
    name="analyze_nutrition",
    description="Phân tích chi tiết thông tin dinh dưỡng của món ăn bao gồm calories, protein, chất béo, carbohydrates",
    examples=[
        "Phân tích dinh dưỡng phở bò",
        "Calories trong 1 bát cơm",
        "Thông tin dinh dưỡng của trứng chiên",
    ],
    tags=["nutrition", "food", "analysis"]
)
async def analyze_nutrition(food_name: str, portion_grams: int = 100) -> dict:
    """
    Analyze nutrition information for a food item.
    
    Returns dict with:
    - calories: kcal
    - protein: grams
    - fat: grams  
    - carbs: grams
    - fiber: grams (if available)
    - sodium: mg (if available)
    """
    # This is a placeholder - actual implementation is in the agent's tools
    return {
        "food": food_name,
        "portion": portion_grams,
        "status": "Use agent.chat() for full analysis"
    }


@registry.register(
    name="compare_foods",
    description="So sánh thông tin dinh dưỡng giữa các món ăn",
    examples=[
        "So sánh cơm trắng và bún",
        "Thịt gà vs thịt bò",
        "Đồ ăn nào ít calories hơn",
    ],
    tags=["nutrition", "food", "comparison"]
)
async def compare_foods(food_a: str, food_b: str) -> dict:
    """Compare nutrition between two foods"""
    return {
        "food_a": food_a,
        "food_b": food_b,
        "status": "Use agent.chat() for full comparison"
    }


@registry.register(
    name="suggest_healthy_alternatives",
    description="Gợi ý các món ăn thay thế lành mạnh hơn",
    examples=[
        "Món gì thay thế cơm để giảm carbs?",
        "Đồ ăn vặt healthy thay cho bánh ngọt",
    ],
    tags=["nutrition", "food", "healthy", "suggestion"]
)
async def suggest_healthy_alternatives(current_food: str, goal: str = None) -> dict:
    """Suggest healthier food alternatives"""
    return {
        "current_food": current_food,
        "goal": goal,
        "status": "Use agent.chat() for suggestions"
    }


@registry.register(
    name="calculate_meal_nutrition",
    description="Tính tổng dinh dưỡng của một bữa ăn gồm nhiều món",
    examples=[
        "Tính calories bữa sáng: phở + nước mía",
        "Dinh dưỡng bữa trưa gồm cơm, thịt kho, canh",
    ],
    tags=["nutrition", "food", "meal", "calculation"]
)
async def calculate_meal_nutrition(foods: list[str]) -> dict:
    """Calculate total nutrition for a meal with multiple items"""
    return {
        "foods": foods,
        "status": "Use agent.chat() for meal calculation"
    }
