CC= clang
CFLAG= -std=c99 -Wall -pedantic
pypath = -I/usr/include/python3.7m

all: _molecule.so

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so -lm

mol.o: mol.c mol.h
	$(CC) $(CFLAG) -c mol.c -fPIC -o mol.o

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAG) $(pypath) -c -fPIC molecule_wrap.c -o molecule_wrap.o

_molecule.so: molecule_wrap.o libmol.so
	$(CC) molecule_wrap.o -shared -dynamiclib -lm -lpython3.7m -L. -lmol -o _molecule.so 

molecule_wrap.c: molecule.i
	swig -python molecule.i

exportPath:
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd):/usr/lib/python3.7/config-3.7m-x86_64-linux-gnu/:/usr/include/python3.7m
	export LD_LIBRARY_PATH=.
	

clean:
	rm *.o *.so molecule.py molecule_wrap.c

