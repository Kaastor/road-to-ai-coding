"""Comprehensive tests for the Observer pattern implementation."""

import threading
import time
from decimal import Decimal
from unittest.mock import Mock, patch
import pytest

from app.observer import Observer, Subject, StockMarket, Trader, Analyst
from app.observer.stock_market import Stock


class MockObserver(Observer):
    """Mock observer for testing purposes."""
    
    def __init__(self, name: str) -> None:
        self._name = name
        self.updates_received = []
        self.update_count = 0
    
    @property
    def name(self) -> str:
        return self._name
    
    def update(self, subject, *args, **kwargs) -> None:
        self.update_count += 1
        self.updates_received.append((args, kwargs))


class TestObserverInterface:
    """Test the Observer abstract base class."""
    
    def test_observer_is_abstract(self) -> None:
        """Test that Observer cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Observer()
    
    def test_mock_observer_implements_interface(self) -> None:
        """Test that MockObserver properly implements the Observer interface."""
        observer = MockObserver("test")
        assert observer.name == "test"
        assert hasattr(observer, 'update')


class TestSubject:
    """Test the Subject class functionality."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.subject = Subject("TestSubject")
        self.observer1 = MockObserver("Observer1")
        self.observer2 = MockObserver("Observer2")
    
    def test_subject_initialization(self) -> None:
        """Test subject initialization."""
        assert self.subject.name == "TestSubject"
        assert self.subject.get_observer_count() == 0
        assert self.subject.get_observer_names() == []
    
    def test_attach_observer(self) -> None:
        """Test attaching observers."""
        self.subject.attach(self.observer1)
        assert self.subject.get_observer_count() == 1
        assert "Observer1" in self.subject.get_observer_names()
    
    def test_attach_duplicate_observer(self) -> None:
        """Test that attaching the same observer twice doesn't duplicate it."""
        self.subject.attach(self.observer1)
        self.subject.attach(self.observer1)
        assert self.subject.get_observer_count() == 1
    
    def test_attach_invalid_observer(self) -> None:
        """Test that attaching non-Observer raises TypeError."""
        with pytest.raises(TypeError, match="Observer must implement Observer interface"):
            self.subject.attach("not_an_observer")
    
    def test_detach_observer(self) -> None:
        """Test detaching observers."""
        self.subject.attach(self.observer1)
        self.subject.attach(self.observer2)
        
        self.subject.detach(self.observer1)
        assert self.subject.get_observer_count() == 1
        assert "Observer1" not in self.subject.get_observer_names()
        assert "Observer2" in self.subject.get_observer_names()
    
    def test_detach_nonexistent_observer(self) -> None:
        """Test detaching an observer that wasn't attached."""
        self.subject.detach(self.observer1)  # Should not raise exception
        assert self.subject.get_observer_count() == 0
    
    def test_notify_observers(self) -> None:
        """Test notifying observers."""
        self.subject.attach(self.observer1)
        self.subject.attach(self.observer2)
        
        self.subject.notify("test_arg", test_kwarg="test_value")
        
        assert self.observer1.update_count == 1
        assert self.observer2.update_count == 1
        assert self.observer1.updates_received[0] == (("test_arg",), {"test_kwarg": "test_value"})
    
    def test_notify_no_observers(self) -> None:
        """Test notifying when no observers are attached."""
        self.subject.notify()  # Should not raise exception
    
    def test_notify_with_observer_exception(self) -> None:
        """Test that observer exceptions don't crash the notification process."""
        failing_observer = Mock(spec=Observer)
        failing_observer.name = "FailingObserver"
        failing_observer.update.side_effect = Exception("Observer error")
        
        self.subject.attach(self.observer1)
        self.subject.attach(failing_observer)
        
        self.subject.notify()  # Should not raise exception
        assert self.observer1.update_count == 1


class TestStock:
    """Test the Stock class functionality."""
    
    def test_stock_initialization(self) -> None:
        """Test stock initialization."""
        stock = Stock("AAPL", Decimal("150.00"), 1000)
        assert stock.symbol == "AAPL"
        assert stock.price == Decimal("150.00")
        assert stock.volume == 1000
        assert stock.previous_price is None
        assert stock.price_change is None
        assert stock.price_change_percent is None
    
    def test_stock_price_update(self) -> None:
        """Test stock price updates."""
        stock = Stock("AAPL", Decimal("150.00"))
        
        changed = stock.update_price(Decimal("155.00"), 2000)
        assert changed is True
        assert stock.price == Decimal("155.00")
        assert stock.previous_price == Decimal("150.00")
        assert stock.volume == 2000
        assert stock.price_change == Decimal("5.00")
        assert abs(stock.price_change_percent - Decimal("3.33")) < Decimal("0.01")
    
    def test_stock_no_price_change(self) -> None:
        """Test when stock price doesn't change."""
        stock = Stock("AAPL", Decimal("150.00"))
        
        changed = stock.update_price(Decimal("150.00"), 2000)
        assert changed is False
        assert stock.price == Decimal("150.00")
        assert stock.previous_price is None


class TestStockMarket:
    """Test the StockMarket class functionality."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.market = StockMarket("TestMarket")
        self.observer = MockObserver("TestObserver")
        self.market.attach(self.observer)
    
    def test_stock_market_initialization(self) -> None:
        """Test stock market initialization."""
        assert self.market.name == "TestMarket"
        assert self.market.stock_count == 0
        assert not self.market.is_market_open
    
    def test_add_stock(self) -> None:
        """Test adding stocks to the market."""
        self.market.add_stock("AAPL", Decimal("150.00"), 1000)
        
        assert self.market.stock_count == 1
        assert self.market.get_stock_price("AAPL") == Decimal("150.00")
        
        stock_info = self.market.get_stock_info("AAPL")
        assert stock_info.symbol == "AAPL"
        assert stock_info.volume == 1000
    
    def test_add_duplicate_stock(self) -> None:
        """Test adding duplicate stock raises ValueError."""
        self.market.add_stock("AAPL", Decimal("150.00"))
        
        with pytest.raises(ValueError, match="Stock AAPL already exists"):
            self.market.add_stock("AAPL", Decimal("160.00"))
    
    def test_remove_stock(self) -> None:
        """Test removing stocks from the market."""
        self.market.add_stock("AAPL", Decimal("150.00"))
        self.market.remove_stock("AAPL")
        
        assert self.market.stock_count == 0
        with pytest.raises(KeyError):
            self.market.get_stock_price("AAPL")
    
    def test_remove_nonexistent_stock(self) -> None:
        """Test removing non-existent stock raises KeyError."""
        with pytest.raises(KeyError, match="Stock AAPL not found"):
            self.market.remove_stock("AAPL")
    
    def test_update_stock_price_with_notification(self) -> None:
        """Test that price updates trigger notifications."""
        self.market.add_stock("AAPL", Decimal("150.00"))
        
        self.market.update_stock_price("AAPL", Decimal("155.00"), 2000)
        
        assert self.observer.update_count == 1
        args, kwargs = self.observer.updates_received[0]
        assert kwargs["event_type"] == "price_change"
        assert kwargs["symbol"] == "AAPL"
        assert kwargs["new_price"] == Decimal("155.00")
        assert kwargs["previous_price"] == Decimal("150.00")
    
    def test_update_stock_price_no_change(self) -> None:
        """Test that unchanged prices don't trigger notifications."""
        self.market.add_stock("AAPL", Decimal("150.00"))
        
        self.market.update_stock_price("AAPL", Decimal("150.00"), 2000)
        
        assert self.observer.update_count == 0
    
    def test_update_nonexistent_stock(self) -> None:
        """Test updating non-existent stock raises KeyError."""
        with pytest.raises(KeyError, match="Stock AAPL not found"):
            self.market.update_stock_price("AAPL", Decimal("155.00"))
    
    def test_market_open_close(self) -> None:
        """Test market open/close operations."""
        self.market.open_market()
        assert self.market.is_market_open
        assert self.observer.update_count == 1
        
        self.market.close_market()
        assert not self.market.is_market_open
        assert self.observer.update_count == 2
        
        # Check notification content
        _, open_kwargs = self.observer.updates_received[0]
        assert open_kwargs["event_type"] == "market_opened"
        
        _, close_kwargs = self.observer.updates_received[1]
        assert close_kwargs["event_type"] == "market_closed"
    
    def test_get_all_stocks(self) -> None:
        """Test getting all stocks information."""
        self.market.add_stock("AAPL", Decimal("150.00"))
        self.market.add_stock("GOOGL", Decimal("2500.00"))
        
        all_stocks = self.market.get_all_stocks()
        assert len(all_stocks) == 2
        assert "AAPL" in all_stocks
        assert "GOOGL" in all_stocks
        assert all_stocks["AAPL"].price == Decimal("150.00")


class TestTrader:
    """Test the Trader observer implementation."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.trader = Trader("TestTrader", Decimal("10000"))
        self.market = StockMarket("TestMarket")
        self.market.attach(self.trader)
        self.market.add_stock("AAPL", Decimal("100.00"))
    
    def test_trader_initialization(self) -> None:
        """Test trader initialization."""
        assert self.trader.name == "TestTrader"
        assert self.trader.cash == Decimal("10000")
        assert self.trader.portfolio == {}
        assert self.trader.trade_history == []
    
    def test_trader_buy_trigger(self) -> None:
        """Test that price drops trigger buy orders."""
        # Simulate 3% price drop (should trigger buy)
        self.market.update_stock_price("AAPL", Decimal("97.00"), 1000)
        
        # Give some time for processing
        time.sleep(0.1)
        
        assert len(self.trader.trade_history) > 0
        assert self.trader.trade_history[0]["action"] == "BUY"
        assert self.trader.portfolio.get("AAPL", 0) > 0
        assert self.trader.cash < Decimal("10000")
    
    def test_trader_sell_trigger(self) -> None:
        """Test that significant price increases trigger sell orders."""
        # First, give trader some shares
        self.market.update_stock_price("AAPL", Decimal("95.00"), 1000)  # Buy trigger
        time.sleep(0.1)
        
        initial_shares = self.trader.portfolio.get("AAPL", 0)
        initial_cash = self.trader.cash
        
        # Now trigger a sell with price increase
        self.market.update_stock_price("AAPL", Decimal("110.00"), 2000)  # +15.8% increase
        time.sleep(0.1)
        
        # Should have sold some shares
        final_shares = self.trader.portfolio.get("AAPL", 0)
        final_cash = self.trader.cash
        
        assert final_shares < initial_shares
        assert final_cash > initial_cash
    
    def test_trader_portfolio_value(self) -> None:
        """Test portfolio value calculation."""
        # Give trader some positions
        self.trader._portfolio["AAPL"] = 10
        self.trader._cash = Decimal("5000")
        
        market_prices = {"AAPL": Decimal("150.00")}
        portfolio_value = self.trader.get_portfolio_value(market_prices)
        
        expected_value = Decimal("5000") + (10 * Decimal("150.00"))  # Cash + stock value
        assert portfolio_value == expected_value
    
    def test_trader_market_events(self) -> None:
        """Test trader response to market open/close events."""
        self.market.open_market()
        self.market.close_market()
        
        # Trader should process these events without error
        # (specific behavior depends on implementation)


class TestAnalyst:
    """Test the Analyst observer implementation."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.analyst = Analyst("TestAnalyst", "Technology")
        self.market = StockMarket("TestMarket")
        self.market.attach(self.analyst)
        self.market.add_stock("AAPL", Decimal("100.00"))
    
    def test_analyst_initialization(self) -> None:
        """Test analyst initialization."""
        assert self.analyst.name == "TestAnalyst"
        assert self.analyst.specialization == "Technology"
        assert self.analyst.stocks_tracked == []
    
    def test_analyst_tracks_price_changes(self) -> None:
        """Test that analyst tracks price changes."""
        self.market.update_stock_price("AAPL", Decimal("105.00"), 1000)
        
        time.sleep(0.1)  # Allow processing
        
        assert "AAPL" in self.analyst.stocks_tracked
        stats = self.analyst.get_stock_statistics("AAPL")
        assert stats is not None
        assert stats["symbol"] == "AAPL"
        assert stats["data_points"] == 1
        assert stats["current_price"] == Decimal("105.00")
    
    def test_analyst_statistics(self) -> None:
        """Test analyst statistical calculations."""
        # Generate several price updates
        prices = [Decimal("100.00"), Decimal("105.00"), Decimal("95.00"), Decimal("110.00")]
        
        for price in prices[1:]:  # Skip first as it's the initial price
            self.market.update_stock_price("AAPL", price, 1000)
            time.sleep(0.05)
        
        stats = self.analyst.get_stock_statistics("AAPL")
        assert stats["data_points"] == 3  # 3 updates after initial
        assert stats["price_range"][0] <= stats["price_range"][1]  # min <= max
        assert stats["volatility"] > Decimal("0")  # Should have some volatility
    
    def test_analyst_nonexistent_stock(self) -> None:
        """Test getting statistics for non-tracked stock."""
        stats = self.analyst.get_stock_statistics("NONEXISTENT")
        assert stats is None


class TestThreadSafety:
    """Test thread safety of the Observer pattern implementation."""
    
    def test_concurrent_attach_detach(self) -> None:
        """Test concurrent attach/detach operations."""
        subject = Subject("ThreadTest")
        observers = [MockObserver(f"Observer{i}") for i in range(10)]
        
        def attach_detach_worker():
            for _ in range(50):
                observer = observers[threading.current_thread().ident % len(observers)]
                if subject.get_observer_count() < 5:
                    subject.attach(observer)
                else:
                    subject.detach(observer)
                time.sleep(0.001)  # Small delay
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=attach_detach_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should complete without deadlocks or exceptions
        assert subject.get_observer_count() >= 0
    
    def test_concurrent_notifications(self) -> None:
        """Test concurrent notification operations."""
        market = StockMarket("ConcurrentTest")
        observers = [MockObserver(f"Observer{i}") for i in range(10)]
        
        for observer in observers:
            market.attach(observer)
        
        market.add_stock("TEST", Decimal("100.00"))
        
        def notification_worker():
            for i in range(20):
                try:
                    price = Decimal(str(100 + i))
                    market.update_stock_price("TEST", price, 1000)
                    time.sleep(0.001)
                except Exception:
                    pass  # Ignore exceptions for this test
        
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=notification_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify that notifications were processed
        total_updates = sum(obs.update_count for obs in observers)
        assert total_updates > 0


class TestIntegration:
    """Integration tests for the complete Observer pattern implementation."""
    
    def test_complete_stock_market_simulation(self) -> None:
        """Test a complete stock market simulation scenario."""
        # Create market and participants
        market = StockMarket("IntegrationTest")
        
        trader1 = Trader("Trader1", Decimal("50000"))
        trader2 = Trader("Trader2", Decimal("75000"))
        analyst = Analyst("Analyst1", "General")
        
        market.attach(trader1)
        market.attach(trader2)
        market.attach(analyst)
        
        # Add stocks
        stocks = {
            "AAPL": Decimal("150.00"),
            "GOOGL": Decimal("2500.00"),
            "MSFT": Decimal("300.00")
        }
        
        for symbol, price in stocks.items():
            market.add_stock(symbol, price)
        
        # Open market
        market.open_market()
        
        # Simulate market activity
        market.update_stock_price("AAPL", Decimal("147.00"), 10000)  # -2% drop
        time.sleep(0.1)
        
        market.update_stock_price("GOOGL", Decimal("2575.00"), 5000)  # +3% rise
        time.sleep(0.1)
        
        market.update_stock_price("MSFT", Decimal("285.00"), 8000)  # -5% drop
        time.sleep(0.1)
        
        # Close market
        market.close_market()
        
        # Verify results
        assert len(analyst.stocks_tracked) == 3
        
        # At least one trader should have made trades due to price movements
        total_trades = len(trader1.trade_history) + len(trader2.trade_history)
        assert total_trades > 0
        
        # Portfolio values should be calculated correctly
        market_prices = {symbol: market.get_stock_price(symbol) for symbol in stocks.keys()}
        
        portfolio_value1 = trader1.get_portfolio_value(market_prices)
        portfolio_value2 = trader2.get_portfolio_value(market_prices)
        
        assert portfolio_value1 > Decimal("0")
        assert portfolio_value2 > Decimal("0")