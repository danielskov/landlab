#! /usr/bin/env python

import numpy
from six.moves import range

from .voronoi import VoronoiDelaunayGrid


class RadialModelGrid(VoronoiDelaunayGrid):

    """Grid of concentric circles.

    This inherited class implements a circular grid in which grid nodes are
    placed at regular radial and semi-regular arc-wise intervals. That is,
    if the radial spacing between *shells* is *dr*, the nodes are placed around
    the circular shell at regular intervals that get as close as possible to
    *dr*. The points are then arranged in a Delaunay triangulation with Voronoi
    cells. Within each ring, nodes are numbered according to Landlab
    convention, from the first node counterclockwise of east. Numbering
    begins at the centermost node and works outwards through the rings.

    Parameters
    ----------
    num_shells : int
        Number of rings in the grid.
    dr : float, optional
        Radial interval for rings.
    origin_x : float, optional
        x-coordinate of origin node.
    origin_y : float, optional
        y-coordinate of origin node.

    Returns
    -------
    RadialModelGrid
        A newly-created grid.

    Examples
    --------
    A grid with just one ring will have a node at the origin surrounded
    by six other nodes.

    >>> from landlab import RadialModelGrid
    >>> omg = RadialModelGrid(num_shells=1, dr=1., origin_x=0., origin_y=0.)
    >>> omg.number_of_nodes
    7
    >>> omg.number_of_cells
    1

    A second rings will have 13 nodes.

    >>> omg = RadialModelGrid(2)
    >>> omg.number_of_nodes
    20
    """

    def __init__(self, num_shells=0, dr=1.0, origin_x=0.0, origin_y=0.0,
                 **kwds):
        """Create a circular grid.

        Create a circular grid in which grid nodes are placed at regular
        radial and semi-regular arc-wise intervals. That is, if the radial
        spacing between *shells* is *dr*, the nodes are placed around the
        circular shell at regular intervals that get as close as possible to
        *dr*.  The points are then arranged in a Delaunay triangulation with
        Voronoi cells.

        Parameters
        ----------
        num_shells : int
            Number of rings in the grid.
        dr : float, optional
            Radial interval for rings.
        origin_x : float, optional
            x-coordinate of origin node.
        origin_y : float, optional
            y-coordinate of origin node.

        Returns
        -------
        RadialModelGrid
            A newly-created grid.

        Examples
        --------
        A grid with just one ring will have a node at the origin surrounded
        by six other nodes.

        >>> from landlab import RadialModelGrid
        >>> omg = RadialModelGrid(num_shells=1, dr=1., origin_x=0., origin_y=0.)
        >>> omg.number_of_nodes
        7
        >>> omg.number_of_cells
        1

        A second rings will have 13 nodes.

        >>> omg = RadialModelGrid(2)
        >>> omg.number_of_nodes
        20
        """
        # Set number of nodes, and initialize if caller has given dimensions
        if num_shells > 0:
            self._initialize(num_shells, dr, origin_x, origin_y)
        super(RadialModelGrid, self).__init__(**kwds)

    @classmethod
    def from_dict(cls, params):
        num_shells = params['num_shells']
        dr = params.get('dr', 1.)
        origin = params.get('origin', (0., 0.))

        return cls(num_shells=num_shells, dr=dr, origin_x=origin[0],
                   origin_y=origin[1])

    def _initialize(self, num_shells, dr, origin_x=0.0, origin_y=0.0):
        [pts, npts] = self.make_radial_points(num_shells, dr)
        self._n_shells = int(num_shells)
        self._dr = dr
        super(RadialModelGrid, self)._initialize(pts[:, 0], pts[:, 1])

    def make_radial_points(self, num_shells, dr, origin_x=0.0, origin_y=0.0):
        """Create a set of points on concentric circles.

        Creates and returns a set of (x,y) points placed in a series of
        concentric circles around the origin.
        """
        shells = numpy.arange(0, num_shells) + 1
        twopi = 2 * numpy.pi
        # number of points in each shell
        n_pts_in_shell = numpy.round(twopi * shells)
        dtheta = twopi / n_pts_in_shell
        npts = int(sum(n_pts_in_shell) + 1)
        pts = numpy.zeros((npts, 2))
        r = shells * dr
        startpt = 1
        for i in numpy.arange(0, num_shells):
            theta = (dtheta[i] * numpy.arange(0, n_pts_in_shell[i]) +
                     dtheta[i] / (i + 1))
            ycoord = r[i] * numpy.sin(theta)
            if numpy.isclose(ycoord[-1], 0.):
                # this modification necessary to force the first ring to
                # follow our new CCW from E numbering convention (DEJH, Nov15)
                ycoord[-1] = 0.
                pts[startpt:(startpt + int(n_pts_in_shell[i])),
                    0] = numpy.roll(r[i] * numpy.cos(theta), 1)
                pts[startpt:(startpt + int(n_pts_in_shell[i])),
                    1] = numpy.roll(ycoord, 1)
            else:
                pts[startpt:(startpt + int(n_pts_in_shell[i])),
                    0] = r[i] * numpy.cos(theta)
                pts[startpt:(startpt + int(n_pts_in_shell[i])),
                    1] = ycoord
            startpt += int(n_pts_in_shell[i])
        pts[:, 0] += origin_x
        pts[:, 1] += origin_y

        return pts, npts

    @property
    def number_of_shells(self):
        """Number of node shells in grid.

        Returns
        -------
        int
            The number of node shells in the radial grid (not counting the
            center node).
        """
        return self._n_shells

    @property
    def shell_spacing(self):
        """Fixed distance between shells."""
        return self._dr

    @property
    def number_of_nodes_in_shell(self):
        """Number of nodes in each shell.

        Returns
        -------
        int
            Number of nodes in each shell, excluding the center node.
        """
        try:
            return self._nnodes_inshell
        except AttributeError:
            n_pts_in_shell = numpy.round(2. * numpy.pi * (
                numpy.arange(self.number_of_shells, dtype=float) + 1.))
            self._nnodes_inshell = n_pts_in_shell.astype(int)
            return self._nnodes_inshell

    @property
    def radius_to_shell(self):
        """Distance from central node to each shell.

        Returns
        -------
        ndarray of float
            The distance from the central node to each shell.
        """
        return ((numpy.arange(self.number_of_shells, dtype=float) + 1.) *
                self.shell_spacing)

    @property
    def radius_at_node(self):
        """Distance for center node to each node.

        Returns
        -------
        ndarray of float
            The distance from the center node of each node.
        """
        try:
            return self._node_radii
        except AttributeError:
            self._node_radii = numpy.empty(self.number_of_nodes, dtype=float)
            self._node_radii[0] = 0
            start_index = 1
            for i in range(self.number_of_shells):
                end_index = start_index + self.number_of_nodes_in_shell[i]
                self._node_radii[start_index:
                                 end_index] = self.radius_to_shell[i]
                start_index = end_index
            return self._node_radii
