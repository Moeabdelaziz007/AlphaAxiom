"""
🎙️ Voice Module - Edge-TTS Integration
AlphaAxiom Trading System v2.0

نظام تحويل النص إلى صوت باستخدام Microsoft Edge TTS
يدعم 15+ لهجة عربية بدون تكلفة

Components:
- EdgeTTSGateway: تحويل التنبيهات إلى صوت
- VoicePresets: الأصوات العربية المحددة مسبقاً

Status: BETA as of December 9, 2025
"""

from .edge_tts_gateway import EdgeTTSGateway, VoicePreset

__all__ = ['EdgeTTSGateway', 'VoicePreset']
