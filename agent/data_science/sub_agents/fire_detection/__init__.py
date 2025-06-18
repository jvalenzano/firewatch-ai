"""
Fire Detection Sub-Agent using NASA FIRMS API

Phase III Sprint 1 - Real-time active fire detection
Built on Phase II optimized foundation
"""

from .nasa_firms import NASAFIRMSClient, ActiveFire
from .agent import fire_detection_agent

__all__ = ['NASAFIRMSClient', 'ActiveFire', 'fire_detection_agent']