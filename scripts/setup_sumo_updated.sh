#!/bin/bash

# Jeremy Lim
# jlim@wpi.edu
# Sets up a directory to use for SUMO_HOME, assuming you installed SUMO on the system already...

# Make directory
mkdir -p $HOME/sumo_binaries/bin
pushd

# instead of installing locally, make symlinks to the system install, and include some
# necessary files.


popd
# Optional: Use this if you get tired of "export SUMO_HOME=..." every time you start a terminal...
#echo 'export PATH="$HOME/sumo_binaries/bin:$PATH"' >> ~/.bashrc
#echo 'export SUMO_HOME="$HOME/sumo_binaries/bin"' >> ~/.bashrc