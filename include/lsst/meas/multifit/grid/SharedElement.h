// -*- LSST-C++ -*-
/* 
 * LSST Data Management System
 * Copyright 2008, 2009, 2010, 2011 LSST Corporation.
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

#ifndef LSST_MEAS_MULTIFIT_GRID_SharedElement
#define LSST_MEAS_MULTIFIT_GRID_SharedElement

#include "lsst/meas/multifit/definition/SharedElement.h"

#include <boost/iterator/indirect_iterator.hpp>
#include <vector>
#include <set>
#include "Eigen/Core"

namespace lsst { namespace meas { namespace multifit { namespace grid {

template <SharedElementType E>
class SharedElement : public detail::SharedElementBase<E>, private boost::noncopyable {
public:
    
    // No ConstPtr typedef to make it clear that this class is strictly immutable.
    typedef boost::shared_ptr< SharedElement<E> > Ptr;
    typedef typename detail::SharedElementTraits<E>::Value Value;

    int const offset;

#ifndef SWIG
    /// Return true if the parameters are in-bounds.
    bool checkBounds(double const * parameters) const {
        return this->getBounds().checkBounds(parameters + offset);
    }

    /**
     *  If the parameters are out of bounds, move them to the boundary and return
     *  a positive value that increases as the necessary parameter change increases.
     *  Return 0.0 if the parameters are already in-bounds
     */
    double clipToBounds(double * parameters) const {
        return this->getBounds().clipToBounds(parameters + offset);
    }
#endif

private:

    friend class Initializer;

    SharedElement(definition::SharedElement<E> const & definition, int offset_) : 
        detail::SharedElementBase<E>(definition), offset(offset_) {}

};


typedef SharedElement<POSITION> PositionElement;
typedef SharedElement<RADIUS> RadiusElement;
typedef SharedElement<ELLIPTICITY> EllipticityElement;

#ifndef SWIG

template <SharedElementType E>
std::ostream & operator<<(std::ostream & os, SharedElement<E> const & component);

#endif

}}}} // namespace lsst::meas::multifit::grid

#endif // !LSST_MEAS_MULTIFIT_GRID_SharedElement
