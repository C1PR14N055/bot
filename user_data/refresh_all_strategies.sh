#!/bin/bash

echo "docker-compose run --rm freqtrade backtesting --datadir user_data/data/binance --export trades --stake-amount 100 -i 15m --timerange=20210101- --strategy-list " > run_all_strats.sh
ls -1a strategies/*.py > all_strategies.txt
cat all_strategies.txt | sed 's/.py/\\/' > all_strategies.txt
#cat all_strategies.txt | sed 's/strategies\///' > all_strategies.txt &&
#cat all_strategies.txt >> run_all_strats.sh &&
#echo "done"
