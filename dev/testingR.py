import rpy2

import numpy as np
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects


# the R session now has the package loaded into it

def main():
    r = robjects.r
    fArma = importr("fArma")

    randn = np.random.randn

    x = robjects.vectors.FloatVector(randn(10000))

    output = r.aggvarFit(x, levels = 50, minnpts = 3)
    print('Hurst exponent from aggvarFit')
    print(output.do_slot("hurst")[0])
    print('Standard error from aggvarFit')
    print(output.do_slot("hurst")[2][1][1])
    return output
    
if __name__ == '__main__':
    main()