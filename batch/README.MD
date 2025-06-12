# Introduction
This document describes how to setup geodms regression testing on a new machine.

# Full regression test
The entrypoint for running the full regression test for geodms is the python script full.py. The entryfunction has the following signature:

```shell
python full.py -version 17.4.6 -MT1 S1 -MT2 S2 -MT3 S3
```

The full regression tests has a series of environment variables that will be used mostly by geodms to resolve paths for projects. The following is a list of paths:
