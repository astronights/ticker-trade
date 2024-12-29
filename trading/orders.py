import logging

from ib_insync import IB, Stock, Trade, Order, MarketOrder, LimitOrder

def place_market_order(ib: IB, stock: Stock, action: str, quantity: int) -> Trade:
    '''Place a Market Order
    
    Args:
        ib (IB): IBKR TWS API Instance
        stock (Stock): IBKR Stock Contract
        action (str): BUY / SELL
        quantity (int): Number of shares

    Returns:
        trade (Trade): IBKR Trade Object
    '''
    try:
        order = MarketOrder(action, quantity)
        trade = ib.placeOrder(stock, order)

        logging.info(f"Placed MARKET {action} order for {stock.symbol} {quantity}.")

        while not trade.isDone():
            ib.sleep(0.5)
        
        return trade
    
    except Exception as e:
        logging.error(f"Failed to place MARKET order: {e}")
        raise

def place_limit_order(ib: IB, stock: Stock, action: str, quantity: int, price: float) -> Trade:
    '''Place a Limit Order
    
    Args:
        ib (IB): IBKR TWS API Instance
        stock (Stock): IBKR Stock Contract
        action (str): BUY / SELL
        quantity (int): Number of shares
        price (float): Order price

    Returns:
        trade (Trade): IBKR Trade Object
    '''
    try:
        order = LimitOrder(action, quantity, price)
        trade = ib.placeOrder(stock, order)

        logging.info(f"Placed LIMIT {action} order for {stock.symbol} {quantity} @ {price:.2f}.")
        return trade
    
    except Exception as e:
        logging.error(f"Failed to place LIMIT order: {e}")
        raise