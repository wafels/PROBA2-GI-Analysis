;
; 31 aug 2011
;
; write out a CSV file
;
dir = '~/lyra/dat/test/'

filename = 'test1_writecsv.csv'

n = 100

f = randomn(seed,n)

t = findgen(n)

header = ['time','emission']

write_csv,dir + filename,t,f, header = header

end
