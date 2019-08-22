import pstats

p = pstats.Stats('test.log')

p.sort_stats('cumulative').print_stats(20)