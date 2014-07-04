#!/usr/bin/env python
import sys
import pstats
s = pstats.Stats(sys.argv[1])
s.sort_stats(sys.argv[2])
s.print_stats()
