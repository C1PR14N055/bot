# Activate py env
source .env/bin/activate
# Download data
# TODO: get current date from date function
freqtrade download-data --timeframe 1h --timerange 20090101-20210823
# Run hyperopt
echo 'Runing hyperopt, --timeframe: 1h, --stake: 0.0022BTC'
freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss --spaces buy roi trailing sell --strategy GodStraNew --timeframe 1h --stake 0.0022
