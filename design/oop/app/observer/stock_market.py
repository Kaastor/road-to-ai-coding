"""Stock market simulator implementing the Subject pattern."""

import logging
import threading
import time
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional
from .subject import Subject


class Stock:
    """Represents a stock with symbol, price, and metadata."""
    
    def __init__(self, symbol: str, price: Decimal, volume: int = 0) -> None:
        """Initialize a stock.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
            price: Current stock price
            volume: Trading volume
        """
        self.symbol = symbol
        self.price = price
        self.volume = volume
        self.last_updated = datetime.now()
        self.previous_price: Optional[Decimal] = None
    
    def update_price(self, new_price: Decimal, volume: int = 0) -> bool:
        """Update stock price and return True if price changed.
        
        Args:
            new_price: New stock price
            volume: Trading volume for this update
            
        Returns:
            True if price changed, False otherwise
        """
        if new_price != self.price:
            self.previous_price = self.price
            self.price = new_price
            self.volume = volume
            self.last_updated = datetime.now()
            return True
        return False
    
    @property
    def price_change(self) -> Optional[Decimal]:
        """Get the price change from previous price."""
        if self.previous_price is not None:
            return self.price - self.previous_price
        return None
    
    @property
    def price_change_percent(self) -> Optional[Decimal]:
        """Get the price change percentage."""
        if self.previous_price is not None and self.previous_price != 0:
            return ((self.price - self.previous_price) / self.previous_price) * 100
        return None


class StockMarket(Subject):
    """Stock market simulator that notifies observers of price changes.
    
    This class extends Subject to provide stock market specific functionality
    including stock tracking, price updates, and market statistics.
    """
    
    def __init__(self, name: str = "StockMarket") -> None:
        """Initialize the stock market.
        
        Args:
            name: Name of the stock market
        """
        super().__init__(name)
        self._stocks: Dict[str, Stock] = {}
        self._market_lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.{self._name}")
        self._is_market_open = False
        
    def add_stock(self, symbol: str, initial_price: Decimal, volume: int = 0) -> None:
        """Add a new stock to the market.
        
        Args:
            symbol: Stock symbol
            initial_price: Initial stock price
            volume: Initial trading volume
            
        Raises:
            ValueError: If stock already exists
        """
        with self._market_lock:
            if symbol in self._stocks:
                raise ValueError(f"Stock {symbol} already exists in the market")
            
            self._stocks[symbol] = Stock(symbol, initial_price, volume)
            self._logger.info(f"Added stock {symbol} with initial price ${initial_price}")
    
    def remove_stock(self, symbol: str) -> None:
        """Remove a stock from the market.
        
        Args:
            symbol: Stock symbol to remove
            
        Raises:
            KeyError: If stock doesn't exist
        """
        with self._market_lock:
            if symbol not in self._stocks:
                raise KeyError(f"Stock {symbol} not found in the market")
            
            del self._stocks[symbol]
            self._logger.info(f"Removed stock {symbol} from market")
    
    def update_stock_price(self, symbol: str, new_price: Decimal, volume: int = 0) -> None:
        """Update stock price and notify observers if price changed.
        
        Args:
            symbol: Stock symbol to update
            new_price: New price for the stock
            volume: Trading volume
            
        Raises:
            KeyError: If stock doesn't exist
        """
        with self._market_lock:
            if symbol not in self._stocks:
                raise KeyError(f"Stock {symbol} not found in the market")
            
            stock = self._stocks[symbol]
            price_changed = stock.update_price(new_price, volume)
        
        # Notify outside the lock to prevent deadlocks
        if price_changed:
            self._logger.info(f"Stock {symbol} price updated: ${new_price} (volume: {volume})")
            self.notify(
                event_type="price_change",
                stock=stock,
                symbol=symbol,
                new_price=new_price,
                previous_price=stock.previous_price,
                price_change=stock.price_change,
                price_change_percent=stock.price_change_percent,
                volume=volume,
                timestamp=stock.last_updated
            )
    
    def get_stock_price(self, symbol: str) -> Decimal:
        """Get current price of a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current stock price
            
        Raises:
            KeyError: If stock doesn't exist
        """
        with self._market_lock:
            if symbol not in self._stocks:
                raise KeyError(f"Stock {symbol} not found in the market")
            return self._stocks[symbol].price
    
    def get_stock_info(self, symbol: str) -> Stock:
        """Get complete stock information.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Stock object with current information
            
        Raises:
            KeyError: If stock doesn't exist
        """
        with self._market_lock:
            if symbol not in self._stocks:
                raise KeyError(f"Stock {symbol} not found in the market")
            return self._stocks[symbol]
    
    def get_all_stocks(self) -> Dict[str, Stock]:
        """Get information for all stocks in the market.
        
        Returns:
            Dictionary of all stocks indexed by symbol
        """
        with self._market_lock:
            return self._stocks.copy()
    
    def open_market(self) -> None:
        """Open the market for trading."""
        with self._market_lock:
            self._is_market_open = True
            self._logger.info("Market opened")
            
        self.notify(
            event_type="market_opened",
            timestamp=datetime.now(),
            stock_count=len(self._stocks)
        )
    
    def close_market(self) -> None:
        """Close the market."""
        with self._market_lock:
            self._is_market_open = False
            self._logger.info("Market closed")
            
        self.notify(
            event_type="market_closed",
            timestamp=datetime.now(),
            stock_count=len(self._stocks)
        )
    
    @property
    def is_market_open(self) -> bool:
        """Check if market is currently open."""
        return self._is_market_open
    
    @property
    def stock_count(self) -> int:
        """Get the number of stocks in the market."""
        with self._market_lock:
            return len(self._stocks)