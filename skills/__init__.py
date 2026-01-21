"""
Skills Module
"""

from .registry import registry, SkillRegistry, Skill
from . import food_analysis  # Import to register skills

__all__ = [
    "registry",
    "SkillRegistry", 
    "Skill",
]
