"""
Food Nutrition AI Agent - Main Entry Point

An intelligent AI assistant specialized in analyzing food nutrition,
calculating calories, protein, fat, and providing dietary recommendations.
"""

import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from config import get_llm_config, LLMProvider
from agent_core import FoodNutritionAgent, LLMException

console = Console()


def print_welcome():
    """Print welcome message"""
    welcome_text = """
# 🍽️ Food Nutrition AI Agent

Xin chào! Tôi là trợ lý AI chuyên về phân tích dinh dưỡng thực phẩm.

## Tôi có thể giúp bạn:
- 📊 Phân tích calories, protein, chất béo của món ăn
- 🔍 Tìm kiếm thông tin dinh dưỡng trên web
- 🥗 So sánh giá trị dinh dưỡng giữa các món
- 💡 Gợi ý món ăn healthy thay thế
- 🍲 Tính tổng dinh dưỡng cho cả bữa ăn

**Gõ câu hỏi và nhấn Enter để bắt đầu!**
**Gõ 'quit' hoặc 'exit' để thoát.**
**Gõ 'clear' để xóa lịch sử hội thoại.**
    """
    console.print(Panel(Markdown(welcome_text), border_style="green"))


def print_response(response: str):
    """Print agent response with formatting"""
    console.print()
    console.print(Panel(
        Markdown(response),
        title="🤖 AI Agent",
        border_style="blue",
    ))
    console.print()


def print_error(error: str):
    """Print error message"""
    console.print(f"[red]❌ Error: {error}[/red]")


async def main():
    """Main function to run the agent"""
    print_welcome()
    
    # Initialize agent
    try:
        config = get_llm_config()
        console.print(f"[dim]Using LLM: {config.provider.value} ({config.model})[/dim]\n")
        agent = FoodNutritionAgent(config)
    except ValueError as e:
        print_error(str(e))
        console.print("\n[yellow]Hướng dẫn setup:[/yellow]")
        console.print("1. Tạo file .env từ .env.example")
        console.print("2. Thêm MODEL_API_KEY vào file .env")
        console.print("3. (Tùy chọn) Thêm SERPER_API_KEY cho tính năng search web")
        return
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold green]Bạn[/bold green]")
            
            # Handle commands
            if user_input.lower() in ('quit', 'exit', 'q'):
                console.print("[dim]Tạm biệt! 👋[/dim]")
                break
            
            if user_input.lower() == 'clear':
                agent.clear_history()
                console.print("[dim]Đã xóa lịch sử hội thoại.[/dim]")
                continue
            
            if not user_input.strip():
                continue
            
            # Process message
            with console.status("[bold blue]Đang suy nghĩ...", spinner="dots"):
                response = await agent.chat(user_input)
            
            print_response(response)
            
        except LLMException as e:
            print_error(f"LLM Error: {e}")
        except KeyboardInterrupt:
            console.print("\n[dim]Tạm biệt! 👋[/dim]")
            break
        except Exception as e:
            print_error(str(e))


def run():
    """Entry point for running the agent"""
    asyncio.run(main())


if __name__ == "__main__":
    run()
