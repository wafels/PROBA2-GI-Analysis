#
# Sep 3 - testing some R code
#


dir = "~/lyra/dat/test/"

# list the files in the directory
files = paste(dir,list.files(path = dir,pattern = "*.csv"),sep = '')

# number of files
nfiles = length(files)

# read in each file
for (i in c(1:nfiles)) {

  filename = files[i]

  # read the comma separated file
  tbl <- read.csv(fullpath)

  # get the time and the emission
  time <- tbl$time
  emission <- tbl$emission

}
