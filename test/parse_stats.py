import pstats

p = pstats.Stats('test2.log')

p.sort_stats('time').print_stats(20)