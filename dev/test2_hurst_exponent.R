#
# Sep 3 - testing some R code
#

# import the library I need
library(fArma)

dir = "~/proba2gi/csv/"

# list the files in the directory
files = paste(dir,list.files(path = dir,pattern = "*.csv"),sep = '')

# number of files
nfiles = length(files)

d = list(0)

# read in each file
for (i in c(1:nfiles)) {

  filename = files[i]

  # read the comma separated file
  tbl <- read.csv(filename)

  # get the time and the emission
  time <- tbl$time
  emission <- tbl$emission

  d[i] = higuchiFit(emission, levels = 50, minnpts = 3, cut.off = 10^c(0.7, 2.5), doplot = TRUE, trace = FALSE, title = NULL, description = NULL)

}
