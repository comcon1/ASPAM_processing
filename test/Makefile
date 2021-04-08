all: rat1-h5.pdf rat1-dnav.xvg rat1-int15.xvg
	true

clean:
	rm -f rat1.xvg rat1-h5.pdf rat1-h5.pdf.data rat1-dnav.xvg rat1-int15.xvg

rat1.xvg:	test-data.xvg
	../src/extract-rat.py -i 25.01.2016 -t 08:00 -f test-data.xvg -o rat1.xvg -n 25 -c 1

rat1-h5.pdf: rat1.xvg
	../src/drawh5sec.py -i rat1.xvg -o rat1-h5.pdf -d 8:01 -n 20:00 

rat1-dnav.xvg: rat1.xvg
	../src/get-dn-averages.py -i rat1.xvg -o rat1-dnav.xvg -d 8:00 -n 20:05

rat1-int15.xvg: rat1.xvg
	../src/an-intervals.py -i rat1.xvg -o rat1-int15.xvg -d 8:00 -n 20:00 -m 15
