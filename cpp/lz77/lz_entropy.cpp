// lz_entropy.cpp - FIXED VERSION
// Uses divsufsort for suffix array construction

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cmath>
#include <cstring>
#include <algorithm>

extern "C" {
    #include "divsufsort.h"
}

// Build LCP (Longest Common Prefix) array from suffix array
std::vector<int> build_lcp(const unsigned char* text, int length, const int* sa) {
    std::vector<int> lcp(length, 0);
    std::vector<int> rank(length);
    
    for (int i = 0; i < length; i++) {
        rank[sa[i]] = i;
    }
    
    int h = 0;
    for (int i = 0; i < length; i++) {
        if (rank[i] > 0) {
            int j = sa[rank[i] - 1];
            while (i + h < length && j + h < length && text[i + h] == text[j + h]) {
                h++;
            }
            lcp[rank[i]] = h;
            if (h > 0) h--;
        }
    }
    
    return lcp;
}

// Improved LZ77 factorization
int lz77_factorize(const unsigned char* text, int length, const int* sa) {
    std::vector<int> lcp = build_lcp(text, length, sa);
    int num_factors = 0;
    int i = 0;
    
    while (i < length) {
        int max_len = 0;
        int max_pos = -1;
        
        // Find longest match in text[0..i-1]
        for (int j = 0; j < length; j++) {
            if (sa[j] >= i) continue;  // Only look at previous positions
            
            int pos = sa[j];
            int len = 0;
            
            // Calculate match length
            while (pos + len < i && i + len < length && 
                   text[pos + len] == text[i + len]) {
                len++;
            }
            
            if (len > max_len) {
                max_len = len;
                max_pos = pos;
            }
        }
        
        if (max_len > 0) {
            // Found a match - this is one factor
            i += max_len;
        } else {
            // No match - literal character
            i++;
        }
        
        num_factors++;
    }
    
    return num_factors;
}

struct CompressionStats {
    int length;
    int factors;
    double compressed_bits;
    double cid;
};

CompressionStats compute_cid(const std::string& data) {
    if (data.empty()) {
        throw std::runtime_error("Empty input");
    }
    
    int length = data.length();
    const unsigned char* text = reinterpret_cast<const unsigned char*>(data.c_str());
    
    // Build suffix array
    std::vector<int> sa(length);
    if (divsufsort(text, sa.data(), length) != 0) {
        throw std::runtime_error("Suffix array construction failed");
    }
    
    // Compute LZ77 factorization
    int num_factors = lz77_factorize(text, length, sa.data());
    
    // Calculate compressed size (KKP approximation)
    double compressed_bits = 0.0;
    if (num_factors > 0 && num_factors < length) {
        compressed_bits = num_factors * std::log2(num_factors) + 
                         2.0 * num_factors * std::log2(static_cast<double>(length) / num_factors);
    } else {
        // Fallback for edge cases
        compressed_bits = length * 8.0;  // Incompressible
    }
    
    CompressionStats stats;
    stats.length = length;
    stats.factors = num_factors;
    stats.compressed_bits = compressed_bits;
    stats.cid = compressed_bits / (length * 8.0);
    
    return stats;
}

void print_usage(const char* prog) {
    std::cerr << "Usage: " << prog << " [options] <input_file>\n\n";
    std::cerr << "Options:\n";
    std::cerr << "  -t           Tab-delimited output (length\\tfactors\\tcid)\n";
    std::cerr << "  -v           Verbose output\n";
    std::cerr << "  -h, --help   Show this help\n\n";
    std::cerr << "Computes LZ77-based compression entropy (CID).\n";
}

int main(int argc, char* argv[]) {
    bool tab_output = false;
    bool verbose = false;
    std::string filename;
    
    // Parse arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "-t") {
            tab_output = true;
        } else if (arg == "-v") {
            verbose = true;
        } else if (arg == "-h" || arg == "--help") {
            print_usage(argv[0]);
            return 0;
        } else if (arg[0] == '-') {
            std::cerr << "Unknown option: " << arg << "\n";
            print_usage(argv[0]);
            return 1;
        } else {
            filename = arg;
        }
    }
    
    if (filename.empty()) {
        std::cerr << "Error: No input file specified\n\n";
        print_usage(argv[0]);
        return 1;
    }
    
    try {
        // Read file
        std::ifstream file(filename, std::ios::binary);
        if (!file) {
            throw std::runtime_error("Cannot open file: " + filename);
        }
        
        std::string data((std::istreambuf_iterator<char>(file)),
                         std::istreambuf_iterator<char>());
        
        if (verbose) {
            std::cerr << "Read " << data.length() << " bytes from " << filename << "\n";
        }
        
        // Compute CID
        auto stats = compute_cid(data);
        
        // Output
        if (tab_output) {
            std::cout << stats.length << "\t" 
                     << stats.factors << "\t" 
                     << stats.cid << "\n";
        } else if (verbose) {
            std::cout << "Input length:         " << stats.length << " bytes\n";
            std::cout << "LZ77 factors:         " << stats.factors << "\n";
            std::cout << "Compressed size:      " << stats.compressed_bits << " bits\n";
            std::cout << "Compressed size:      " << stats.compressed_bits / 8.0 << " bytes\n";
            std::cout << "Compression ratio:    " << (1.0 - stats.compressed_bits / (stats.length * 8.0)) << "\n";
            std::cout << "CID (bits/char):      " << stats.cid << "\n";
        } else {
            std::cout << stats.cid << "\n";
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    
    return 0;
}
