from api.third_party.binance.api import API


class CMFutures(API):
    def __init__(self, key=None, secret=None, **kwargs):
        if "base_url" not in kwargs:
            kwargs["base_url"] = "https://dapi.binance.com"
        super().__init__(key, secret, **kwargs)

    # MARKETS
    from api.third_party.binance.cm_futures.market import ping
    from api.third_party.binance.cm_futures.market import time
    from api.third_party.binance.cm_futures.market import exchange_info
    from api.third_party.binance.cm_futures.market import depth
    from api.third_party.binance.cm_futures.market import trades
    from api.third_party.binance.cm_futures.market import historical_trades
    from api.third_party.binance.cm_futures.market import agg_trades
    from api.third_party.binance.cm_futures.market import klines
    from api.third_party.binance.cm_futures.market import continuous_klines
    from api.third_party.binance.cm_futures.market import index_price_klines
    from api.third_party.binance.cm_futures.market import mark_price_klines
    from api.third_party.binance.cm_futures.market import mark_price
    from api.third_party.binance.cm_futures.market import funding_rate
    from api.third_party.binance.cm_futures.market import ticker_24hr_price_change
    from api.third_party.binance.cm_futures.market import ticker_price
    from api.third_party.binance.cm_futures.market import book_ticker
    from api.third_party.binance.cm_futures.market import open_interest
    from api.third_party.binance.cm_futures.market import open_interest_hist
    from api.third_party.binance.cm_futures.market import top_long_short_account_ratio
    from api.third_party.binance.cm_futures.market import top_long_short_position_ratio
    from api.third_party.binance.cm_futures.market import long_short_account_ratio
    from api.third_party.binance.cm_futures.market import taker_long_short_ratio
    from api.third_party.binance.cm_futures.market import basis

    # ACCOUNT(including orders and trades)
    from api.third_party.binance.cm_futures.account import change_position_mode
    from api.third_party.binance.cm_futures.account import get_position_mode
    from api.third_party.binance.cm_futures.account import new_order
    from api.third_party.binance.cm_futures.account import modify_order
    from api.third_party.binance.cm_futures.account import new_batch_order
    from api.third_party.binance.cm_futures.account import modify_batch_order
    from api.third_party.binance.cm_futures.account import order_modify_history
    from api.third_party.binance.cm_futures.account import query_order
    from api.third_party.binance.cm_futures.account import cancel_order
    from api.third_party.binance.cm_futures.account import cancel_open_orders
    from api.third_party.binance.cm_futures.account import cancel_batch_order
    from api.third_party.binance.cm_futures.account import countdown_cancel_order
    from api.third_party.binance.cm_futures.account import get_open_orders
    from api.third_party.binance.cm_futures.account import get_orders
    from api.third_party.binance.cm_futures.account import get_all_orders
    from api.third_party.binance.cm_futures.account import balance
    from api.third_party.binance.cm_futures.account import account
    from api.third_party.binance.cm_futures.account import change_leverage
    from api.third_party.binance.cm_futures.account import change_margin_type
    from api.third_party.binance.cm_futures.account import modify_isolated_position_margin
    from api.third_party.binance.cm_futures.account import get_position_margin_history
    from api.third_party.binance.cm_futures.account import get_position_risk
    from api.third_party.binance.cm_futures.account import get_account_trades
    from api.third_party.binance.cm_futures.account import get_income_history
    from api.third_party.binance.cm_futures.account import leverage_brackets
    from api.third_party.binance.cm_futures.account import adl_quantile
    from api.third_party.binance.cm_futures.account import force_orders
    from api.third_party.binance.cm_futures.account import commission_rate

    # STREAMS
    from api.third_party.binance.cm_futures.data_stream import new_listen_key
    from api.third_party.binance.cm_futures.data_stream import renew_listen_key
    from api.third_party.binance.cm_futures.data_stream import close_listen_key

    # PORTFOLIO MARGIN
    from api.third_party.binance.cm_futures.portfolio_margin import pm_exchange_info
