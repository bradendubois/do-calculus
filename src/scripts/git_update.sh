#!/usr/bin/sh

#########################################################
#                                                       #
#   Git Update                                          #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Pretty short. Two steps, both of which are important.

# The repository is private - you need to be on the list to see the repository or pull from it.
#   Once added, when attempting to pull (update, essentially), you need to log in to GitHub.
#   Very annoying to always have to do that *every* time though, so this will store your credentials
#   to ~/.git-credentials, so you log in once and they are saved.

# WARNING: These credentials are saved in PLAINTEXT. I can't do anything about that, but take any
#   precautions regarding that caveat. If you are concerned, just comment out the next line.

git config --global credential.helper store

# Set this so that it attempts to fast forward if there are updates

git config pull.ff only

# Pull from the repository and update the project.

git pull