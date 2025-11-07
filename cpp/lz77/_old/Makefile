CXX = g++
CXXFLAGS = -O3 -std=c++17 -Wall
CC = gcc
CFLAGS = -O3 -Wall

# Object files
OBJS = common.o count.o divsufsort.o

all: lz_entropy gensa

# Main CID executable
lz_entropy: main.o $(OBJS)
	$(CXX) $(CXXFLAGS) -o lz_entropy main.o $(OBJS)

# Suffix array generator
gensa: gensa.o $(OBJS)
	$(CXX) $(CXXFLAGS) -o gensa gensa.o $(OBJS)

# C++ compilation
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $<

# C compilation (for divsufsort)
divsufsort.o: divsufsort.c
	$(CC) $(CFLAGS) -c $<

clean:
	rm -f *.o lz_entropy gensa

.PHONY: all clean
