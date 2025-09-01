"""Concrete observer implementations for the stock market simulator."""

import logging
import threading
from decimal import Decimal
from typing import Any, Dict, List, Optional
from datetime import datetime

from .observer import Observer


class Trader(Observer):
    """Trader observer that makes trading decisions based on price changes.
    
    The trader maintains a portfolio and makes buy/sell decisions based on
    price movements and predefined thresholds.
    """
    
    def __init__(self, name: str, initial_cash: Decimal = Decimal("10000")) -> None:
        """Initialize the trader.
        
        Args:
            name: Trader's name/identifier
            initial_cash: Initial cash available for trading
        """
        self._name = name
        self._cash = initial_cash
        self._portfolio: Dict[str, int] = {}  # symbol -> shares owned
        self._trade_history: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.Trader.{self._name}")
        
        # Trading parameters
        self._buy_threshold_percent = Decimal("-2.0")  # Buy if price drops 2%
        self._sell_threshold_percent = Decimal("3.0")  # Sell if price rises 3%
        self._max_position_size = 100  # Maximum shares per stock
        
    @property
    def name(self) -> str:
        """Return the trader's name."""
        return self._name
    
    def update(self, subject: Any, *args, **kwargs) -> None:
        """Handle stock market updates.
        
        Args:
            subject: The stock market that sent the update
            *args: Variable arguments
            **kwargs: Keyword arguments containing update information
        """
        event_type = kwargs.get("event_type")
        
        if event_type == "price_change":
            self._handle_price_change(**kwargs)
        elif event_type == "market_opened":
            self._handle_market_open(**kwargs)
        elif event_type == "market_closed":
            self._handle_market_close(**kwargs)
        else:
            self._logger.debug(f"Received unknown event type: {event_type}")
    
    def _handle_price_change(self, **kwargs) -> None:
        """Handle stock price change notifications."""
        symbol = kwargs.get("symbol")
        new_price = kwargs.get("new_price")
        previous_price = kwargs.get("previous_price")
        price_change_percent = kwargs.get("price_change_percent")
        volume = kwargs.get("volume")
        
        if not all([symbol, new_price, previous_price, price_change_percent]):
            self._logger.warning("Incomplete price change data received")
            return
        
        self._logger.info(
            f"Price update for {symbol}: ${new_price} "
            f"({price_change_percent:+.2f}%, volume: {volume})"
        )
        
        with self._lock:
            # Make trading decision based on price change
            if price_change_percent <= self._buy_threshold_percent:
                self._consider_buy(symbol, new_price)
            elif price_change_percent >= self._sell_threshold_percent:
                self._consider_sell(symbol, new_price)
    
    def _consider_buy(self, symbol: str, price: Decimal) -> None:
        """Consider buying a stock based on price drop."""
        current_shares = self._portfolio.get(symbol, 0)
        
        if current_shares >= self._max_position_size:
            self._logger.debug(f"Already at max position for {symbol}")
            return
        
        shares_to_buy = min(
            self._max_position_size - current_shares,
            int(self._cash / price) if price > 0 else 0
        )
        
        if shares_to_buy > 0:
            cost = shares_to_buy * price
            if cost <= self._cash:
                self._execute_buy(symbol, shares_to_buy, price)
    
    def _consider_sell(self, symbol: str, price: Decimal) -> None:
        """Consider selling a stock based on price increase."""
        current_shares = self._portfolio.get(symbol, 0)
        
        if current_shares > 0:
            # Sell half of current position for profit taking
            shares_to_sell = max(1, current_shares // 2)
            self._execute_sell(symbol, shares_to_sell, price)
    
    def _execute_buy(self, symbol: str, shares: int, price: Decimal) -> None:
        """Execute a buy order."""
        cost = shares * price
        self._cash -= cost
        self._portfolio[symbol] = self._portfolio.get(symbol, 0) + shares
        
        trade = {
            "action": "BUY",
            "symbol": symbol,
            "shares": shares,
            "price": price,
            "total": cost,
            "timestamp": datetime.now()
        }
        self._trade_history.append(trade)
        
        self._logger.info(f"BOUGHT {shares} shares of {symbol} at ${price} (total: ${cost})")
    
    def _execute_sell(self, symbol: str, shares: int, price: Decimal) -> None:
        """Execute a sell order."""
        if self._portfolio.get(symbol, 0) < shares:
            self._logger.warning(f"Insufficient shares to sell {shares} of {symbol}")
            return
        
        revenue = shares * price
        self._cash += revenue
        self._portfolio[symbol] -= shares
        
        if self._portfolio[symbol] == 0:
            del self._portfolio[symbol]
        
        trade = {
            "action": "SELL",
            "symbol": symbol,
            "shares": shares,
            "price": price,
            "total": revenue,
            "timestamp": datetime.now()
        }
        self._trade_history.append(trade)
        
        self._logger.info(f"SOLD {shares} shares of {symbol} at ${price} (total: ${revenue})")
    
    def _handle_market_open(self, **kwargs) -> None:
        """Handle market open notification."""
        self._logger.info("Market opened - ready for trading")
    
    def _handle_market_close(self, **kwargs) -> None:
        """Handle market close notification."""
        self._logger.info("Market closed - trading suspended")
        self._log_portfolio_summary()
    
    def _log_portfolio_summary(self) -> None:
        """Log current portfolio status."""
        with self._lock:
            total_trades = len(self._trade_history)
            self._logger.info(
                f"Portfolio summary - Cash: ${self._cash}, "
                f"Positions: {len(self._portfolio)}, "
                f"Total trades: {total_trades}"
            )
    
    def get_portfolio_value(self, market_prices: Dict[str, Decimal]) -> Decimal:
        """Calculate total portfolio value including cash and stock positions.
        
        Args:
            market_prices: Current market prices for stocks
            
        Returns:
            Total portfolio value
        """
        with self._lock:
            stock_value = sum(
                shares * market_prices.get(symbol, Decimal("0"))
                for symbol, shares in self._portfolio.items()
            )
            return self._cash + stock_value
    
    @property
    def cash(self) -> Decimal:
        """Get current cash balance."""
        return self._cash
    
    @property
    def portfolio(self) -> Dict[str, int]:
        """Get current portfolio positions."""
        with self._lock:
            return self._portfolio.copy()
    
    @property
    def trade_history(self) -> List[Dict[str, Any]]:
        """Get trading history."""
        with self._lock:
            return self._trade_history.copy()


class Analyst(Observer):
    """Analyst observer that tracks and analyzes stock market data.
    
    The analyst maintains statistics and performs analysis on stock movements
    without executing trades.
    """
    
    def __init__(self, name: str, specialization: str = "General") -> None:
        """Initialize the analyst.
        
        Args:
            name: Analyst's name/identifier
            specialization: Area of specialization (e.g., 'Tech', 'Finance')
        """
        self._name = name
        self._specialization = specialization
        self._price_history: Dict[str, List[Dict[str, Any]]] = {}
        self._market_events: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.Analyst.{self._name}")
        
        # Analysis thresholds
        self._significant_change_threshold = Decimal("5.0")  # 5% change is significant
        self._volatility_window = 10  # Track volatility over last 10 updates
        
    @property
    def name(self) -> str:
        """Return the analyst's name."""
        return self._name
    
    def update(self, subject: Any, *args, **kwargs) -> None:
        """Handle stock market updates.
        
        Args:
            subject: The stock market that sent the update
            *args: Variable arguments
            **kwargs: Keyword arguments containing update information
        """
        event_type = kwargs.get("event_type")
        
        if event_type == "price_change":
            self._analyze_price_change(**kwargs)
        elif event_type == "market_opened":
            self._track_market_event("MARKET_OPENED", **kwargs)
        elif event_type == "market_closed":
            self._track_market_event("MARKET_CLOSED", **kwargs)
            self._generate_daily_report()
        else:
            self._logger.debug(f"Received unknown event type: {event_type}")
    
    def _analyze_price_change(self, **kwargs) -> None:
        """Analyze stock price changes and detect patterns."""
        symbol = kwargs.get("symbol")
        new_price = kwargs.get("new_price")
        previous_price = kwargs.get("previous_price")
        price_change_percent = kwargs.get("price_change_percent")
        volume = kwargs.get("volume")
        timestamp = kwargs.get("timestamp")
        
        if not all([symbol, new_price, previous_price, price_change_percent]):
            self._logger.warning("Incomplete price change data received")
            return
        
        with self._lock:
            # Record price data
            if symbol not in self._price_history:
                self._price_history[symbol] = []
            
            price_data = {
                "price": new_price,
                "previous_price": previous_price,
                "change_percent": price_change_percent,
                "volume": volume,
                "timestamp": timestamp
            }
            
            self._price_history[symbol].append(price_data)
            
            # Keep only recent history for volatility calculation
            if len(self._price_history[symbol]) > self._volatility_window:
                self._price_history[symbol] = self._price_history[symbol][-self._volatility_window:]
        
        # Perform analysis
        self._check_significant_movement(symbol, price_change_percent, new_price)
        self._analyze_volatility(symbol)
    
    def _check_significant_movement(self, symbol: str, change_percent: Decimal, price: Decimal) -> None:
        """Check for significant price movements."""
        if abs(change_percent) >= self._significant_change_threshold:
            direction = "UP" if change_percent > 0 else "DOWN"
            self._logger.warning(
                f"SIGNIFICANT MOVEMENT: {symbol} moved {direction} by {abs(change_percent):.2f}% "
                f"to ${price}"
            )
    
    def _analyze_volatility(self, symbol: str) -> None:
        """Analyze stock volatility based on recent price changes."""
        with self._lock:
            price_history = self._price_history.get(symbol, [])
            
            if len(price_history) >= 3:  # Need at least 3 data points
                recent_changes = [abs(data["change_percent"]) for data in price_history[-5:]]
                avg_volatility = sum(recent_changes) / len(recent_changes)
                
                if avg_volatility > self._significant_change_threshold:
                    self._logger.info(
                        f"HIGH VOLATILITY detected for {symbol}: "
                        f"average change {avg_volatility:.2f}% over last {len(recent_changes)} updates"
                    )
    
    def _track_market_event(self, event: str, **kwargs) -> None:
        """Track market events for analysis."""
        with self._lock:
            event_data = {
                "event": event,
                "timestamp": kwargs.get("timestamp", datetime.now()),
                "stock_count": kwargs.get("stock_count", 0)
            }
            self._market_events.append(event_data)
            
        self._logger.info(f"Market event tracked: {event}")
    
    def _generate_daily_report(self) -> None:
        """Generate daily market analysis report."""
        with self._lock:
            total_stocks_tracked = len(self._price_history)
            total_updates = sum(len(history) for history in self._price_history.values())
            
            # Find most volatile stock
            most_volatile_stock = None
            highest_volatility = Decimal("0")
            
            for symbol, history in self._price_history.items():
                if len(history) >= 2:
                    volatility = sum(abs(data["change_percent"]) for data in history) / len(history)
                    if volatility > highest_volatility:
                        highest_volatility = volatility
                        most_volatile_stock = symbol
        
        self._logger.info(
            f"DAILY REPORT ({self._specialization} Analysis): "
            f"Tracked {total_stocks_tracked} stocks, "
            f"processed {total_updates} price updates. "
            f"Most volatile: {most_volatile_stock} ({highest_volatility:.2f}% avg)"
        )
    
    def get_stock_statistics(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get statistical analysis for a specific stock.
        
        Args:
            symbol: Stock symbol to analyze
            
        Returns:
            Dictionary containing stock statistics, or None if no data
        """
        with self._lock:
            history = self._price_history.get(symbol)
            if not history:
                return None
            
            prices = [data["price"] for data in history]
            changes = [data["change_percent"] for data in history]
            
            return {
                "symbol": symbol,
                "data_points": len(history),
                "current_price": prices[-1] if prices else None,
                "price_range": (min(prices), max(prices)) if prices else None,
                "avg_change_percent": sum(changes) / len(changes) if changes else Decimal("0"),
                "volatility": sum(abs(change) for change in changes) / len(changes) if changes else Decimal("0"),
                "total_volume": sum(data["volume"] for data in history),
                "last_updated": history[-1]["timestamp"] if history else None
            }
    
    @property
    def specialization(self) -> str:
        """Get analyst's specialization."""
        return self._specialization
    
    @property
    def stocks_tracked(self) -> List[str]:
        """Get list of stocks being tracked."""
        with self._lock:
            return list(self._price_history.keys())