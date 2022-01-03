# twincrane-routing-dp
Modified DP Algorithm from 

<em> 
  Lennart Zey, Dirk Briskorn, Nils Boysen: Twin-crane scheduling during seaside workload peaks with a dedicated handshake area, Journal of Scheduling (https://link.springer.com/article/10.1007/s10951-021-00710-w) 
</em>

### Algorithm
The algorithm allows to determine a minimum makespan routing for a pair of rail-mounted-gantry cranes in O(n³). 


### Modification as opposed to the original article
In this implementation
 - we ignore trolley-travel (which, however, can be implemented easily). 
 - we account for any-bay-interference and do not restrict ourselves to requests in the handshake-bay

### Tutorial (see example.py)
1. Transform a sequence of container transports to a sequence of pick-up and drop-off requests
2. Pass this sequence (and a pair of starting bays) to the algorithm

