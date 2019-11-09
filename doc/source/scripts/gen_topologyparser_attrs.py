#!/usr/bin/env python
"""
Generate two tables:
    - connectivityattrs.txt: A table of supported formats for bonds, angles, dihedrals, impropers
    - topologyattrs.txt: A table of supported formats for non-connectivity attributes.
    - topology_parsers.txt: A table of all formats and the attributes they read and guess

This script imports the testsuite, which tests these.
"""
import os
import sys
from collections import defaultdict
from core import DESCRIPTIONS, ATTRS
from base import TableWriter

import MDAnalysis as mda

tests = os.path.join(mda.__path__[0], '..', '..', 'testsuite', 'MDAnalysisTests')
sys.path.append(tests)

from topology.base import mandatory_attrs
from topology.test_crd import TestCRDParser
from topology.test_dlpoly import TestDLPHistoryParser, TestDLPConfigParser
from topology.test_dms import TestDMSParser
from topology.test_gms import GMSBase
from topology.test_gro import TestGROParser
from topology.test_gsd import TestGSDParser
from topology.test_hoomdxml import TestHoomdXMLParser
from topology.test_lammpsdata import LammpsBase, TestDumpParser
from topology.test_mmtf import TestMMTFParser
from topology.test_mol2 import TestMOL2Base
from topology.test_pdb import TestPDBParser
from topology.test_pdbqt import TestPDBQT
from topology.test_pqr import TestPQRParser
from topology.test_psf import PSFBase
from topology.test_top import TestPRMParser
from topology.test_tprparser import TPRAttrs
from topology.test_txyz import TestTXYZParser
from topology.test_xpdb import TestXPDBParser
from topology.test_xyz import XYZBase

PARSER_TESTS = (TestCRDParser, TestDLPHistoryParser, TestDLPConfigParser, 
                TestDMSParser, GMSBase,
                TestGROParser, TestGSDParser, TestHoomdXMLParser, 
                LammpsBase, TestMMTFParser, TestMOL2Base, 
                TestPDBParser, TestPDBQT, TestPQRParser, PSFBase, 
                TestPRMParser, TPRAttrs, TestTXYZParser, 
                TestXPDBParser, XYZBase, TestDumpParser)

MANDATORY_ATTRS = set(mandatory_attrs)

parser_attrs = {}

for p in PARSER_TESTS:
    e, g = set(p.expected_attrs)-MANDATORY_ATTRS, set(p.guessed_attrs)
    parser_attrs[p.parser] = (e, g)

class TopologyParsers(TableWriter):
    headings = ['Format', 'Attributes read', 'Attributes guessed']
    filename = 'formats/topology_parsers.txt'
    sort = True

    def __init__(self):
        self.attrs = defaultdict(set)
        super(TopologyParsers, self).__init__()

    def _set_up_input(self):
        return [[x, *y] for x, y in parser_attrs.items()]

    def get_line(self, parser, expected, guessed):
        line = super(TopologyParsers, self).get_line(parser, expected, guessed)
        for a in expected|guessed:
            self.attrs[a].add(self.fields['Format'][-1])
        return line
    
    def _format(self, parser, *args):
        f = parser.format
        if isinstance(f, (list, tuple)):
            key = f[0]
            label = ', '.join(f)
        else:
            key = label = f
        
        return self.sphinx_ref(label, key)
    
    def _attributes_read(self, parser, expected, guessed):
        vals = sorted(expected - guessed)
        return ', '.join(vals)
    
    def _attributes_guessed(self, parser, expected, guessed):
        return ', '.join(sorted(guessed))
    

class TopologyAttrs(TableWriter):

    headings = ('Atom', 'AtomGroup', 'Description', 'Supported formats')
    filename = 'generated/topology/topologyattrs.txt'

    def __init__(self, attrs):
        self.attrs = attrs
        super(TopologyAttrs, self).__init__()

    def _set_up_input(self):
        return sorted([x, *y] for x, y in ATTRS.items() if x not in MANDATORY_ATTRS)
    
    def _atom(self, name, singular, *args):
        return singular
    
    def _atomgroup(self, name, *args):
        return name
    
    def _description(self, name, singular, description):
        return description
    
    def _supported_formats(self, name, singular, description):
        return ', '.join(sorted(self.attrs[name]))

class ConnectivityAttrs(TopologyAttrs):
    headings = ('Atom', 'AtomGroup', 'Supported formats')
    filename = 'generated/topology/connectivityattrs.txt'

    def _set_up_input(self):
        inp = [[x]*3 for x in 'bonds angles dihedrals impropers'.split()]
        return inp


if __name__ == '__main__':
    top = TopologyParsers()
    TopologyAttrs(top.attrs)
    ConnectivityAttrs(top.attrs)