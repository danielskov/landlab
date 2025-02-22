import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal
from landlab import BAD_INDEX_VALUE as XX
try:
    from nose.tools import assert_is
except ImportError:
    from landlab.testing.tools import assert_is

from landlab import RasterModelGrid
import landlab.grid.mappers as maps


class TestPatchesAtNode():

    patch_values = np.array([[0, -1, -1, -1],
                             [1,  0, -1, -1],
                             [2,  1, -1, -1],
                             [3,  2, -1, -1],
                             [-1,  3, -1, -1],
                             [4, -1, -1,  0],
                             [5,  4,  0,  1],
                             [6,  5,  1,  2],
                             [7,  6,  2,  3],
                             [-1,  7,  3, -1],
                             [8, -1, -1,  4],
                             [9,  8,  4,  5],
                             [10,  9,  5,  6],
                             [11, 10,  6,  7],
                             [-1, 11,  7, -1],
                             [-1, -1, -1,  8],
                             [-1, -1,  8,  9],
                             [-1, -1,  9, 10],
                             [-1, -1, 10, 11],
                             [-1, -1, 11, -1]])

    patch_mask = np.array([[False,  True,  True,  True],
                           [False, False,  True,  True],
                           [False, False,  True,  True],
                           [False, False,  True,  True],
                           [True, False,  True,  True],
                           [False,  True,  True, False],
                           [False, False, False, False],
                           [False, False, False, False],
                           [False, False, False, False],
                           [True, False, False,  True],
                           [False,  True,  True, False],
                           [False, False, False, False],
                           [False, False, False, False],
                           [False, False, False, False],
                           [True, False, False,  True],
                           [True,  True,  True, False],
                           [True,  True, False, False],
                           [True,  True, False, False],
                           [True,  True, False, False],
                           [True,  True, False,  True]])

    def test_create_masked(self):
        rmg = RasterModelGrid((4, 5))
        patches_out = rmg.patches_at_node(masked=True)

        assert_array_equal(patches_out.data, self.patch_values)

        assert_array_equal(patches_out.mask, self.patch_mask)

        # check we can change:
        patches_out2 = rmg.patches_at_node(masked=False)
        assert_array_equal(patches_out2, patches_out.data)

    def test_create_unmasked(self):
        rmg = RasterModelGrid((4, 5))
        patches_out = rmg.patches_at_node(masked=False, nodata='bad_value')
        patch_values_BAD = self.patch_values.copy()
        patch_values_BAD[patch_values_BAD == -1] = XX
        assert_array_equal(patches_out, patch_values_BAD)
        patches_out2 = rmg.patches_at_node(masked=True, nodata=-1)
        assert_array_equal(patches_out2.data, self.patch_values)
        assert_array_equal(patches_out2.mask, self.patch_mask)

    def test_nodes_at_patch(self):
        rmg = RasterModelGrid((4, 5))
        nodes_out = rmg.nodes_at_patch
        assert_array_equal(nodes_out,
                           np.array([[6,  5,  0,  1],
                                     [7,  6,  1,  2],
                                     [8,  7,  2,  3],
                                     [9,  8,  3,  4],
                                     [11, 10,  5,  6],
                                     [12, 11,  6,  7],
                                     [13, 12,  7,  8],
                                     [14, 13,  8,  9],
                                     [16, 15, 10, 11],
                                     [17, 16, 11, 12],
                                     [18, 17, 12, 13],
                                     [19, 18, 13, 14]]))


class TestSlopesAtPatches():

    def test_slopes_at_patches(self):
        rmg = RasterModelGrid((4, 5))
        rmg.at_node['topographic__elevation'] = rmg.node_x.copy()
        slopes_out = rmg.node_slopes(unit='degrees')
        assert_array_almost_equal(slopes_out, np.full(20, 45., dtype=float))

    def test_slopes_at_patches_comps(self):
        rmg = RasterModelGrid((4, 5))
        rmg.at_node['topographic__elevation'] = rmg.node_x.copy()
        slopes_out = rmg.node_slopes(unit='radians', return_components=True)
        assert_array_almost_equal(slopes_out[0].data,
                                  np.full(20, np.pi / 4., dtype=float))
        assert_array_almost_equal(slopes_out[1][0].data,
                                  np.ones(20, dtype=float))
        assert_array_almost_equal(slopes_out[1][1].data,
                                  np.zeros(20, dtype=float))
