;
; 31 aug 2011
;
; write out a CSV file
;
dir = '~/lyra/dat/test/'

rootname = 'test_writecsv'
extension = '.csv'

n = 5000
nfile = 19


for i = 0, nfile-1 do begin
   if i le 9 then begin
      number = '00'+trim(i) 
   endif else begin
      if i ge 10 and i le 99 then begin
         number = '0'+trim(i)
      endif else begin
         number = trim(i)
      endelse
   endelse

   f = randomn(seed,n)
   
   t = findgen(n)

   header = ['time','emission']

   filename = rootname + number + extension

   write_csv,dir + filename,t,f, header = header

endfor


end
