#!/bin/bash
git submodule foreach --recursive "git pull || true"
