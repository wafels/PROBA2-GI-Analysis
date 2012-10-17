"""Example analysis script"""

import numpy as np
from scipy.stats import ks_2samp
import pickle


def main():

    functions = ['aggvarFit', 'diffvarFit', 'absvalFit', 'rsFit', 'higuchiFit']

    h=pickle.load( open('/Users/ireland/proba2gi/pickle/20110215_000000__20110215_000000.hurst.proba2gi.pickle', "rb"))

    # Do the two-sided K-S test
    for function in functions:
        print ' '
        print function
        for type1 in h.keys():
                h1 = np.array(h[type1][function])
                for type2 in h.keys():
                    h2 = np.array(h[type2][function])
                    kstest = ks_2samp(h1,h2)
                    print type1, len(h1), type2, len(h2), kstest


if __name__ == '__main__':
    main()
