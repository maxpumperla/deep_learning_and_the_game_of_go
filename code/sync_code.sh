#!/bin/bash

cd "${DLGO_HOME}"
git checkout chapter_$1

cp "${DLGO_SECRET_HOME}"/requirements.txt .
cp "${DLGO_SECRET_HOME}"/setup.py .

# dlgo main
DIR="dlgo"
if [ ! -d $DIR ]; then
  mkdir $DIR
fi

### CHAPTER 3
if [ $1 = "3" ]; then
  cp "${DLGO_SECRET_HOME}"/$DIR/__init__.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/zobrist.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/gotypes.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/goboard*.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/utils.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/scoring.py ./$DIR

  # agents
  DIR="dlgo/agent"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/__init__.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/base.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/helpers*.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/naive*.py ./$DIR

  # examples/scripts
  cp "${DLGO_SECRET_HOME}"/bot_v_bot.py .
  cp "${DLGO_SECRET_HOME}"/human_v_bot.py .
  cp "${DLGO_SECRET_HOME}"/generate_zobrist.py .



### CHAPTER 4
elif [ $1 = "4" ]; then
  cp "${DLGO_SECRET_HOME}"/$DIR/__init__.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/gotypes.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/goboard* ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/utils.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/zobrist.py ./$DIR

  # tree search
  cp -r "${DLGO_SECRET_HOME}"/$DIR/mcts ./$DIR
  cp -r "${DLGO_SECRET_HOME}"/$DIR/minimax ./$DIR
  cp -r "${DLGO_SECRET_HOME}"/$DIR/ttt ./$DIR

  # examples/scripts
  cp "${DLGO_SECRET_HOME}"/mcts_go.py .
  cp "${DLGO_SECRET_HOME}"/play_ttt.py .
  cp "${DLGO_SECRET_HOME}"/pruned_go.py .



### CHAPTER 5
elif [ $1 = "5" ]; then
  # networks from scratch
  cp -r "${DLGO_SECRET_HOME}"/$DIR/nn ./$DIR



### CHAPTER 6
elif [ $1 = "6" ]; then
  cp "${DLGO_SECRET_HOME}"/$DIR/__init__.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/gotypes.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/goboard* ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/utils.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/zobrist.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/scoring.py ./$DIR

  # encoders
  DIR="dlgo/encoders"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/__init__.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/base.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/oneplane.py ./$DIR

  # generated games
  cp -r "${DLGO_SECRET_HOME}"/generated_games .

  # examples/scripts
  cp -r "${DLGO_SECRET_HOME}"/chapter_6_cnn .
  cp "${DLGO_SECRET_HOME}"/generate_mcts_games.py .

  # networks
  DIR="dlgo/networks"
    if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/small.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/medium.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/large.py ./$DIR


### CHAPTER 7
elif [ $1 = "7" ]; then
  cp "${DLGO_SECRET_HOME}"/$DIR/*.py ./$DIR

  # gosgf
  cp -r "${DLGO_SECRET_HOME}"/$DIR/gosgf ./$DIR

  # data processor
  cp -r "${DLGO_SECRET_HOME}"/$DIR/data ./$DIR

  # http frontend
  cp -r "${DLGO_SECRET_HOME}"/$DIR/httpfrontend ./$DIR

  # model checkpoints
  cp -r "${DLGO_SECRET_HOME}"/checkpoints .

  # agents
  DIR="dlgo/agent"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/__init__.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/base.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/helpers* ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/naive* ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/predict.py ./$DIR

  # encoders
  DIR="dlgo/encoders"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/__init__.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/base.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/oneplane.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/sevenplane.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/betago.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/simple.py ./$DIR

  # model zoo
  DIR="agents"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/betago.hdf5 ./$DIR

  # model zoo
  DIR="examples"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/end_to_end.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/train_generator.py ./$DIR

  # networks
  DIR="dlgo/networks"
    if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/small.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/medium.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/large.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/fullyconnected.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/leaky.py ./$DI




### CHAPTER 8
elif [ $1 = "8" ]; then
  cp "${DLGO_SECRET_HOME}"/$DIR/*.py ./$DIR

  # examples/scripts
  cp "${DLGO_SECRET_HOME}"/Dockerfile .
  cp "${DLGO_SECRET_HOME}"/run_* .
  cp "${DLGO_SECRET_HOME}"/Dockerfile .
  cp "${DLGO_SECRET_HOME}"/gtp2ogs.js .
  cp "${DLGO_SECRET_HOME}"/package.json .
  cp "${DLGO_SECRET_HOME}"/web* .


  # gtp
  cp -r "${DLGO_SECRET_HOME}"/$DIR/gtp ./$DIR

  # gosgf
  cp -r "${DLGO_SECRET_HOME}"/$DIR/gosgf ./$DIR

  # data processor
  cp -r "${DLGO_SECRET_HOME}"/$DIR/data ./$DIR

  # http frontend
  cp -r "${DLGO_SECRET_HOME}"/$DIR/httpfrontend ./$DIR

  # model checkpoints
  cp -r "${DLGO_SECRET_HOME}"/checkpoints .

  # agents
  DIR="dlgo/agent"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/__init__.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/base.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/helpers* ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/naive* ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/predict.py ./$DIR

  # encoders
  DIR="dlgo/encoders"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/__init__.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/base.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/oneplane.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/sevenplane.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/betago.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/simple.py ./$DIR

  # model zoo
  DIR="agents"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/betago.hdf5 ./$DIR

  # model zoo
  DIR="examples"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/end_to_end.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/train_generator.py ./$DIR

  # networks
  DIR="dlgo/networks"
    if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/small.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/medium.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/large.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/fullyconnected.py ./$DIR
  cp "${DLGO_SECRET_HOME}"/$DIR/leaky.py ./$DIR



### CHAPTER 13
elif [ $1 = "13" ]; then
  cp "${DLGO_SECRET_HOME}"/$DIR/*.py ./$DIR

  # gtp
  cp -r "${DLGO_SECRET_HOME}"/$DIR/gtp ./$DIR

  # gosgf
  cp -r "${DLGO_SECRET_HOME}"/$DIR/gosgf ./$DIR

  # data processor
  cp -r "${DLGO_SECRET_HOME}"/$DIR/data ./$DIR

  # http frontend
  cp -r "${DLGO_SECRET_HOME}"/$DIR/httpfrontend ./$DIR

  # model checkpoints
  cp -r "${DLGO_SECRET_HOME}"/checkpoints .

  # agents
  cp -r "${DLGO_SECRET_HOME}"/$DIR/agent ./$DIR

  # encoders
  cp -r "${DLGO_SECRET_HOME}"/$DIR/encoders ./$DIR

  # networks
  cp -r "${DLGO_SECRET_HOME}"/$DIR/networks ./$DIR

  # model zoo
  DIR="agents"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/betago.hdf5 ./$DIR

  # alphago examples
  DIR="examples"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
    DIR="examples/alphago"
  if [ ! -d $DIR ]; then
    mkdir $DIR
  fi
  cp "${DLGO_SECRET_HOME}"/$DIR/* ./$DIR


else
  cp "${DLGO_SECRET_HOME}"/$DIR/*.py ./$DIR  # update basics regardless
	echo "Unknown chapter"
fi

git add .
git commit -m "update code for chapter $1"
git push --set-upstream origin chapter_$1
git checkout master
cd "${DLGO_SECRET_HOME}"
