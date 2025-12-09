"""Integration Components Module
Contains integration components for connecting the AlphaAxiom Learning Loop v2.0
with the existing system infrastructure.

Status: LIVE as of December 9, 2025
"""

from .worker_bridge import LearningLoopBridge, LoopStatus

__all__ = ['LearningLoopBridge', 'LoopStatus']