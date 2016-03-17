#!/bin/sh

# Copy the mockup package definition verbatim, needed for dependency
# even though this is not even going to be an npm package.
/bin/cp src/mockup/package.json .

# Copy the mockup bower configuration
/bin/cp src/mockup/bower.json .

# Make our bootstrap with that.
make bootstrap
