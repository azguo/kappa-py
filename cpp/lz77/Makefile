CXX = g++
CXXFLAGS = -O3 -std=c++17 -Wall -Wextra
CC = gcc
CFLAGS = -O3 -Wall

all: lz_entropy

lz_entropy: lz_entropy.o divsufsort.o
	$(CXX) $(CXXFLAGS) -o lz_entropy lz_entropy.o divsufsort.o

lz_entropy.o: lz_entropy.cpp
	$(CXX) $(CXXFLAGS) -c lz_entropy.cpp

divsufsort.o: divsufsort.c divsufsort.h
	$(CC) $(CFLAGS) -c divsufsort.c

clean:
	rm -f *.o lz_entropy

test: lz_entropy
	@echo "Testing with simple patterns..."
	@echo "ABCABCABCABC" > test_repeat.txt
	@echo "AAAAAAAAAAAA" > test_same.txt
	@head -c 1000 /dev/urandom | base64 > test_random.txt
	@echo "Repeated pattern:"; ./lz_entropy -v test_repeat.txt
	@echo "\nSame character:"; ./lz_entropy -v test_same.txt
	@echo "\nRandom data:"; ./lz_entropy -v test_random.txt

.PHONY: all clean test
