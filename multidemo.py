
import urllib2 
from multiprocessing.dummy import Pool as ThreadPool 
import time
urls = [
	'http://www.baidu.com',
    'http://www.baidu.com',
    'http://www.baidu.com',
    'http://www.baidu.com',
    'http://www.baidu.com',
    'http://www.baidu.com',
    'http://www.baidu.com',
    'http://www.baidu.com',
    'http://www.baidu.com',
    'http://www.ustb.edu.cn',
    'http://www.ustb.edu.cn',
    'http://www.ustb.edu.cn',
    'http://www.ustb.edu.cn',
    'http://www.ustb.edu.cn',
    'http://www.ustb.edu.cn',
    'http://www.ustb.edu.cn',
    'http://www.ustb.edu.cn',
    'http://www.ustb.edu.cn',
    'http://www.ustb.edu.cn',
    'http://www.ustb.edu.cn',
    'http://www.ustb.edu.cn',
    'http://www.baidu.com',
    'http://www.baidu.com',
    'http://www.baidu.com',
    'http://www.baidu.com'

	]

# Make the Pool of workers
start = time.time()
pool = ThreadPool(4) 
# Open the urls in their own threads
# and return the results
results = pool.map(urllib2.urlopen, urls)
#close the pool and wait for the work to finish 
pool.close() 
pool.join() 
end = time.time()
print end - start

start = time.time()
pool = ThreadPool(8) 
# Open the urls in their own threads
# and return the results
results = pool.map(urllib2.urlopen, urls)
#close the pool and wait for the work to finish 
pool.close() 
pool.join() 
end = time.time()
print end - start

start = time.time()
pool = ThreadPool(12) 
# Open the urls in their own threads
# and return the results
results = pool.map(urllib2.urlopen, urls)
#close the pool and wait for the work to finish 
pool.close() 
pool.join() 
end = time.time()
print end - start
# results = [] 
# for url in urls:
# 	result = urllib2.urlopen(url)
# 	results.append(result)

# # ------- VERSUS ------- # 


# # ------- 4 Pool ------- # 
# pool = ThreadPool(4) 
# results = pool.map(urllib2.urlopen, urls)

# # ------- 8 Pool ------- # 

# pool = ThreadPool(8) 
# results = pool.map(urllib2.urlopen, urls)

# # ------- 13 Pool ------- # 

# pool = ThreadPool(13) 
# results = pool.map(urllib2.urlopen, urls)


# 						Single thread:  14.4 Seconds 
# 						       4 Pool:   3.1 Seconds
# 						       8 Pool:   1.4 Seconds
# 						      13 Pool:   1.3 Seconds



