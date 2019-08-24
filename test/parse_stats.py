import pstats

p = pstats.Stats('test.log')

p.sort_stats('time').print_stats(20)