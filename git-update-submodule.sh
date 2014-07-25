#!/bin/bash
# This should only be used on the deployment server, as it resets the tracking branches of the submodules.
git submodule update --init --recursive
