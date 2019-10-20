# The Earth As a Rolled-up Paper

As Dr. Mann explained in the edX course, the solar radiation impinging on earth delivers a certain amount of power per unit area:  the [solar constant](https://en.wikipedia.org/wiki/Solar_constant), $S$.  The earth's cross sectional area $A_{cs}$ as seen by the incident radiation "wavefront" is roughly $A_{cs} = \pi {r_{e}}^{2}$, where ${r_{e}}$ is the earth's average radius, so the amount of solar power delivered to earth is proportional to $SA_{cs}$.

Despite the tilt of the earth's rotational axis relative to its orbital plane, over the course of a year the incident radiation is distributed pretty evenly over its entire surface.  If the earth were a perfect sphere, that area would be $A_{s} = 4 \pi {r_{e}}^{2}$.

So, the effective solar constant (that is, the average amount of power delivered to earth's surface) is

$S_{e} = \frac{S A_{cs}}{A_{s}} = \frac {1}{4}S$.

The Matlab code doesn't use this analytical solution.  Instead, it takes a numerical methods approach, dividing the earth's surface into longitudinal strips $1\degree$ in width, calculating the fractional cross-sectional area of each strip as seen by the incident wavefront at any given hour of the day, and calculating the average of the incident power over all of the strips.

I wonder why the code considers only the longitude of the patch, and not its latitude.  It's as though the author got partway to a numerical solution and then moved on to other tasks.

In effect the code treats the earth as a cylinder with no end caps: a rolled-up sheet of paper.  As seen by the sun such an earth – assuming no axial tilt, etc. – has cross-section $A_{cs} = 2 {r_{e}} h$ and surface area $A_{s} = 2 \pi {r_{e}} h$.  

The upshot is that the Matlab code produces a value for the effective solar constant of $S_{e} = {S}/{\pi}$.

Similarly, when computing the fraction of the sphere's surface area covered by each latitude band, the code considers only the fraction of the total "height" (extent along the rotational axis) covered by each band.  No consideration is given to the approximate radius of each band.

What's more, in this implementation the vertical extent of each band is independent of the latitude.  A more faithful implementation would reflect the fact that latitude bands near the poles have less vertical extent (again, as seen by the sun) than those near the equator.  I.e., for latitude $l$ with latitude band "width" $dl$,

${h} = {|sin(l + dl) - sin(l)|}$

# earth_as_rolled_paper.js

When porting software from one environment/language to another, it's normal to duplicate the behavior of the original, bugs and all.  So it's no surprise that the [JavaScript implementation](http://www.climate.be/textbook/EBM.js) contains exactly the same strange logic.

I would love to know more about the origins of the Matlab implementation.  It could be that all of this was intentional.  As far as I can tell, these details do not affect the essential characteristics of the model.
