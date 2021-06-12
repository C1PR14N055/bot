#!/bin/bash
# This script initializes the VPS. 
# It updates, upgrades & installs deps, adds aliases, 
# customizes shell, customizes vim, etc, runs docker stuff etc

# colorsss
green='\033[0;32m'
red='\033[0;31m'
nocolor='\033[0m'

# hello there
echo -e "\n
_____________________________\n
< ${red}Fuck bitches${green} get money \$\$\$\$ ${nocolor} >\n
 -----------------------------\n
        \   ^__^\n
         \  (oo)\_______\ \n
            (__)\       )\/\ \n
                ||----w |\n
                ||     ||\n
"

echo -e "${green}\$\$\$\$\$\$${nocolor} Setting up initial server requirements..."

## 0. Check EUID is root
if ((EUID != 0 ));
  then echo -e "${green}\$\$\$\$\$\$${nocolor} Must be executed as root!"
  exit
fi

## 1. Update and upgrade everything 
echo -e "${green}\$\$\$\$\$\$${nocolor} Updating packages..."
apt update 
echo -e "${green}\$\$\$\$\$\$${nocolor} Upgrading packages..."
apt upgrade -y

## 2. Download and install docker + deps
echo -e "${green}\$\$\$\$\$\$${nocolor} Installing docker + deps + other packages..."
apt install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    python3 \
    python3-pip \
    docker \
    docker-compose \
    htop -y ## cuz its cool

## 3. Install zsh && oh-my-zsh
echo -e "${green}\$\$\$\$\$\$${nocolor} Installing zsh..."
apt install zsh -y
echo -e "${green}\$\$\$\$\$\$${nocolor} Installing oh-my-zsh for extra cool stuff..."
## unattended install ohmyzsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

## install zsh addons
echo -e "${green}\$\$\$\$\$\$${nocolor} Installing extra zsh autosuggestions && syntax-highlighting..."

if ! test -f ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions;
    then
        ## clone zsh autosuggestions
        git clone https://github.com/zsh-users/zsh-autosuggestions.git ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions
    else
        echo "Skipping autosuggestions..."
fi

if ! test -f ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting;
    then
        ## clone zsh syntax-highlighting
        git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting
    else 
        echo "Skipping syntax highlighting..."
fi

## 4. Create .stuffrc file with zsh aliases and shortcuts
echo -e "${green}\$\$\$\$\$\$${nocolor} Creating .stuffrc config file..."
cat << EOF > ~/.stuffrc
## histfilesize & hist mem size
HISTFILESIZE=1000000
HISTSIZE=5000

## magic regex
## eg: ping www.google.com -c 1 | regex 'time=([0-9]+\.[0-9]+)' 1
## prints second capture group (39.317)
function regex { gawk 'match($0,/'$1'/,ary) {print ary['${2:-'0'}']}'; }

## common aliases
alias l='ls -l'
alias la='ls -la'
alias cls='clear'
alias py='python3'
alias vin='vim'
alias vi='vim'
alias dc='docker-compose'
alias dcr='docker-compose run'
alias dcb='docker-compose build'
alias botbk='docker-compose run freqtrade backtesting --datadir user_data/data/binance --export trades --stake-amount 100 --timeframe 1h --strategy-list GodStraNew DevilStra --timerange=20210101-'
alias botup='docker-compose up -d'
alias bothogod='docker-compose run freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss --spaces buy roi trailing sell --strategy GodStraNew'
alias bothodevil='docker-compose run freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss --spaces buy sell -s DevilStra'
EOF

## 5. Create .vimrc
echo -e "${green}\$\$\$\$\$\$${nocolor} Creating .vimrc..."
cat << EOF > ~/.vimrc 
" Syntax hl
syntax on
" Dont try to be compatible
set nocompatible
" Show cursor position
set ruler
" Show ln
set number
set relativenumber
" Encoding
set encoding=utf-8
set fileencoding=utf-8
set fileencodings=utf-8
set ttyfast
" Fix backspace deletes indent and more
set backspace=indent,eol,start
" Tab spaces
set tabstop=2
set softtabstop=0
set shiftwidth=2
set expandtab
" Search
set hlsearch
set incsearch
set ignorecase
set smartcase
set laststatus=2
EOF

## 6. Add plugins to .zshrc
if test -f ~/.zshrc;
    then
        echo -e "${green}\$\$\$\$\$\$${nocolor} Sed-ing new plugins in .zshrc..."
        sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/g' ~/.zshrc
    else
        echo -e "${red}!!!!!!${nocolor} No .zshrc file to update!"
fi

## 7. Add .stuffrc to .zshrc if it exists and not added
if test -f ~/.zshrc && ! grep ".stuffrc" ~/.zshrc;
    then
        echo -e "${green}\$\$\$\$\$\$${nocolor} Source-ing .stuffrc..."
        echo -e "\nsource ~/.stuffrc" >> ~/.zshrc
    else
        echo -e "${red}!!!!!!${nocolor} No .zshrc or sourced .stuffrc already!"
fi

## 8. Build the bot
docker-compose run --rm freqtrade create-userdir --userdir user_data
echo -e "${green}\$\$\$\$\$\$${nocolor} Create a config.json file, it can be overwritten later!"
docker-compose run --rm freqtrade new-config --config user_data/config.json

# build the image
docker-compose build

echo -e "${green}\$\$\$\$\$\$${nocolor} Downloading data 1m / 5m / 15m / 30m / 1h / 1d"
docker-compose run --rm freqtrade download-data --exchange binance -t 1m --timerange=20130101-
docker-compose run --rm freqtrade download-data --exchange binance -t 5m --timerange=20130101-
docker-compose run --rm freqtrade download-data --exchange binance -t 15m --timerange=20130101-
docker-compose run --rm freqtrade download-data --exchange binance -t 1h --timerange=20130101-
docker-compose run --rm freqtrade download-data --exchange binance -t 1d --timerange=20130101-

read -r "Generate ssh key? [y/n]: " yn
case $yn in
    [Yy]*) ssh-keygen;;
    [Nn]*) echo -e "${green}\$\$\$\$\$\$${nocolor} Not generating!";;
    *) echo -e "${green}\$\$\$\$\$\$${nocolor} Not generating!";;
esac

# Do a backtest?
read -r "Do a backtest? [y/n]: " yn
case $yn in
    [Yy]*) docker-compose run --rm freqtrade backtesting --datadir user_data/data/binance --export trades --stake-amount 100 --timeframe 1h --strategy-list GodStraNew DevilStra --timerange=20210101-;;
    [Nn]*) echo -e "${green}\$\$\$\$\$\$${nocolor} Not backtesting!";;
    *) echo -e "${green}\$\$\$\$\$\$${nocolor} Not backtesting!";;
esac

## TODO: disabled to test --config config_private.json, FIXME: not working?
# read -r "Overwrite config.json with existing config? [y/n]: " yn
# case $yn in
#     [Yy]*) cp user_data/config.json.bk user_data/config.json;;
#     [Nn]*) echo -e "${green}\$\$\$\$\$\$${nocolor} Not overwriting!";;
#     *) echo -e "${green}\$\$\$\$\$\$${nocolor} Not overwriting!";;
# esac

echo -e "${green}\$\$\$\$\$\$${nocolor} Done, you should reboot!"
zsh