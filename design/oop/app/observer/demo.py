"""Demonstration script for the Observer pattern stock market simulator with threading."""

import logging
import random
import threading
import time
from decimal import Decimal

from .stock_market import StockMarket
from .observers import Trader, Analyst


def setup_logging() -> None:
    """Configure logging for the demonstration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def price_update_worker(market: StockMarket, symbols: list[str], duration: int) -> None:
    """Worker function to simulate price updates in a separate thread.
    
    Args:
        market: Stock market instance
        symbols: List of stock symbols to update
        duration: Duration in seconds to run updates
    """
    logger = logging.getLogger(f"{__name__}.PriceWorker")
    start_time = time.time()
    update_count = 0
    
    logger.info(f"Starting price updates for {duration} seconds")
    
    while time.time() - start_time < duration:
        try:
            # Select random stock and generate price change
            symbol = random.choice(symbols)
            current_price = market.get_stock_price(symbol)
            
            # Generate random price change between -10% and +10%
            change_percent = Decimal(str(random.uniform(-10.0, 10.0)))
            new_price = current_price * (1 + change_percent / 100)
            
            # Ensure price doesn't go below $1
            new_price = max(new_price, Decimal("1.00"))
            
            # Generate random volume
            volume = random.randint(1000, 50000)
            
            market.update_stock_price(symbol, new_price, volume)
            update_count += 1
            
            # Random delay between updates (0.1 to 1.0 seconds)
            time.sleep(random.uniform(0.1, 1.0))
            
        except Exception as e:
            logger.error(f"Error updating prices: {e}")
            break
    
    logger.info(f"Price worker completed {update_count} updates in {duration} seconds")


def observer_lifecycle_worker(market: StockMarket, observers: list, duration: int) -> None:
    """Worker function to simulate observer attach/detach operations.
    
    Args:
        market: Stock market instance
        observers: List of observers to manage
        duration: Duration in seconds to run lifecycle operations
    """
    logger = logging.getLogger(f"{__name__}.LifecycleWorker")
    start_time = time.time()
    operations = 0
    
    logger.info(f"Starting observer lifecycle operations for {duration} seconds")
    
    while time.time() - start_time < duration:
        try:
            observer = random.choice(observers)
            
            if random.choice([True, False]):
                # Attach observer
                market.attach(observer)
            else:
                # Detach observer
                market.detach(observer)
            
            operations += 1
            time.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            logger.error(f"Error in lifecycle operations: {e}")
            break
    
    logger.info(f"Lifecycle worker completed {operations} operations in {duration} seconds")


def run_basic_demo() -> None:
    """Run a basic demonstration of the Observer pattern."""
    print("\n" + "="*60)
    print("BASIC OBSERVER PATTERN DEMONSTRATION")
    print("="*60)
    
    # Create stock market
    market = StockMarket("NASDAQ")
    
    # Create observers
    trader1 = Trader("Alice", Decimal("15000"))
    trader2 = Trader("Bob", Decimal("20000"))
    analyst1 = Analyst("Charlie", "Tech Stocks")
    analyst2 = Analyst("Diana", "Market Trends")
    
    # Attach observers
    market.attach(trader1)
    market.attach(trader2)
    market.attach(analyst1)
    market.attach(analyst2)
    
    print(f"Attached {market.get_observer_count()} observers: {', '.join(market.get_observer_names())}")
    
    # Add stocks
    stocks = {
        "AAPL": Decimal("150.00"),
        "GOOGL": Decimal("2500.00"),
        "MSFT": Decimal("300.00"),
        "TSLA": Decimal("800.00")
    }
    
    for symbol, price in stocks.items():
        market.add_stock(symbol, price, random.randint(10000, 100000))
    
    print(f"Added {market.stock_count} stocks to the market")
    
    # Open market
    market.open_market()
    
    # Simulate some price changes
    time.sleep(1)
    market.update_stock_price("AAPL", Decimal("147.00"), 25000)  # -2% drop, should trigger buys
    time.sleep(1)
    market.update_stock_price("TSLA", Decimal("824.00"), 30000)  # +3% rise, should trigger sells
    time.sleep(1)
    market.update_stock_price("GOOGL", Decimal("2375.00"), 15000)  # -5% significant drop
    
    # Close market
    time.sleep(1)
    market.close_market()
    
    # Show final portfolios
    print("\n" + "-"*40)
    print("FINAL PORTFOLIO SUMMARY")
    print("-"*40)
    
    market_prices = {symbol: market.get_stock_price(symbol) for symbol in stocks.keys()}
    
    for trader in [trader1, trader2]:
        portfolio_value = trader.get_portfolio_value(market_prices)
        print(f"{trader.name}: Cash=${trader.cash}, Portfolio Value=${portfolio_value}, "
              f"Trades={len(trader.trade_history)}")


def run_threaded_demo() -> None:
    """Run a demonstration with multiple threads simulating concurrent operations."""
    print("\n" + "="*60)
    print("THREADED OBSERVER PATTERN DEMONSTRATION")
    print("="*60)
    
    # Create stock market
    market = StockMarket("NYSE")
    
    # Create multiple observers
    traders = [
        Trader("Trader_1", Decimal("50000")),
        Trader("Trader_2", Decimal("75000")),
        Trader("Trader_3", Decimal("100000"))
    ]
    
    analysts = [
        Analyst("TechAnalyst", "Technology"),
        Analyst("FinanceAnalyst", "Finance"),
        Analyst("EnergyAnalyst", "Energy")
    ]
    
    all_observers = traders + analysts
    
    # Initially attach all observers
    for observer in all_observers:
        market.attach(observer)
    
    print(f"Initially attached {market.get_observer_count()} observers")
    
    # Add stocks
    stock_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
    base_prices = [150, 2500, 300, 3200, 800, 500, 350, 400]
    
    for symbol, price in zip(stock_symbols, base_prices):
        market.add_stock(symbol, Decimal(str(price)), random.randint(50000, 200000))
    
    print(f"Added {market.stock_count} stocks to the market")
    
    # Open market
    market.open_market()
    
    # Create and start worker threads
    threads = []
    demo_duration = 15  # Run for 15 seconds
    
    # Price update workers (2 threads)
    for i in range(2):
        thread = threading.Thread(
            target=price_update_worker,
            args=(market, stock_symbols, demo_duration),
            name=f"PriceWorker-{i+1}"
        )
        threads.append(thread)
    
    # Observer lifecycle worker (1 thread)
    lifecycle_thread = threading.Thread(
        target=observer_lifecycle_worker,
        args=(market, all_observers, demo_duration),
        name="LifecycleWorker"
    )
    threads.append(lifecycle_thread)
    
    print(f"Starting {len(threads)} worker threads for {demo_duration} seconds...")
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Monitor progress
    for i in range(demo_duration):
        time.sleep(1)
        attached_count = market.get_observer_count()
        print(f"Progress: {i+1}/{demo_duration}s - Observers attached: {attached_count}")
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("All worker threads completed")
    
    # Close market
    market.close_market()
    
    # Final statistics
    print("\n" + "-"*50)
    print("FINAL THREADED DEMO STATISTICS")
    print("-"*50)
    
    market_prices = {symbol: market.get_stock_price(symbol) for symbol in stock_symbols}
    
    print(f"Final observer count: {market.get_observer_count()}")
    print(f"Observers: {', '.join(market.get_observer_names())}")
    
    for trader in traders:
        if trader in market._observers:  # Only show stats for attached traders
            portfolio_value = trader.get_portfolio_value(market_prices)
            print(f"{trader.name}: Portfolio Value=${portfolio_value:.2f}, "
                  f"Trades={len(trader.trade_history)}")
    
    for analyst in analysts:
        if analyst in market._observers:  # Only show stats for attached analysts
            tracked_stocks = len(analyst.stocks_tracked)
            print(f"{analyst.name} ({analyst.specialization}): Tracking {tracked_stocks} stocks")


def main() -> None:
    """Main function to run all demonstrations."""
    setup_logging()
    
    print("Observer Pattern Stock Market Simulator")
    print("Threading-enabled demonstration")
    
    try:
        # Run basic demo
        run_basic_demo()
        
        # Wait between demos
        time.sleep(2)
        
        # Run threaded demo
        run_threaded_demo()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        raise


if __name__ == "__main__":
    main()