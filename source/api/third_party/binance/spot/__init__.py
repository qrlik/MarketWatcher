from api.third_party.binance.api import API


class Spot(API):
    def __init__(self, api_key=None, api_secret=None, **kwargs):
        if "base_url" not in kwargs:
            kwargs["base_url"] = "https://api.binance.com"
        super().__init__(api_key, api_secret, **kwargs)

    # MARKETS
    from api.third_party.binance.spot.market import ping
    from api.third_party.binance.spot.market import time
    from api.third_party.binance.spot.market import exchange_info
    from api.third_party.binance.spot.market import depth
    from api.third_party.binance.spot.market import trades
    from api.third_party.binance.spot.market import historical_trades
    from api.third_party.binance.spot.market import agg_trades
    from api.third_party.binance.spot.market import klines
    from api.third_party.binance.spot.market import klinesAsync
    from api.third_party.binance.spot.market import ui_klines
    from api.third_party.binance.spot.market import avg_price
    from api.third_party.binance.spot.market import ticker_24hr
    from api.third_party.binance.spot.market import ticker_price
    from api.third_party.binance.spot.market import book_ticker
    from api.third_party.binance.spot.market import rolling_window_ticker

    # ACCOUNT (including orders and trades)
    from api.third_party.binance.spot.trade import new_order_test
    from api.third_party.binance.spot.trade import new_order
    from api.third_party.binance.spot.trade import cancel_order
    from api.third_party.binance.spot.trade import cancel_open_orders
    from api.third_party.binance.spot.trade import get_order
    from api.third_party.binance.spot.trade import cancel_and_replace
    from api.third_party.binance.spot.trade import get_open_orders
    from api.third_party.binance.spot.trade import get_orders
    from api.third_party.binance.spot.trade import new_oco_order
    from api.third_party.binance.spot.trade import cancel_oco_order
    from api.third_party.binance.spot.trade import get_oco_order
    from api.third_party.binance.spot.trade import get_oco_orders
    from api.third_party.binance.spot.trade import get_oco_open_orders
    from api.third_party.binance.spot.trade import account
    from api.third_party.binance.spot.trade import my_trades
    from api.third_party.binance.spot.trade import get_order_rate_limit

    # STREAMS
    from api.third_party.binance.spot.data_stream import new_listen_key
    from api.third_party.binance.spot.data_stream import renew_listen_key
    from api.third_party.binance.spot.data_stream import close_listen_key
    from api.third_party.binance.spot.data_stream import new_margin_listen_key
    from api.third_party.binance.spot.data_stream import renew_margin_listen_key
    from api.third_party.binance.spot.data_stream import close_margin_listen_key
    from api.third_party.binance.spot.data_stream import new_isolated_margin_listen_key
    from api.third_party.binance.spot.data_stream import renew_isolated_margin_listen_key
    from api.third_party.binance.spot.data_stream import close_isolated_margin_listen_key

    # MARGIN
    from api.third_party.binance.spot.margin import margin_transfer
    from api.third_party.binance.spot.margin import margin_borrow
    from api.third_party.binance.spot.margin import margin_repay
    from api.third_party.binance.spot.margin import margin_asset
    from api.third_party.binance.spot.margin import margin_pair
    from api.third_party.binance.spot.margin import margin_all_assets
    from api.third_party.binance.spot.margin import margin_all_pairs
    from api.third_party.binance.spot.margin import margin_pair_index
    from api.third_party.binance.spot.margin import new_margin_order
    from api.third_party.binance.spot.margin import cancel_margin_order
    from api.third_party.binance.spot.margin import margin_transfer_history
    from api.third_party.binance.spot.margin import margin_load_record
    from api.third_party.binance.spot.margin import margin_repay_record
    from api.third_party.binance.spot.margin import margin_interest_history
    from api.third_party.binance.spot.margin import margin_force_liquidation_record
    from api.third_party.binance.spot.margin import margin_account
    from api.third_party.binance.spot.margin import margin_order
    from api.third_party.binance.spot.margin import margin_open_orders
    from api.third_party.binance.spot.margin import margin_open_orders_cancellation
    from api.third_party.binance.spot.margin import margin_all_orders
    from api.third_party.binance.spot.margin import margin_my_trades
    from api.third_party.binance.spot.margin import margin_max_borrowable
    from api.third_party.binance.spot.margin import margin_max_transferable
    from api.third_party.binance.spot.margin import isolated_margin_transfer
    from api.third_party.binance.spot.margin import isolated_margin_transfer_history
    from api.third_party.binance.spot.margin import isolated_margin_account
    from api.third_party.binance.spot.margin import isolated_margin_pair
    from api.third_party.binance.spot.margin import isolated_margin_all_pairs
    from api.third_party.binance.spot.margin import toggle_bnbBurn
    from api.third_party.binance.spot.margin import bnbBurn_status
    from api.third_party.binance.spot.margin import margin_interest_rate_history
    from api.third_party.binance.spot.margin import new_margin_oco_order
    from api.third_party.binance.spot.margin import cancel_margin_oco_order
    from api.third_party.binance.spot.margin import get_margin_oco_order
    from api.third_party.binance.spot.margin import get_margin_oco_orders
    from api.third_party.binance.spot.margin import get_margin_open_oco_orders
    from api.third_party.binance.spot.margin import cancel_isolated_margin_account
    from api.third_party.binance.spot.margin import enable_isolated_margin_account
    from api.third_party.binance.spot.margin import isolated_margin_account_limit
    from api.third_party.binance.spot.margin import margin_fee
    from api.third_party.binance.spot.margin import isolated_margin_fee
    from api.third_party.binance.spot.margin import isolated_margin_tier
    from api.third_party.binance.spot.margin import margin_order_usage
    from api.third_party.binance.spot.margin import margin_dust_log
    from api.third_party.binance.spot.margin import summary_of_margin_account

    # SAVINGS
    from api.third_party.binance.spot.savings import savings_flexible_products
    from api.third_party.binance.spot.savings import savings_flexible_user_left_quota
    from api.third_party.binance.spot.savings import savings_purchase_flexible_product
    from api.third_party.binance.spot.savings import savings_flexible_user_redemption_quota
    from api.third_party.binance.spot.savings import savings_flexible_redeem
    from api.third_party.binance.spot.savings import savings_flexible_product_position
    from api.third_party.binance.spot.savings import savings_project_list
    from api.third_party.binance.spot.savings import savings_purchase_project
    from api.third_party.binance.spot.savings import savings_project_position
    from api.third_party.binance.spot.savings import savings_account
    from api.third_party.binance.spot.savings import savings_purchase_record
    from api.third_party.binance.spot.savings import savings_redemption_record
    from api.third_party.binance.spot.savings import savings_interest_history
    from api.third_party.binance.spot.savings import savings_change_position

    # Staking
    from api.third_party.binance.spot.staking import staking_product_list
    from api.third_party.binance.spot.staking import staking_purchase_product
    from api.third_party.binance.spot.staking import staking_redeem_product
    from api.third_party.binance.spot.staking import staking_product_position
    from api.third_party.binance.spot.staking import staking_history
    from api.third_party.binance.spot.staking import staking_set_auto_staking
    from api.third_party.binance.spot.staking import staking_product_quota

    # WALLET
    from api.third_party.binance.spot.wallet import system_status
    from api.third_party.binance.spot.wallet import coin_info
    from api.third_party.binance.spot.wallet import account_snapshot
    from api.third_party.binance.spot.wallet import disable_fast_withdraw
    from api.third_party.binance.spot.wallet import enable_fast_withdraw
    from api.third_party.binance.spot.wallet import withdraw
    from api.third_party.binance.spot.wallet import deposit_history
    from api.third_party.binance.spot.wallet import withdraw_history
    from api.third_party.binance.spot.wallet import deposit_address
    from api.third_party.binance.spot.wallet import account_status
    from api.third_party.binance.spot.wallet import api_trading_status
    from api.third_party.binance.spot.wallet import dust_log
    from api.third_party.binance.spot.wallet import user_universal_transfer
    from api.third_party.binance.spot.wallet import user_universal_transfer_history
    from api.third_party.binance.spot.wallet import transfer_dust
    from api.third_party.binance.spot.wallet import asset_dividend_record
    from api.third_party.binance.spot.wallet import asset_detail
    from api.third_party.binance.spot.wallet import trade_fee
    from api.third_party.binance.spot.wallet import funding_wallet
    from api.third_party.binance.spot.wallet import user_asset
    from api.third_party.binance.spot.wallet import api_key_permissions
    from api.third_party.binance.spot.wallet import bnb_convertible_assets
    from api.third_party.binance.spot.wallet import convertible_coins
    from api.third_party.binance.spot.wallet import toggle_auto_convertion
    from api.third_party.binance.spot.wallet import cloud_mining_trans_history
    from api.third_party.binance.spot.wallet import convert_transfer
    from api.third_party.binance.spot.wallet import convert_history

    # MINING
    from api.third_party.binance.spot.mining import mining_algo_list
    from api.third_party.binance.spot.mining import mining_coin_list
    from api.third_party.binance.spot.mining import mining_worker
    from api.third_party.binance.spot.mining import mining_worker_list
    from api.third_party.binance.spot.mining import mining_earnings_list
    from api.third_party.binance.spot.mining import mining_bonus_list
    from api.third_party.binance.spot.mining import mining_statistics_list
    from api.third_party.binance.spot.mining import mining_account_list
    from api.third_party.binance.spot.mining import mining_hashrate_resale_request
    from api.third_party.binance.spot.mining import mining_hashrate_resale_cancellation
    from api.third_party.binance.spot.mining import mining_hashrate_resale_list
    from api.third_party.binance.spot.mining import mining_hashrate_resale_details
    from api.third_party.binance.spot.mining import mining_account_earning

    # SUB-ACCOUNT
    from api.third_party.binance.spot.sub_account import sub_account_create
    from api.third_party.binance.spot.sub_account import sub_account_list
    from api.third_party.binance.spot.sub_account import sub_account_assets
    from api.third_party.binance.spot.sub_account import sub_account_deposit_address
    from api.third_party.binance.spot.sub_account import sub_account_deposit_history
    from api.third_party.binance.spot.sub_account import sub_account_status
    from api.third_party.binance.spot.sub_account import sub_account_enable_margin
    from api.third_party.binance.spot.sub_account import sub_account_margin_account
    from api.third_party.binance.spot.sub_account import sub_account_margin_account_summary
    from api.third_party.binance.spot.sub_account import sub_account_enable_futures
    from api.third_party.binance.spot.sub_account import sub_account_futures_transfer
    from api.third_party.binance.spot.sub_account import sub_account_margin_transfer
    from api.third_party.binance.spot.sub_account import sub_account_transfer_to_sub
    from api.third_party.binance.spot.sub_account import sub_account_transfer_to_master
    from api.third_party.binance.spot.sub_account import sub_account_transfer_sub_account_history
    from api.third_party.binance.spot.sub_account import sub_account_futures_asset_transfer_history
    from api.third_party.binance.spot.sub_account import sub_account_futures_asset_transfer
    from api.third_party.binance.spot.sub_account import sub_account_spot_summary
    from api.third_party.binance.spot.sub_account import sub_account_universal_transfer
    from api.third_party.binance.spot.sub_account import sub_account_universal_transfer_history
    from api.third_party.binance.spot.sub_account import sub_account_futures_account
    from api.third_party.binance.spot.sub_account import sub_account_futures_account_summary
    from api.third_party.binance.spot.sub_account import sub_account_futures_position_risk
    from api.third_party.binance.spot.sub_account import sub_account_spot_transfer_history
    from api.third_party.binance.spot.sub_account import sub_account_enable_leverage_token
    from api.third_party.binance.spot.sub_account import managed_sub_account_deposit
    from api.third_party.binance.spot.sub_account import managed_sub_account_assets
    from api.third_party.binance.spot.sub_account import managed_sub_account_withdraw
    from api.third_party.binance.spot.sub_account import sub_account_api_toggle_ip_restriction
    from api.third_party.binance.spot.sub_account import sub_account_api_add_ip
    from api.third_party.binance.spot.sub_account import sub_account_api_get_ip_restriction
    from api.third_party.binance.spot.sub_account import sub_account_api_delete_ip
    from api.third_party.binance.spot.sub_account import managed_sub_account_get_snapshot
    from api.third_party.binance.spot.sub_account import managed_sub_account_investor_trans_log
    from api.third_party.binance.spot.sub_account import managed_sub_account_trading_trans_log

    # FUTURES
    from api.third_party.binance.spot.futures import futures_transfer
    from api.third_party.binance.spot.futures import futures_transfer_history
    from api.third_party.binance.spot.futures import futures_loan_borrow_history
    from api.third_party.binance.spot.futures import futures_loan_repay_history
    from api.third_party.binance.spot.futures import futures_loan_wallet
    from api.third_party.binance.spot.futures import futures_loan_adjust_collateral_history
    from api.third_party.binance.spot.futures import futures_loan_liquidation_history
    from api.third_party.binance.spot.futures import futures_loan_interest_history

    # BLVTs
    from api.third_party.binance.spot.blvt import blvt_info
    from api.third_party.binance.spot.blvt import subscribe_blvt
    from api.third_party.binance.spot.blvt import subscription_record
    from api.third_party.binance.spot.blvt import redeem_blvt
    from api.third_party.binance.spot.blvt import redemption_record
    from api.third_party.binance.spot.blvt import user_limit_info

    # BSwap
    from api.third_party.binance.spot.bswap import bswap_pools
    from api.third_party.binance.spot.bswap import bswap_liquidity
    from api.third_party.binance.spot.bswap import bswap_liquidity_add
    from api.third_party.binance.spot.bswap import bswap_liquidity_remove
    from api.third_party.binance.spot.bswap import bswap_liquidity_operation_record
    from api.third_party.binance.spot.bswap import bswap_request_quote
    from api.third_party.binance.spot.bswap import bswap_swap
    from api.third_party.binance.spot.bswap import bswap_swap_history
    from api.third_party.binance.spot.bswap import bswap_pool_configure
    from api.third_party.binance.spot.bswap import bswap_add_liquidity_preview
    from api.third_party.binance.spot.bswap import bswap_remove_liquidity_preview
    from api.third_party.binance.spot.bswap import bswap_unclaimed_rewards
    from api.third_party.binance.spot.bswap import bswap_claim_rewards
    from api.third_party.binance.spot.bswap import bswap_claimed_rewards

    # FIAT
    from api.third_party.binance.spot.fiat import fiat_order_history
    from api.third_party.binance.spot.fiat import fiat_payment_history

    # C2C
    from api.third_party.binance.spot.c2c import c2c_trade_history

    # LOANS
    from api.third_party.binance.spot.loan import loan_history
    from api.third_party.binance.spot.loan import loan_borrow
    from api.third_party.binance.spot.loan import loan_borrow_history
    from api.third_party.binance.spot.loan import loan_ongoing_orders
    from api.third_party.binance.spot.loan import loan_repay
    from api.third_party.binance.spot.loan import loan_repay_history
    from api.third_party.binance.spot.loan import loan_adjust_ltv
    from api.third_party.binance.spot.loan import loan_adjust_ltv_history
    from api.third_party.binance.spot.loan import loan_vip_ongoing_orders
    from api.third_party.binance.spot.loan import loan_vip_repay
    from api.third_party.binance.spot.loan import loan_vip_repay_history
    from api.third_party.binance.spot.loan import loan_vip_collateral_account
    from api.third_party.binance.spot.loan import loan_loanable_data
    from api.third_party.binance.spot.loan import loan_collateral_data
    from api.third_party.binance.spot.loan import loan_collateral_rate
    from api.third_party.binance.spot.loan import loan_customize_margin_call

    # PAY
    from api.third_party.binance.spot.pay import pay_history

    # CONVERT
    from api.third_party.binance.spot.convert import convert_trade_history

    # REBATE
    from api.third_party.binance.spot.rebate import rebate_spot_history

    # NFT
    from api.third_party.binance.spot.nft import nft_transaction_history
    from api.third_party.binance.spot.nft import nft_deposit_history
    from api.third_party.binance.spot.nft import nft_withdraw_history
    from api.third_party.binance.spot.nft import nft_asset

    # Gift Card (Binance Code in the API documentation)
    from api.third_party.binance.spot.gift_card import gift_card_create_code
    from api.third_party.binance.spot.gift_card import gift_card_redeem_code
    from api.third_party.binance.spot.gift_card import gift_card_verify_code
    from api.third_party.binance.spot.gift_card import gift_card_rsa_public_key
    from api.third_party.binance.spot.gift_card import gift_card_buy_code
    from api.third_party.binance.spot.gift_card import gift_card_token_limit

    # Portfolio Margin
    from api.third_party.binance.spot.portfolio_margin import portfolio_margin_account
    from api.third_party.binance.spot.portfolio_margin import portfolio_margin_collateral_rate
    from api.third_party.binance.spot.portfolio_margin import portfolio_margin_bankruptcy_loan_amount
    from api.third_party.binance.spot.portfolio_margin import portfolio_margin_bankruptcy_loan_repay
