#!/bin/bash
echo "! Creating run_all_strats.sh file"
echo "docker-compose run --rm freqtrade backtesting --datadir user_data/data/binance --export trades --stake-amount 100 -i 1h --timerange=20210101- --strategy-list " > run_all_strats.sh
echo "! Listing 'ls -1a strategies/*.py'"
ls -1a strategies/*.py | tee all_strategies.txt
cat all_strategies.txt | sed "s/.py//; s/strategies\///" > final_all_strategies.txt
echo "! Cleaning up..."
rm all_strategies.txt
echo "! Final 'final_all_strategies.txt' list"
cat final_all_strategies.txt
echo "! Done"