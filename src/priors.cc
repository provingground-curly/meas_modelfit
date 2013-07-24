// -*- lsst-c++ -*-
/*
 * LSST Data Management System
 * Copyright 2008-2013 LSST Corporation.
 *
 * This product includes software developed by the
 * LSST Project (http://www.lsst.org/).
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the LSST License Statement and
 * the GNU General Public License along with this program.  If not,
 * see <http://www.lsstcorp.org/LegalNotices/>.
 */

#include "Eigen/LU"

#include "lsst/pex/exceptions.h"
#include "lsst/meas/multifit/priors.h"
#include "lsst/meas/multifit/integrals.h"

namespace lsst { namespace meas { namespace multifit {

PTR(FlatPrior) FlatPrior::get() {
    static PTR(FlatPrior) instance(new FlatPrior());
    return instance;
}

samples::Scalar FlatPrior::apply(LogGaussian const & likelihood, samples::Vector const & parameters) const {
    return integrateGaussian(likelihood.grad, likelihood.fisher);
}

samples::Scalar MixturePrior::apply(
    LogGaussian const & likelihood, samples::Vector const & parameters
) const {
    return FlatPrior::get()->apply(likelihood, parameters)
        - std::log(_mixture.evaluate(parameters.head<3>()));
}

MixturePrior::MixturePrior(Mixture<3> const & mixture) : _mixture(mixture) {}

namespace {

class EllipseUpdateRestriction : public Mixture<3>::UpdateRestriction {
public:

    virtual void restrictMu(Vector & mu) const {
        mu[0] = 0.0;
        mu[1] = 0.0;
    }

    virtual void restrictSigma(Matrix & sigma) const {
        sigma(0,0) = sigma(1,1) = 0.5*(sigma(0,0) + sigma(1,1));
        sigma(0,1) = sigma(0,1) = 0.0;
        sigma(0,2) = sigma(2,0) = sigma(1,2) = sigma(2,1) = 0.5*(sigma(0,2) + sigma(1,2));
    }

};

} // anonymous

Mixture<3>::UpdateRestriction const & MixturePrior::getUpdateRestriction() {
    static EllipseUpdateRestriction const instance;
    return instance;
}

}}} // namespace lsst::meas::multifit
