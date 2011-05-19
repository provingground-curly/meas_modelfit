#!/usr/bin/env python

# 
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
# 
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the LSST License Statement and 
# the GNU General Public License along with this program.  If not, 
# see <http://www.lsstcorp.org/LegalNotices/>.
#
import lsst.afw.image as afwImage
import lsst.afw.math as afwMath
import lsst.afw.geom as afwGeom
import lsst.afw.detection as afwDetection
import lsst.meas.algorithms as measAlgorithms
import lsst.meas.multifit as mf
import lsst.pex.policy as policy
import lsst.utils.tests as utilTests
import unittest
import eups
import sys
import math
import numpy

class GaussianPsfTestCase(unittest.TestCase):
    """A test case detecting and measuring Gaussian PSFs"""
    def setUp(self):
        FWHM = 5
        psf = afwDetection.createPsf("SingleGaussian", 15, 15, FWHM/(2*math.sqrt(2*math.log(2))))
        mi = afwImage.MaskedImageF(afwGeom.ExtentI(100, 100))

        self.xc, self.yc, self.flux = 45, 55, 1000.0
        mi.getImage().set(self.xc, self.yc, self.flux)
        mi.getVariance().set(1e-6)

        cnvImage = mi.Factory(mi.getDimensions())
        afwMath.convolve(cnvImage, mi, psf.getKernel(), afwMath.ConvolutionControl())
        self.exp = afwImage.makeExposure(cnvImage)
        self.exp.setPsf(psf)

        axes = afwGeom.ellipses.Axes(1, 1, 0)
        quad = afwGeom.ellipses.Quadrupole(axes)
        point = afwGeom.Point2D(self.xc, self.yc)
        ellipse = afwGeom.ellipses.Ellipse(axes, point)        
        print >>sys.stderr, ellipse
        self.source = afwDetection.Source()
        self.source.setXAstrom(self.xc)
        self.source.setYAstrom(self.yc)
        self.source.setIxx(quad.getIXX())
        self.source.setIyy(quad.getIYY())
        self.source.setIxy(quad.getIXY())
        self.source.setFootprint(afwDetection.Footprint(ellipse))

    def tearDown(self):
        del self.exp
        del self.source

    def testPsfFlux(self):
        """Test that fluxes are measured correctly"""
        #
        # Total flux in image
        #
        flux = afwMath.makeStatistics(self.exp.getMaskedImage(), afwMath.SUM).getValue()

        #
        # Various algorithms
        #
        photoAlgorithms = ["SHAPELET_MODEL_2"]
        mp = measAlgorithms.makeMeasurePhotometry(self.exp)
        for a in photoAlgorithms:
            mp.addAlgorithm(a)

        rad = 10.0
        pol = policy.Policy(policy.PolicyString(
            """#<?cfg paf policy?>
            SHAPELET_MODEL_2: {
                enabled: true
                #nGrowFp: 2
                #psfShapeletOrder: 2
                #maxIter: 200
                #isPositionActive: false
                #isRadiusActive: false
                #isEllipticityActive: false
                #retryWithSvd: true
                #ftol: 1e-8
                #gtol: 1e-8
                #minStep: 1e-8
                #tau: 1e-6
                #maskPlaneName: "BAD" "SAT" "CR"
            }
            """ 
            ))
        mp.configure(pol)        

        meas = mp.measure(afwDetection.Peak(self.xc, self.yc), self.source)
        for a in photoAlgorithms:
            photom = meas.find(a)
            print >> sys.stderr, "flux:", photom.get(afwDetection.Schema("FLUX", 0, afwDetection.Schema.DOUBLE))
            print >> sys.stderr, "fluxErr:",photom.get(afwDetection.Schema("FLUX_ERR", 1, afwDetection.Schema.DOUBLE))
            print >> sys.stderr, "status:",photom.get(afwDetection.Schema("STATUS", 2, afwDetection.Schema.INT))
            print >> sys.stderr, "e1:",photom.get(afwDetection.Schema("E1", 3, afwDetection.Schema.DOUBLE))
            print >> sys.stderr, "e2:", photom.get(afwDetection.Schema("E2", 4, afwDetection.Schema.DOUBLE))
            print >> sys.stderr, "radius",photom.get(afwDetection.Schema("RADIUS", 5, afwDetection.Schema.DOUBLE))
            for i in range(2):
                print >> sys.stderr, "coeff %i: %g"%(i, photom.get(i, afwDetection.Schema("COEFFICIENTS", 6, afwDetection.Schema.DOUBLE)))

            
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def suite():
    """Returns a suite containing all the test cases in this module."""
    utilTests.init()

    suites = []
    suites += unittest.makeSuite(GaussianPsfTestCase)
    suites += unittest.makeSuite(utilTests.MemoryTestCase)
    return unittest.TestSuite(suites)

def run(exit = False):
    """Run the tests"""
    utilTests.run(suite(), exit)

if __name__ == "__main__":
    run(True)