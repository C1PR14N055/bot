clear
echo "******* RUNNIGN ALL STATS *******"
docker-compose run --rm freqtrade backtesting \
--datadir user_data/data/binance \
--export trades \
--stake-amount 100 \
--timeframe 15m \
--timerange=20210101- \
--strategy-list \
ADXMomentum \
ASDTSRockwellTrading \
AdxSmas \
AverageStrategy \
AwesomeMacd \
BbandRsi \
BinHV27 \
BinHV45 \
CCIStrategy \
CMCWinner \
ClucMay72018 \
CofiBitStrategy \
CombinedBinHAndCluc \
DevilStra \
DoesNothingStrategy \
EMASkipPump \
Freqtrade_backtest_validation_freqtrade1 \
GodStraNew \
InformativeSample \
Low_BB \
MACDStrategy \
MACDStrategy_crossed \
MultiRSI \
Quickie \
ReinforcedAverageStrategy \
ReinforcedQuickie \
ReinforcedSmoothScalp \
Scalp \
Simple \
SmoothOperator \
SmoothScalp \
Strategy001 \
Strategy002 \
Strategy003 \
Strategy004 \
Strategy005 \
TDSequentialStrategy \
TechnicalExampleStrategy \
BBRSISimpleStrategy \
CustomStoplossWithPSAR \
FixedRiskRewardLoss \
hlhb \
mabStra 
echo "******* DONE *******"
