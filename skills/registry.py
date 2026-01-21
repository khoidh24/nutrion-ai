"""
Skills Registry - Register and manage agent skills.
"""

from typing import Callable, Any
from dataclasses import dataclass, field


@dataclass
class Skill:
    """Represents a skill/capability of the agent"""
    name: str
    description: str
    handler: Callable
    examples: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


class SkillRegistry:
    """
    Registry for managing agent skills.
    
    Skills are specialized capabilities that the agent can use
    to handle specific types of requests.
    """
    
    def __init__(self):
        self._skills: dict[str, Skill] = {}
    
    def register(
        self,
        name: str,
        description: str,
        examples: list[str] = None,
        tags: list[str] = None,
    ):
        """
        Decorator to register a skill.
        
        Usage:
            @registry.register(
                name="analyze_food",
                description="Phân tích thông tin dinh dưỡng món ăn",
                examples=["Phân tích phở bò", "Calories trong cơm gà"],
                tags=["nutrition", "food"]
            )
            async def analyze_food(query: str) -> str:
                ...
        """
        def decorator(func: Callable) -> Callable:
            self._skills[name] = Skill(
                name=name,
                description=description,
                handler=func,
                examples=examples or [],
                tags=tags or [],
            )
            return func
        return decorator
    
    def get(self, name: str) -> Skill | None:
        """Get a skill by name"""
        return self._skills.get(name)
    
    def list_skills(self) -> list[Skill]:
        """List all registered skills"""
        return list(self._skills.values())
    
    def get_by_tag(self, tag: str) -> list[Skill]:
        """Get skills by tag"""
        return [s for s in self._skills.values() if tag in s.tags]
    
    def generate_prompt(self) -> str:
        """Generate skills description for prompts"""
        lines = ["## Kỹ năng có sẵn:\n"]
        
        for skill in self._skills.values():
            lines.append(f"### {skill.name}")
            lines.append(f"{skill.description}")
            
            if skill.examples:
                lines.append("\n**Ví dụ:**")
                for ex in skill.examples:
                    lines.append(f"- {ex}")
            
            lines.append("")
        
        return "\n".join(lines)


# Global registry instance
registry = SkillRegistry()
