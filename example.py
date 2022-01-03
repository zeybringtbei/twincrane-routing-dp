import twincranerouting as twc

# The cranes start in bay 0 (crane 1) and 31 (crane 2)
startbays = [0, 31]

# Crane 1 has three container transports. 
# - a pickup in bay 26 (duration: 3), a transport to bay 10
# - a pickup in bay 19 and transport to bay 28 (durations 4 and 3)
# - a pickup in bay 17 and transport to 20 (durations 5 and 1)
req1 = [[26, 3], [10, 3], [19, 4], [28, 3], [17, 5], [20, 1]] 

# Crane 2 has two container transports:
# - a pickup in bay 19 and transport to bay 13
# - a pickup in bay 22 and transport to bay 14
req2 = [[19, 4], [13, 6], [22, 5], [14, 2]]

# Run the algorithm. 
# - Retrieve all request pairs, where there is an active decision regarding priorites 
# - and the corresponding makespan 
priorities, makespan = twc.getMinimumMakespanSchedule(req1, req2, startbays)
print(makespan)
