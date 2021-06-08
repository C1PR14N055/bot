#!/bin/bash
# This script initializes the VPS setup

## 0. Script variables
install_docker_from_script=0 # 0 = from get-docker.sh, 1 = gpg key & install from repo

## check EUID is root
if ((EUID != 0 ));
  then echo "Must be executed as root!"
  exit
fi

## update everything
apt update 
## upgrade everything
apt upgrade -y

## generate ssh-key
# ssh-keygen -f ~/.ssh/known_hosts -R 139.180.142.51 
# ssh-copy-id root@139.180.142.51

## clone repo
while true; do
    git clone https://github.com/C1PR14N055/bot
    read -r -p "Did you clone the repo?" yn
    case $yn in
        [Yy]* ) echo "Ok!"; break;;
        [Nn]* ) continue;;
        * ) echo "Please answer y / n";;
    esac
done

## download and install docker
if [ $install_docker_from_script -eq 0 ]
    then curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
else
    ## add deps
    sudo apt-get install \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        git \
        python3 \
        python3-pip \
        htop ## cuz its cool

    ## curl gpg key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    ## install core docker
    sudo apt-get install docker-ce docker-ce-cli containerd.io
fi

## install zsh && oh-my-zsh
apt install zsh
sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"

## install zsh addons
## clone zsh autosuggestions
git clone https://github.com/zsh-users/zsh-autosuggestions.git "$ZSH_CUSTOM"/plugins/zsh-autosuggestions
## clone zsh syntax-highlighting
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$ZSH_CUSTOM"/plugins/zsh-syntax-highlighting

## add plugins to .zshrc
sed -i 's/plugins(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/g' .zshrc

## 2. Create .stuffrc file with zsh aliases and shortcuts
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
echo "source ~/.stuffrc" >> .zshrc

## 3. Create .vimrc
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

echo "Done!"