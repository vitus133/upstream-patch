#!/bin/bash

tag=($1)

bundle_hash=$(podman pull --quiet quay.io/openshift-kni/cluster-group-upgrades-operator-bundle:${tag})
echo $bundle_hash
path=$(podman image mount ${bundle_hash})
echo $path
rm -rf artifacts/bundle/*
cp -rf $path/manifests $path/metadata $path/tests artifacts/bundle/
podman image unmount ${bundle_hash}

