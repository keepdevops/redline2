#!/usr/bin/env python3
"""
REDLINE Massive.com WebSocket Client
Supports both delayed (15-min) and real-time feeds.
"""

import asyncio
import json
import logging
import pandas as pd
from typing import Callable, Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import websockets library
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    websockets = None
    logger.warning("websockets library not available. Install with: pip install websockets")

class MassiveWebSocketClient:
    """WebSocket client for Massive.com delayed and real-time data."""
    
    # WebSocket endpoints
    DELAYED_WS_URL = "wss://delayed.massive.com/stocks"  # 15-minute delayed feed
    REALTIME_WS_URL = "wss://socket.massive.com"  # Real-time feed (may require paid plan)
    
    def __init__(self, api_key: str, use_delayed: bool = True, callback: Optional[Callable] = None):
        """
        Initialize WebSocket client.
        
        Args:
            api_key: Massive.com API key
            use_delayed: Use 15-minute delayed feed (True) or real-time feed (False)
            callback: Optional callback function for received data
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets library required. Install with: pip install websockets")
        
        self.api_key = api_key
        self.use_delayed = use_delayed
        self.callback = callback
        self.ws_url = self.DELAYED_WS_URL if use_delayed else self.REALTIME_WS_URL
        self.connected = False
        self.websocket = None
        self.subscribed_tickers = []
        
    async def connect(self, tickers: List[str]):
        """
        Connect and subscribe to tickers.
        
        Args:
            tickers: List of ticker symbols to subscribe to
        """
        if not tickers:
            raise ValueError("At least one ticker is required")
        
        feed_type = "15-minute delayed" if self.use_delayed else "real-time"
        logger.info(f"Connecting to Massive.com {feed_type} WebSocket feed...")
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            self.websocket = await websockets.connect(self.ws_url, extra_headers=headers)
            self.connected = True
            logger.info(f"Connected to {feed_type} feed")
            
            # Subscribe to tickers
            subscribe_msg = {"action": "subscribe", "tickers": tickers}
            await self.websocket.send(json.dumps(subscribe_msg))
            self.subscribed_tickers = tickers
            logger.info(f"Subscribed to {len(tickers)} tickers: {', '.join(tickers)}")
            
            # Listen for messages
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse WebSocket message: {e}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    
        except websockets.exceptions.InvalidStatusCode as e:
            if e.status_code == 401:
                raise ValueError("Invalid API key or unauthorized access")
            raise
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            raise
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket messages."""
        try:
            if self.callback:
                # Convert to DataFrame
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    df = pd.DataFrame([data])
                else:
                    logger.warning(f"Unexpected data format: {type(data)}")
                    return
                
                # Call callback
                if asyncio.iscoroutinefunction(self.callback):
                    await self.callback(df)
                else:
                    self.callback(df)
            else:
                logger.info(f"Received data: {data}")
        except Exception as e:
            logger.error(f"Error in message handler: {e}")
    
    async def unsubscribe(self, tickers: List[str]):
        """Unsubscribe from tickers."""
        if not self.connected or not self.websocket:
            return
        
        unsubscribe_msg = {"action": "unsubscribe", "tickers": tickers}
        await self.websocket.send(json.dumps(unsubscribe_msg))
        self.subscribed_tickers = [t for t in self.subscribed_tickers if t not in tickers]
        logger.info(f"Unsubscribed from {len(tickers)} tickers")
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        if self.websocket:
            await self.websocket.close()
        self.connected = False
        logger.info("Disconnected from WebSocket")
    
    async def run(self, tickers: List[str], duration: Optional[int] = None):
        """
        Run WebSocket connection for specified duration.
        
        Args:
            tickers: List of tickers to subscribe to
            duration: Duration in seconds (None for indefinite)
        """
        try:
            if duration:
                await asyncio.wait_for(self.connect(tickers), timeout=duration)
            else:
                await self.connect(tickers)
        except asyncio.TimeoutError:
            logger.info(f"WebSocket connection timeout after {duration} seconds")
        finally:
            await self.disconnect()
    
    def get_feed_info(self) -> Dict[str, Any]:
        """Get information about the current feed."""
        return {
            "feed_type": "15-minute delayed" if self.use_delayed else "real-time",
            "url": self.ws_url,
            "connected": self.connected,
            "subscribed_tickers": self.subscribed_tickers.copy(),
            "endpoint": self.DELAYED_WS_URL if self.use_delayed else self.REALTIME_WS_URL
        }
    
    @staticmethod
    async def test_connection(api_key: str, use_delayed: bool = True) -> bool:
        """
        Test WebSocket connection without subscribing.
        
        Args:
            api_key: Massive.com API key
            use_delayed: Test delayed feed (True) or real-time (False)
            
        Returns:
            True if connection successful, False otherwise
        """
        if not WEBSOCKETS_AVAILABLE:
            return False
        
        try:
            ws_url = MassiveWebSocketClient.DELAYED_WS_URL if use_delayed else MassiveWebSocketClient.REALTIME_WS_URL
            headers = {"Authorization": f"Bearer {api_key}"}
            async with websockets.connect(ws_url, extra_headers=headers) as ws:
                return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.connected and self.websocket is not None
    
    def get_subscribed_count(self) -> int:
        """Get number of subscribed tickers."""
        return len(self.subscribed_tickers)
    
    async def reconnect(self, tickers: List[str]):
        """Reconnect to WebSocket and resubscribe."""
        await self.disconnect()
        await self.connect(tickers)
