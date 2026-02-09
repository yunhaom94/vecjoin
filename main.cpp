#include "include/constants.h" 

#include <iostream>
#include <fstream>
#include <vector>


struct FVecs {
    std::size_t n = 0;   // number of vectors
    std::size_t d = 0;   // dimension
    std::vector<float> data; // size n*d, row-major: data[i*d + j]
};

static std::uint64_t file_size_bytes(std::ifstream& in) {
    auto cur = in.tellg();
    in.seekg(0, std::ios::end);
    auto end = in.tellg();
    in.seekg(cur, std::ios::beg);
    return static_cast<std::uint64_t>(end);
}

FVecs read_fvecs(const std::string& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("Failed to open: " + path);

    // Read first dimension
    std::int32_t d32 = 0;
    in.read(reinterpret_cast<char*>(&d32), sizeof(d32));
    if (!in) throw std::runtime_error("Failed to read dimension from: " + path);
    if (d32 <= 0) throw std::runtime_error("Invalid dimension in file.");

    const std::size_t d = static_cast<std::size_t>(d32);

    // Compute number of vectors from file size
    in.seekg(0, std::ios::beg);
    const std::uint64_t sz = file_size_bytes(in);
    const std::uint64_t record_bytes = 4ull + 4ull * static_cast<std::uint64_t>(d);

    if (sz % record_bytes != 0) {
        throw std::runtime_error("File size is not a multiple of record size. "
                                 "Wrong dim or corrupt file?");
    }

    const std::size_t n = static_cast<std::size_t>(sz / record_bytes);

    FVecs out;
    out.n = n;
    out.d = d;
    out.data.resize(n * d);

    // Read all records
    in.seekg(0, std::ios::beg);
    for (std::size_t i = 0; i < n; ++i) {
        std::int32_t dim_check = 0;
        in.read(reinterpret_cast<char*>(&dim_check), 4);
        if (!in) throw std::runtime_error("Unexpected EOF reading dim.");
        if (dim_check != d32) throw std::runtime_error("Inconsistent dim in record.");

        in.read(reinterpret_cast<char*>(&out.data[i * d]), static_cast<std::streamsize>(4 * d));
        if (!in) throw std::runtime_error("Unexpected EOF reading vector data.");
    }

    std::cout << "Loaded n=" << out.n << " d=" << out.d << "\n";
    return out;
}


int main(int argc, char *argv[]) {
    auto fvecs = read_fvecs(DATASET);
    


    return 0;
}