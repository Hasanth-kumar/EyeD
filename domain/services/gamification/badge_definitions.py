"""
Badge definitions value object.

Contains immutable badge criteria and configuration for the gamification system.
This is a pure value object with no dependencies on infrastructure.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class BadgeDefinition:
    """
    Immutable badge definition.
    
    Attributes:
        name: Display name of the badge.
        criteria: Required count/threshold to earn the badge.
        type: Type of badge (e.g., 'weekly', 'monthly', 'total', 'consecutive').
        description: Description of what the badge represents.
    """
    name: str
    criteria: int
    type: str
    description: str


@dataclass(frozen=True)
class BadgeDefinitions:
    """
    Immutable value object containing all badge definitions.
    
    This object contains the configuration for all badge types in the system.
    It is immutable and can be safely shared across the application.
    
    Attributes:
        attendance: Dictionary of attendance badge definitions.
        streak: Dictionary of streak badge definitions.
        timing: Dictionary of timing badge definitions.
        quality: Dictionary of quality badge definitions.
    """
    attendance: Dict[str, BadgeDefinition]
    streak: Dict[str, BadgeDefinition]
    timing: Dict[str, BadgeDefinition]
    quality: Dict[str, BadgeDefinition]
    
    @classmethod
    def default(cls) -> 'BadgeDefinitions':
        """
        Create default badge definitions.
        
        Returns:
            BadgeDefinitions instance with default badge configurations.
        """
        return cls(
            attendance={
                'perfect_week': BadgeDefinition(
                    name='🌟 Perfect Week',
                    criteria=5,
                    type='weekly',
                    description='Attended all 5 days in a week'
                ),
                'perfect_month': BadgeDefinition(
                    name='🏆 Perfect Month',
                    criteria=20,
                    type='monthly',
                    description='Attended 20 days in a month'
                ),
                'consistency_master': BadgeDefinition(
                    name='📅 Consistency Master',
                    criteria=50,
                    type='total',
                    description='Accumulated 50 total attendance entries'
                ),
                'dedication_champion': BadgeDefinition(
                    name='💪 Dedication Champion',
                    criteria=100,
                    type='total',
                    description='Accumulated 100 total attendance entries'
                )
            },
            streak={
                'week_warrior': BadgeDefinition(
                    name='🔥 Week Warrior',
                    criteria=7,
                    type='consecutive',
                    description='Maintained a 7-day consecutive attendance streak'
                ),
                'month_master': BadgeDefinition(
                    name='📆 Month Master',
                    criteria=30,
                    type='consecutive',
                    description='Maintained a 30-day consecutive attendance streak'
                ),
                'streak_legend': BadgeDefinition(
                    name='⚡ Streak Legend',
                    criteria=60,
                    type='consecutive',
                    description='Maintained a 60-day consecutive attendance streak'
                )
            },
            timing={
                'early_bird': BadgeDefinition(
                    name='🐦 Early Bird',
                    criteria=5,
                    type='early_arrivals',
                    description='Arrived before 8 AM on 5 occasions'
                ),
                'punctuality_pro': BadgeDefinition(
                    name='⏰ Punctuality Pro',
                    criteria=10,
                    type='on_time',
                    description='Arrived on time (9:00-9:15 AM) on 10 occasions'
                ),
                'time_master': BadgeDefinition(
                    name='⌚ Time Master',
                    criteria=20,
                    type='consistent_timing',
                    description='Maintained consistent arrival times on 20 occasions'
                )
            },
            quality={
                'quality_seeker': BadgeDefinition(
                    name='📸 Quality Seeker',
                    criteria=5,
                    type='high_quality',
                    description='Achieved high quality face recognition (≥0.8) on 5 occasions'
                ),
                'quality_master': BadgeDefinition(
                    name='🎯 Quality Master',
                    criteria=15,
                    type='high_quality',
                    description='Achieved high quality face recognition (≥0.8) on 15 occasions'
                ),
                'perfectionist': BadgeDefinition(
                    name='✨ Perfectionist',
                    criteria=30,
                    type='high_quality',
                    description='Achieved high quality face recognition (≥0.8) on 30 occasions'
                )
            }
        )















