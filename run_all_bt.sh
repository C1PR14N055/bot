docker-compose run --rm freqtrade backtesting --datadir user_data/data/binance --export trades \
--stake-amount 100 \
--timeframe 15m \
--timerange=20210101- \
--strategy-list BinHV45HyperOpt GodStraNew
