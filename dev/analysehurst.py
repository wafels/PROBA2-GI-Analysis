"""Example analysis script"""

import numpy as np
from scipy.stats import ks_2samp
import pickle
from matplotlib import pyplot as plt

def main():

    functions = ['aggvarFit', 'diffvarFit', 'absvalFit', 'rsFit', 'higuchiFit']

    #h=pickle.load( open('/Users/ireland/proba2gi/pickle/summedup_to_1second_factoris3_20110215_000000__20110314_000000.hurst.proba2gi.pickle', "rb"))
    #h=pickle.load( open('/Users/ireland/proba2gi/pickle/20120608_000000__20120619_000000.hurst.proba2gi.pickle', "rb"))
    h = pickle.load( open('/Users/ireland/proba2gi/pickle/20120608_000000__20120708_000000.hurst.proba2gi.pickle', "rb"))

    #h = dict( h1.items() + h2.items())

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
                    fig = plt.figure()
                    plt.hist(h1, bins=20, label=type1)
                    plt.hist(h2, bins=20, label=type2)
                    plt.title('Fitting algorithm: '+function)
                    plt.xlabel('Estimated Hurst exponent')
                    plt.ylabel('Number')
                    plt.legend( (type1 + ' ('+str(len(h1))+')', type2 + ' ('+str(len(h2))+')'), fontsize=12 )
                    fig.savefig('/Users/ireland/proba2gi/png/' + function + '_'+ type1 + '_' + type2)
    return h

if __name__ == '__main__':
    main()
