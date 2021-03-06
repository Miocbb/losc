"""
Test code for the extended SCF procedure, `psi4_losc.scf.scf()` for integer
systems.
"""

import unittest
import psi4
from psi4_losc.scf import scf

psi4.core.be_quiet()

class TestSelfSCFIntegerAufbau(unittest.TestCase):
    """
    Test `psi4_losc.scf.scf()` for integer systems with aufbau occupations.
    """
    def setUp(self):
        self.mol_H = psi4.geometry("""
            0 2
            H
        symmetry c1
        """, name="H")
        self.mol_H_plus = psi4.geometry("""
            1 1
            H
        symmetry c1
        """, name="H+")
        self.mol_H2 = psi4.geometry("""
            0 1
            H
            H 1 1.2
        symmetry c1
        """, name="H2")
        self.mol_H2_plus = psi4.geometry("""
            1 2
            H
            H 1 1.2
        symmetry c1
        """, name="H2+")
        self.mol_H2O = psi4.geometry("""
            0 1
            O 0 0 0
            H 1 0 0
            H 0 1 0
        symmetry c1
        """, name="H2O")
        self.mol_H2O_plus = psi4.geometry("""
            1 2
            O 0 0 0
            H 1 0 0
            H 0 1 0
        symmetry c1
        """, name="H2O+")

        psi4.set_options({'guess':      'core',
                          'basis':      '3-21g',
                          'scf_type':   'df',
                          'e_convergence': 1e-8,
                          'maxiter': 100})

    def run_mol(self, mol, precision=7):
        """
        Compare the total energy between `psi4_losc.scf.scf()` and `psi4.energy()`.
        Three representative DFAs, svwn, blyp and b3lyp, are used for test.
        """
        psi4.core.set_active_molecule(mol)
        for dfa in 'hf svwn blyp b3lyp'.split():
            print(f'    Test mol {mol.name()}:  dfa={dfa}')
            E_ref = psi4.energy(dfa)
            wfn = scf(dfa)
            self.assertAlmostEqual(E_ref, wfn.energy(), places=precision)
        psi4.core.clean()

    def test_H_plus(self):
        """
        Test a very special case, H+, just a naked nuclear. The results should
        be zero.
        """
        print("\n==> Test H+: just a naked nuclear")
        self.run_mol(self.mol_H_plus)

    def test_uks_open_shell(self):
        """
        Test unrestricted calculations for open shell cases.
        """
        print("\n==> Test UKS Open Shell")
        optstash = psi4.driver.p4util.OptionsState(
            ['SCF', 'REFERENCE'],
            ['SCF', 'D_CONVERGENCE'],
            )
        psi4.core.set_local_option('SCF', 'REFERENCE','UHF')
        psi4.core.set_local_option('SCF', 'D_CONVERGENCE', 1.0e-4)

        self.run_mol(self.mol_H)
        self.run_mol(self.mol_H2_plus)
        self.run_mol(self.mol_H2O_plus, precision=5)

        optstash.restore()

    def test_uks_close_shell(self):
        """
        Test unrestricted calculations for close shell cases.
        """
        print("\n==> Test UKS Close Shell")
        optstash = psi4.driver.p4util.OptionsState(['SCF', 'REFERENCE'])
        psi4.core.set_local_option('SCF', 'REFERENCE','UHF')

        self.run_mol(self.mol_H2)
        self.run_mol(self.mol_H2O)

        optstash.restore()
    def test_rks_close_shell(self):
        """
        Test restricted calculations for close shell cases.
        """
        print("\n==> Test RKS Close Shell")
        optstash = psi4.driver.p4util.OptionsState(['SCF', 'REFERENCE'])
        psi4.core.set_local_option('SCF', 'REFERENCE','RHF')
        self.run_mol(self.mol_H2)
        self.run_mol(self.mol_H2O)

        optstash.restore()


if __name__ == '__main__':
    unittest.main()
