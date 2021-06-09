#!/bin/bash

green='\033[0;32m'
red='\033[0;31m'

echo -e "${green}# < Hey there h00man! > \n
#  ------------------ \n
#         \   ^__^\n
#          \  (oo)\_______\n
#             (__)\       )\/\\\n
#                 ||----w |\n
#                 ||     ||\n"

# This script initializes the VPS. It updates / upgrades / installs deps, adds aliases, customizes shell,
# customizes vim, 
echo -e "\$\$\$\$\$\$ ${green}Setting up initial server requirements..."
exit

## 0. Check EUID is root
if ((EUID != 0 ));
  then echo "\$\$\$\$\$\$ Must be executed as root!"
  exit
fi

## 1. Update and upgrade everything 
echo "\$\$\$\$\$\$ Updating packages..."
apt update 
echo "\$\$\$\$\$\$ Upgrading packages..."
apt upgrade -y

## 2. Download and install docker + deps
echo "\$\$\$\$\$\$ Installing docker + deps + other packages..."
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
echo "\$\$\$\$\$\$ Installing zsh..."
apt install zsh -y
echo "\$\$\$\$\$\$ Installing oh-my-zsh for extra cool stuff..."
## unattended install ohmyzsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

## install zsh addons
echo "\$\$\$\$\$\$ Installing extra zsh autosuggestions && syntax-highlighting..."

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
echo "\$\$\$\$\$\$ Creating .stuffrc config file..."
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
echo "\$\$\$\$\$\$ Creating .vimrc..."
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
        echo "\$\$\$\$\$\$ Sed-ing new plugins in .zshrc..."
        sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/g' ~/.zshrc
    else
        echo "!!!!!! No .zshrc file to update!"
fi

## 7. Add .stuffrc to .zshrc if it exists and not added
if test -f ~/.zshrc && ! grep ".stuffrc" ~/.zshrc;
    then
        echo "\$\$\$\$\$\$ Source-ing .stuffrc..."
        echo -e "\nsource ~/.stuffrc" >> ~/.zshrc
    else
        echo "!!!!!! No .zshrc or sourced .stuffrc already!"
fi

## 8. Build the bot
docker-compose --rm bot freqtrade create-userdir --userdir user_data
echo "\$\$\$\$\$\$ Create a config.json file, it can be overwritten later!"
docker-compose --rm bot new-config --config user_data/config.json
read -r "\$\$\$\$\$\$ Overwrite config.json with existing config?" yn
case $yn in
    [Yy]*) cp user_data/config.json.bk user_data/config.json;;
    [Nn]*) echo "\$\$\$\$\$\$ Not overwriting!";;
    *) echo "\$\$\$\$\$\$ Not overwriting!";;
esac
docker-compose build

echo "\$\$\$\$\$\$ Downloading data 1m / 5m / 15m / 30m / 1h / 1d"
docker-compose --rm bot download-data -t 1m
docker-compose --rm bot download-data -t 5m
docker-compose --rm bot download-data -t 15m
docker-compose --rm bot download-data -t 30m
docker-compose --rm bot download-data -t 1h
docker-compose --rm bot download-data -t 1d

read -r "\$\$\$\$\$\$ Generate ssh key?" yn
case $yn in
    [Yy]*) ssh-keygen;;
    [Nn]*) echo "\$\$\$\$\$\$ Not generating!";;
    *) echo "\$\$\$\$\$\$ Not generating!";;
esac

echo "\$\$\$\$\$\$ Done, you should reboot!"

zsh