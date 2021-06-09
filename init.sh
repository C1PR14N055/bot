#!/bin/bash
# This script initializes the VPS setup
echo "\$\$\$ Setting up initial server requirements..."
## 0. Script variables
# install_docker_from_script=1 # 0 = from get-docker.sh, 1 = gpg key & install from repo

## check EUID is root
if ((EUID != 0 ));
  then echo "\$\$\$ Must be executed as root!"
  exit
fi

## 1. Update and upgrade everything 
echo "\$\$\$ Updating packages..."
apt update 
echo "\$\$\$ Upgrading packages..."
apt upgrade -y

## 2. Download and install docker + deps
echo "\$\$\$ Installing docker + deps + other packages..."
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
echo "\$\$\$ Installing zsh..."
apt install zsh -y
echo "\$\$\$ Installing oh-my-zsh for extra cool stuff..."
# sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
## install normally and exit zsh env afterwards, so that .zshrc is created
sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)" && exit

## install zsh addons
echo "\$\$\$ Installing extra zsh autosuggestions && syntax-highlighting..."
## clone zsh autosuggestions
git clone https://github.com/zsh-users/zsh-autosuggestions.git ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions
## clone zsh syntax-highlighting
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting

## add plugins to .zshrc
echo "\$\$\$ Sed-ing new plugins in .zshrc..."
sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/g' ~/.zshrc

## 4. Create .stuffrc file with zsh aliases and shortcuts
echo "\$\$\$ Creating .stuffrc config file..."
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
alias dcr='docker-compose run'
alias dcb='docker-compose build'
alias botbk='docker-compose run freqtrade backtesting --datadir user_data/data/binance --export trades --stake-amount 100 --timeframe 1h --strategy-list GodStraNew DevilStra --timerange=20210101-'
alias botup='docker-compose up -d'
alias bothogod='docker-compose run freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss --spaces buy roi trailing sell --strategy GodStraNew'
alias bothodevil='docker-compose run freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss --spaces buy sell -s DevilStra'
EOF

## Add .stuffrc to .zshrc
grep ".stuffrc" ~/.zshrc
if [ $? -ne 0 ]
    then
        echo "\$\$\$ Source-ing .stuffrc..."
        echo -e "\nsource ~/.stuffrc" >> ~/.zshrc
fi

## 5. Create .vimrc
echo "\$\$\$ Creating .vimrc..."
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

echo "\$\$\$ Done!"