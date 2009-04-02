# guess-renames
# Copyright (c) 2009 Colin Barrett <colin@springsandstruts.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

import guessrenames

def main():
    gr = guessrenames.MercurialCLIGuessRenames()
    gr.guess()
    gr.move()
