#include <cmath>
#include <fstream>
#include <gtest/gtest.h>
#include <stdio.h>
#include <string>
#include <vector>

#include "matrix_helper.hpp"
#include "matrix_io.hpp"
#include <losc/local_occupation.hpp>

using Eigen::MatrixXd;
using Eigen::VectorXd;
using std::string;
using std::vector;

struct LocalOccupationTest : public ::testing::TestWithParam<string> {
    string file_path;
    string dir_path;

    virtual void SetUp() override
    {
        file_path = __FILE__;
        dir_path = file_path.substr(0, file_path.rfind("/"));
    }

    virtual void TearDown() override {}
};

TEST_P(LocalOccupationTest, test)
{
    // load data.
    string mol = GetParam();
    const char *mol_str = mol.c_str();
    string S_path = dir_path + "/./data/" + mol + "/ao_overlap.txt";
    string C_lo_path = dir_path + "/./data/" + mol + "/lo.txt";
    string D_path = dir_path + "/./data/" + mol + "/dfa_density.txt";
    string L_ref_path = dir_path + "/./data/" + mol + "/localocc.txt";
    MatrixXd S = test::read_matrices_from_txt(S_path)[0];
    auto C_lo = test::read_matrices_from_txt(C_lo_path);
    auto D = test::read_matrices_from_txt(D_path);
    auto L_ref = test::read_matrices_from_txt(L_ref_path);

    for (int is = 0; is < 2; is++) {
        C_lo[is].transposeInPlace();
    }

    for (int is = 0; is < 2; is++) {
        // Do calculation.
        MatrixXd L_calc = losc::local_occupation(C_lo[is], S, D[is]);

        // Testing.
        // True condition is the calculated Losc local occupation matrix matches
        // the reference to the 8-th digit.
        bool status = test::mtx_is_cwise_equal(L_calc, L_ref[is], 1e-8);
        if (!status) {
            std::cout << "Mol: " << mol << std::endl;
            std::cout << "data dir path: " << dir_path << std::endl;
            printf("%s, Reference Local occupation matrix: spin=%d\n", mol_str,
                   is);
            test::mtx_show_full(L_ref[is]);
            printf("%s, Calculated Local occupation matrix: spin=%d\n", mol_str,
                   is);
            test::mtx_show_full(L_calc);
        }
        EXPECT_TRUE(status);
    }
}

INSTANTIATE_TEST_SUITE_P(correction_test, LocalOccupationTest,
                         ::testing::Values("H2_1.0", "H2_10", "H2+_10", "H2O"));