#!/usr/bin/env bash

DIR=$(cd $(dirname $0); pwd)

SOURCEDIR=${DIR}/trajectory
TARGETDIR=${DIR}/../HMM

for TEMPERATURE in 27 30 32 37
do
  ${DIR}/trackmate -vv --mat ${TARGETDIR}/mito${TEMPERATURE}/trajectory.mat ${SOURCEDIR} '^.*Div7MitoMove'${TEMPERATURE}'C.*\.xml$'
done
