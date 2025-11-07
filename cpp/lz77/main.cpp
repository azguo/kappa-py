// first attempt at implementing LZ77 for 1D shear model

#include <iostream>
#include <fstream>
#include <cstring>
#include <cstdlib>
#include <cmath>
#include "kkp/algorithm/kkp.h"

int main(int argc, char *argv[]){
	if(argc != 2){
		std::cerr << "usage: " << argv[0] << " inputfile safile\n";
		std::cerr << "inputfile is pre-discretized from 1D toy model output\n";
		std::cerr << "safile is corresponding suffix array file\n";
		return(1);
	}

	// read pre-binned file
	std::string seq, filename = argv[1];
	std::ifstream namefile; 
	namefile.open(argv[1]);
	std::getline(namefile, seq);
	int length = seq.length();
	std::cerr << ".........\nreading sequence from file " << argv[1] << "\n";
	std::cerr << "sequence: " << seq << "\n";
	std::cerr << "sequence length : " << length << "\n";
	namefile.close();

	// read suffix array
	//int *suffixarray(new int[length + 2]);
	int *suffixarray = NULL;
	suffixarray = new int[length + 2];
	std::string sanamefile = "sa_" + filename;
	std::fstream saf(sanamefile.c_str(), std::fstream::in);
	saf.read((char *)suffixarray, sizeof(int) * length);
	std::cerr << "read " << saf.gcount() << " bytes\n";
	saf.close();
	
	// calculate LZ77
	unsigned char* text = (unsigned char*)seq.c_str();
	std::cerr << "calculating factors now\n";

	std::vector<std::pair<int,int> > factors;
	int nfactors = kkp2(text, suffixarray, length, &factors);
	std::cerr << "nfactors: " << nfactors << std::endl;
	std::cerr << "original length: " << length << std::endl;
	//double sumcompressed = 0;
	//for (std::pair<int,int>&factor : factors){
	//	sumcompressed += log2(std::to_string(factor.first).length()) + log2(std::to_string(factor.second).length());
	//}
	double cid = (double)nfactors * log2(nfactors) + 2 * nfactors * log2((double) length / nfactors);
	std::cerr << "compressed length from approximation: " << cid << std::endl;
	std::cerr << "CID: " << std::endl;
	//std::cerr << cid / saf.gcount() << std::endl;
	std::cerr << cid / length << std::endl;
	//std::cerr << "compressed length from summing log terms: " << sumcompressed << std::endl;
	//std::cerr << "CID: " << sumcompressed / length << std::endl;

	return 0;
}

