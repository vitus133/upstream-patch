#!/bin/bash

tag=($1)
podman unshare ./extract_bundle.sh $tag
exit
