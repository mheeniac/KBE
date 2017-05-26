#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Fokker Aerostructures
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
# KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR
# PURPOSE.

from __future__ import division
from parapy.core import Base, Attribute, Input


class AnalyticPanelBucklingAnalysis(Base):
    """Perform an analytical buckling analysis
    The analysis is based on TH3.372

    The class expects d_matrix values
    D_ij = 1/3 * sum_of_all_plies(Q_ij * (z_(ply)**3 - z_(ply-1)**3)
    Q_ij are elements from the matrix [Q] in [stress] = [Q][strain]
    z_(ply) is the distance of the positive side of the ply to the neutral axis
    z_(ply-1) = z_(ply) - ply_thickness

    Only specially orthotropic plates are considered, i.e. D_13 = D_23 = 0 Usage:

    >>> obj = AnalyticPanelBucklingAnalysis(panel_length=500., panel_width=227.5,
    ...                                     D_11=3069022, D_22=3069022, D_33=1051600.3,
    ...                                     D_12=965821.3, clamping_factor=0.66667,
    ...                                     compression_running_load=-410.,
    ...                                    shear_running_load=300.)
    >>> obj.rf_combined
    8.246596195509994
    """

    #: unit must be 'mm'
    #: :type: float
    panel_length = Input()

    #: unit must be 'mm'
    #: :type: float
    panel_width = Input()

    #: unit must be 'Nmm'
    #: :type: float
    D_11 = Input()

    #: unit must be 'Nmm'
    #: :type: float
    D_22 = Input()

    #: unit must be 'Nmm'
    #: :type: float
    D_33 = Input()

    #: unit must be 'Nmm'
    #: :type: float
    D_12 = Input()

    #: this factor determines to what extend the edges are clamped
    #: clamping_factor = 0 means that all edges are simply supported
    #: clamping_factor = 1 means that two edges are fully clamped and two edges are simply supported
    #: clamping_factor between 0 and 1 means that the edges are more or less clamped
    #: :type: float
    clamping_factor = Input(0)

    #: unit must be 'N/mm'
    #: :type: float
    compression_running_load = Input(0)

    #: unit must be 'N/mm'
    #: :type: float
    shear_running_load = Input(0)

    #: D_13 and D_23 are assumed to be zero or negligible

    # ---------------------------------------------------------------------------------------------
    # ----------------------------COMPRESSION-BUCKLING---------------------------------------------
    # ---------------------------------------------------------------------------------------------

    @Attribute
    def beta(self):
        """This attribute represents a constant that is a value for the difference in length and
        material properties in two perpendicular directions.

        :rtype: float
        """
        return (self.panel_length / self.panel_width) * ((self.D_22 / self.D_11) ** 0.25)

    @Attribute
    def gamma(self):
        """This attribute represents a constant that is a value for the average bending
        stiffness of the panel.

        :rtype: float
        """
        return (self.D_12 + 2 * self.D_33) / ((self.D_11 * self.D_22) ** 0.5)

    @Attribute
    def k_compr_ssss_star(self):
        """This attribute represents the buckling load factor k* as a function of beta. It has
        been determined by a curve fit of a graph from TH3.372. This buckling load factor k is
        valid for fully simply supported cases.

        :rtype: float
        """
        if self.beta < 0.6:
            return 23.975 * self.beta ** -1.4132
        elif self.beta < 1.4:
            return -62.5 * self.beta ** 3 + 235.71 * self.beta ** 2 - 281.43 * self.beta + 147.46
        elif self.beta < 2.5:
            return 11.384 * self.beta ** 2 - 46.116 * self.beta + 86.196
        elif self.beta <= 3.2:
            return 5.9774 * self.beta ** 2 - 35.887 * self.beta + 93.375
        else:
            return 39.5

    @Attribute
    def k_compr_ssss(self):
        """This attribute represents the buckling load factor k as a function of k* and gamma.
        This buckling load factor k is valid for fully simply supported cases.

        :rtype: float
        """
        return self.k_compr_ssss_star + 19.74 * (self.gamma - 1)

    @Attribute
    def k_compr_sscc_star(self):
        """This attribute represents the buckling load factor k* as a function of beta. It has
        been determined by a curve fit of a graph from TH3.372. This buckling load factor k* is
        valid for cases where two sides are simply supported and two sides are clamped.

        :rtype: float
        """
        if self.beta < 0.4:
            return -600 * self.beta + 335
        elif self.beta < 0.925:
            return -295.41 * self.beta ** 3 + 859.18 * self.beta ** 2 - 757.65 * self.beta + 279.5
        elif self.beta < 1.61:
            return 62.519 * self.beta ** 2 - 168.71 * self.beta + 182.56
        elif self.beta < 2.28:
            return 32.019 * self.beta ** 2 - 126.05 * self.beta + 192.94
        elif self.beta < 2.95:
            return 19.15 * self.beta ** 2 - 103.14 * self.beta + 207.61
        else:
            return 68.9

    @Attribute
    def k_compr_sscc(self):
        """This attribute represents the buckling load factor k as a function of k* and gamma.
        This buckling load factor k is valid for cases where two sides are
        simply supported and two sides are clamped.

        :rtype: float
        """
        return self.k_compr_sscc_star + 23.54 * (self.gamma - 1)

    @Attribute
    def k_compr(self):
        """This attribute represents the final buckling load factor k based on the
        clamping_factor input. It is set up in such a way that it interpolates between the
        k factor for fully simply supported sides and the k factor for cases where two sides are
        simply supported and two sides are clamped.

        :rtype: float
        """
        if self.clamping_factor <= 0:
            # no need to calculate the clamped buckling factor
            return self.k_compr_ssss
        elif self.clamping_factor < 1:
            # compose final buckling factor based on simply supported and clamped k factor
            return self.clamping_factor * self.k_compr_sscc + \
                   (1 - self.clamping_factor) * self.k_compr_ssss
        else:
            # only the partially clamped k factor needs to be calculated
            return self.k_compr_sscc

    @Attribute
    def critical_compr_running_load(self):
        """This attribute represents the allowable compression load in N/mm

        :rtype: float
        """
        return -1. * self.k_compr * ((self.D_11 * self.D_22) ** 0.5) / (self.panel_width ** 2.)

    # -------------------------------------------------------------------------------------------------
    # -------------------------------SHEAR-BUCKLING----------------------------------------------------
    # -------------------------------------------------------------------------------------------------

    @Attribute
    def beta_shear(self):
        """This attribute represents a constant that is a value for the difference in length and
        material properties in two perpendicular directions. The length must be the longest side
        of the panel. Length and width and also D_11 and D_22 must be swapped if this is not the
        case. This is why the beta for shear is different than for compression.

        :rtype: float
        """
        if self.panel_length > self.panel_width:
            # use the same beta
            return (self.panel_width / self.panel_length) * ((self.D_11 / self.D_22) ** 0.25)
        else:
            # length and width and D's must be swapped
            return self.beta

    @Attribute
    def k_shear(self):
        """This attribute represents the shear buckling load factor k based on beta shear and
        gamma. It has been determined by a curve fit of a graph from Th3.372.

        :rtype: float
        """
        bs = self.beta_shear
        gmm = self.gamma
        return (((((
                   -1.1723 * gmm ** 5 + 9.8887 * gmm ** 4 - 32.513 * gmm ** 3 + 52.246 * gmm ** 2 - 41.835 * gmm + 29.331) -
                   (
                   1.318 * gmm ** 4 - 8.9 * gmm ** 3 + 22.077 * gmm ** 2 - 24.634 * gmm + 23.24)) -
                  0.5 * ((
                         2.0452 * gmm ** 4 - 13.796 * gmm ** 3 + 33.903 * gmm ** 2 - 34.685 * gmm + 35.472) -
                         (
                         1.318 * gmm ** 4 - 8.9 * gmm ** 3 + 22.077 * gmm ** 2 - 24.634 * gmm + 23.24))) * -4)) * bs ** 2 + \
               (((0.25 * ((
                          2.0452 * gmm ** 4 - 13.796 * gmm ** 3 + 33.903 * gmm ** 2 - 34.685 * gmm + 35.472) -
                          (
                          1.318 * gmm ** 4 - 8.9 * gmm ** 3 + 22.077 * gmm ** 2 - 24.634 * gmm + 23.24)) -
                  ((
                   -1.1723 * gmm ** 5 + 9.8887 * gmm ** 4 - 32.513 * gmm ** 3 + 52.246 * gmm ** 2 - 41.835 * gmm + 29.331) -
                   (
                   1.318 * gmm ** 4 - 8.9 * gmm ** 3 + 22.077 * gmm ** 2 - 24.634 * gmm + 23.24))) * -4)) * bs + \
               (1.318 * gmm ** 4 - 8.9 * gmm ** 3 + 22.077 * gmm ** 2 - 24.634 * gmm + 23.24)

    @Attribute
    def critical_shear_running_load(self):
        """This attribute represents the allowable shear load in N/mm. The value is valid for
        simply supported on all edges.

        :rtype: float
        """
        if self.panel_length > self.panel_width:
            return 4 * self.k_shear * (self.gamma ** 0.5) * \
                   (self.D_11 * (self.D_22 ** 3)) ** 0.25 / (self.panel_width ** 2)
        else:
            return 4 * self.k_shear * (self.gamma ** 0.5) * \
                   (self.D_22 * (self.D_11 ** 3)) ** 0.25 / (self.panel_length ** 2)

        # -----------------------------------------------------------------------------------------
        # ----------------------------------RESERVE FACTORS----------------------------------------
        # -----------------------------------------------------------------------------------------

    @Attribute
    def rf_compression(self):
        """This attribute represents the reserve factor for buckling due to compression load only.

        :rtype: float
        """
        if self.compression_running_load <= 0:
            return self.critical_compr_running_load / self.compression_running_load
        else:
            return 100.

    @Attribute
    def rf_shear(self):
        """This attribute represents the reserve factor for buckling due to shear load only.

        :return: float
        """
        if self.shear_running_load != 0:
            return self.critical_shear_running_load / self.shear_running_load
        else:
            return 100.

    @Attribute
    def rf_combined(self):
        """This attribute represents the reserve factor for buckling due to a combination of
        compression load and shear load.

        :rtype: float
        """
        return 1 / ((1 / self.rf_compression) + (1 / self.rf_shear) ** 2)


if __name__ == '__main__':
    obj = AnalyticPanelBucklingAnalysis(panel_length=500.,
                                        panel_width=227.5,
                                        D_11=3069022,
                                        D_22=3069022,
                                        D_33=1051600.3,
                                        D_12=965821.3,
                                        clamping_factor=0.66667,
                                        compression_running_load=-410.,
                                        shear_running_load=300.)
    print obj.rf_combined
