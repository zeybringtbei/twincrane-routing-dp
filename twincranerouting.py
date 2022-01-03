requests = []

# ------------------------------------------------------------------
# ZUSTAND
# Speichert die Bay der Kräne.
# Der Kran mit Priorität (priocrane) steht in der Bay seines letzten erfüllten Requests
# Der Kran ohne Priorität (1-priocrane) steht direkt links oder rechts neben dem anderen Kran
# --------------------------------------------------------------------
class State:
    """
        DP-State. 

        Stores the prioritized crane in this state
        
        Stores the crane's bays: 
        - PrioCrane is positioned in the bay of its last fulfilled request
        - The other crane is positioned left or right of the PrioCrane

        Stores the current makespan

        Stores the pair of conflicting requests:
        - PrioCrane has fulfilled the request
        - The other crane has to fulfill its request next


    """

    def __init__(self, iBay, iPriocrane, iMakespan, inextReq):

        # definiert die Bays in denen die Kräne positioniert sind
        self.bay = iBay[:]
        self.makespan = iMakespan       # aktueller Makespan im State
        self.priocrane = iPriocrane     # Kran der priorisiert wurde
        self.confRequest = inextReq[:]
        self.prevStateIndex = None


class Crane:
    """Crane class. Stores the current bay of a crane, its number, if it is working (i.e. lifting or releasing a container),
        its next request and, if it is working, the duration that remains until it is finished working.
    """

    def __init__(self, iBay, iNr):
        self.bay = iBay
        self.nr = iNr
        self.working = False
        self.nextReq = 0
        self.remDur = 0

    def evade(self):
        """If the crane is crane 0, it is placed in a smaller bay than crane 1, hence evading implies moving to a smaller bay.
            If the crane is crane 1, evading implies moving to a larger bay.
        """
        if self.nr == 0:
            self.bay -= 1
        else:
            self.bay += 1

    def endReq(self):
        self.nextReq += 1
        self.working = False
        self.remDur = 0

    def startReq(self, iremDur):
        self.working = True
        self.remDur = iremDur

    def workSomePeriods(self, workdur):
        self.remDur -= workdur

# Bestimmt die Interferenzfreien Endzeiten des nächsten Requests


def _endTimesNextReq(c, makespan):
    """Determines the (possible) end times of the next two requests of both cranes, assuming the cranes do not interfere

    Args:
        c (Crane class): The crane class
        makespan (int): The current makespan

    Returns:
        List{int}: The end times of the next 2 requests
    """
    endTimes = []
    for i in range(2):
        ending = makespan + (c[i].remDur if c[i].working == True else abs(c[i].bay-requests[i][c[i].nextReq][0])+requests[i][c[i].nextReq][1])
        endTimes.append(ending)
    return endTimes

# Lässt beide Kräne die restlichen Requests beenden


def _letCranesFinish(c, time) -> State:
    """Assumes that one crane has finished all its requests and hence can always evade from the other crane in case of interference. 
    Then determines the (conflict free) ending times of the remaining requests of the other crane.

    Args:
        c (List<Crane>): A pair of cranes
        time (int): current Makespan

    Returns:
        State: the final State of the DP
    """
    finalfinish = [time, time]
    for i in range(2):
        while c[i].nextReq < len(requests[i]):
            finalfinish[i] += c[i].remDur if c[i].working else abs(
                c[i].bay-requests[i][c[i].nextReq][0])+requests[i][c[i].nextReq][1]
            _letCraneProceedNextReq(c[i])

    makespan = max(finalfinish[0], finalfinish[1])
    final_state = State([requests[0][c[0].nextReq-1][0], requests[1]
                         [c[1].nextReq-1][0]], 0, makespan, [c[0].nextReq, c[1].nextReq])
    return final_state

# Lässt den Kran für x Perioden fortfahren


def _letCraneProceedPeriods(c, duration):
    timeToStart = min(abs(requests[c.nr][c.nextReq][0]-c.bay), duration)

    if c.bay < requests[c.nr][c.nextReq][0]:
        c.bay += timeToStart
    elif c.bay > requests[c.nr][c.nextReq][0]:
        c.bay -= timeToStart

    if duration > timeToStart:
        c.remDur = requests[c.nr][c.nextReq][1] - (duration-timeToStart)
        if c.remDur > 0:
            c.working = True
        else:
            c.endReq()


def _letCraneProceedNextReq(c):
    c.bay = requests[c.nr][c.nextReq][0]
    c.endReq()


def _hasFinished(c):
    return c[0].nextReq >= len(requests[0]) or c[1].nextReq >= len(requests[1])

# Prüft ob Interferenz auftritt


def interference(c, finTimeFirst, time, firstcrane) -> bool:
    """Checks if the next requests of the cranes cause interference, i.e. implies that cranes have to cross position at the same time

    Args:
        c (Crane): Crane class
        finTimeFirst (int): Finish time of the request that finishes earlier
        time (int): current makespan
        firstcrane (int): Number of the crane that could finish first (if there was no interference)

    Returns:
        bool: True if there is interference, False else
    """
    if requests[0][c[0].nextReq][0] >= requests[1][c[1].nextReq][0]:
        return _interfereAtSameTime(c, finTimeFirst, time, firstcrane)
    return False

def _interfereAtSameTime(c, finTimeFirst, time, firstcrane: int) -> bool:
    """Assuming that a pair of requests implies that the cranes cross positions: Checks if the cranes have to cross positions at the same time

    Args:
        c (Crane): a pair of cranes
        finTimeFirst (int): Time when the first request can be finished
        time (int): Current makespan
        firstcrane (int): Number of the crane that finishes first

    Returns:
        bool: True if they interfere at the same time
    """
    pseuc = Crane(c[1-firstcrane].bay, c[1-firstcrane].nr)
    pseuc.nextReq = c[1-firstcrane].nextReq
    pseuc.remDur = c[1-firstcrane].remDur
    pseuc.working = c[1-firstcrane].working

    _letCraneProceedPeriods(pseuc, finTimeFirst-time)

    if firstcrane == 0:
        return requests[0][c[0].nextReq][0] >= pseuc.bay
    else:
        return requests[1][c[1].nextReq][0] <= pseuc.bay


def _transitions(currstate: State):
    """
    Determines the possible transitions from a state (and in doing so its pair of possible succeeding states or the final state) 
    Lets the cranes proceed until they:
    - either have finished all of their requests (and reach the final state) 
    - or until they interfere. 
    
    In the latter case a pair of states is returned, giving priority to either crane in order to resolve
    the interference.

    Args:
        currstate (State): The State from which the cranes shall proceed

    Returns:
        List<State>: A list of possible succeeding states
    """
    c = _deriveCranes(currstate)
    transitions = []
    time = currstate.makespan

    while len(transitions) == 0:
        endTimes = _endTimesNextReq(c, time)
        firstToEnd = 0 if endTimes[0] < endTimes[1] else 1

        if interference(c, endTimes[firstToEnd], time, firstToEnd):
            for i in range(2):
                bayprio = [0, 0]
                bayprio[i] = requests[i][c[i].nextReq][0]
                bayprio[1-i] = bayprio[i]+1 if i == 0 else bayprio[i]-1
                prioState = State(bayprio, i, endTimes[i], [c[0].nextReq, c[1].nextReq])

                pseuc = _deriveCranes(prioState)
                if _hasFinished(pseuc):
                    finstate = _letCranesFinish(pseuc, prioState.makespan)
                    transitions.append(finstate)
                else:
                    transitions.append(prioState)

        else:
            _letCraneProceedPeriods(c[1-firstToEnd], endTimes[firstToEnd]-time)
            _letCraneProceedNextReq(c[firstToEnd])
            time = endTimes[firstToEnd]
            if _hasFinished(c):
                finstate = _letCranesFinish(c, time)
                transitions.append(finstate)

    return transitions


def _deriveCranes(currstate: State):
    """
    Derives a pair of crane(classes) from the given state

    Args:
        currstate (State): [State from the DP]

    Returns:
        [list[Crane]]: [The pair of cranes]
    """
    cranes = []
    for i in range(2):
        c = Crane(currstate.bay[i], i)
        c.nextReq = currstate.confRequest[i] # crane's progress
        if currstate.priocrane == i:
            c.nextReq += 1
        cranes.append(c)
    return cranes

# Binary Search Implementierung


def _binSearch(states, st: State):
    """Binary Search implementation for a list of DP-States

    Args:
        states (List<State>): List of DP-States
        st (State): A state which shall be added to the list of states

    Returns:
        int: Index of st in the list of States, <0 if st is not in the List (abs(int)-1 is the insertion index), >=0, implying the index if st is already in the list
    """
    low = 0
    high = len(states)-1
    while low <= high:
        mid = int((low+high)/2)
        compval = _compare(st, states[mid])
        if compval == -1:
            low = mid+1
        if compval == 1:
            high = mid - 1
        if compval == 0:
            return mid

    return -(low+1)
# Comparator für Binary Search


def _compare(stone: State, sttwo: State):
    """Comparator of two DP-States. 
    1) Compares the request-nr of crane 0
    2) If 1) are equal: Compares the request-nr of crane 1
    3) If 2) are equal: Compares the prioritized crane-nr

    Args:
        stone (State): State 1
        sttwo (State): State 2

    Returns:
        int: 0 if State 1 and 2 are equal, -1 of State 1 is ranked higher, 1 if State 1 is ranked lower
    """
    if stone.confRequest[0] > sttwo.confRequest[0]:
        return -1
    if stone.confRequest[0] < sttwo.confRequest[0]:
        return 1
    if stone.confRequest[1] > sttwo.confRequest[1]:
        return -1
    if stone.confRequest[1] < sttwo.confRequest[1]:
        return 1
    if stone.priocrane > sttwo.priocrane:
        return -1
    if stone.priocrane < sttwo.priocrane:
        return 1
    return 0


def _addOrRefresh(st: State, states: "list[State]"):
    """
    
    Adds a state to the list of states if the list does not contain the state.
    Or refreshes the state in the list, if its implied makespan can be updated.

    Args:
        st (State): State to be added
        states (List<State>): List of DP-States
    """
    pos = _binSearch(states, st)
    if pos < 0:
        states.insert(abs(pos)-1, st)
    else:
        if states[pos].makespan > st.makespan:
            states[pos].makespan = st.makespan

class Priorities:
    
    def __init__(self) -> None:
        # Dict that stores each pair of requests
        self.reqsWithPrioDecision = {}

    def getPrioritizedCrane(self, reqNrFirstCrane: int, reqNrSecondCrane: int):
        if self.priorityDecisionExists(reqNrFirstCrane,reqNrSecondCrane):
            return self.reqsWithPrioDecision[(reqNrFirstCrane,reqNrSecondCrane)]
        return None

    def priorityDecisionExists(self, reqNrFirstCrane: int, reqNrSecondCrane: int):
        # Check if there exists an entry in our table of decisions. Return "true" if so
        return (reqNrFirstCrane,reqNrSecondCrane) in self.reqsWithPrioDecision
    
    def putDecision(self, reqNrFirstCrane: int, reqNrSecondCrane: int, prioritizedCrane: int):
        # Adds a new priority decision to the dict (we use tuples, since they are hashable)
        self.reqsWithPrioDecision[(reqNrFirstCrane,reqNrSecondCrane)] = prioritizedCrane

def _stagePrioritySequence(states: "list[State]", s: State):
    """
        Recursively determines crane-priorities for conflicting requests based on a given state.

    Args:
        s (State): A given state of the optimal routing

    Returns:
        Priorities: Dictionary of priorites
    """

    # Add the states to the dict
    prios = Priorities()
    incState = states[s.prevStateIndex] 
    while incState.prevStateIndex is not None:
        prios.putDecision(incState.confRequest[0], incState.confRequest[1], incState.priocrane)
        incState = states[incState.prevStateIndex]

    return prios
    


# ------------------------------------------------------------------
#
# (C) 2019 Lennart Zey
# Determiniert den minimalen Makespan in O(n³) für ein Paar von Twin Kränen
#
# Benötigt Requests des 1. Krans. 1 Request = 2 Dim Array mit [Position, Dauer]
# Benötigt Requests des 2. Krans. 1 Request = 2 Dim Array mit [Position, Dauer]
# Benötigt Startpositionen [startpos1,startpos2]
#
# --------------------------------------------------------------------

def getMinimumMakespanSchedule(requestsCrane1, requestsCrane2, startpos):
    """ Determines a minimum makespan schedule for a pair of Twin-Cranes in O(n³)


    Args:
        requestsCrane1 (list[list[Position, Duration]]): 
        * List of requests for crane 1. 
        * Each request hast a position and a duration
        
        requestsCrane2 (list[list[Position, Duration]]): 
        * List of requests for crane 1. 
        * Each request hast a position and a duration

        startpos (list[pos1,po2]): 
        * Initial positions of the cranes

    Returns:
        [Priorities, makespan]: Priority class and makespan of the optimum schedule. 
        
        * Check whether a pair of request indices has a predetermined priority by calling "priorityDecionExists(reqIndexCrane1, reqIndexCrane2)" on the Priorities Class.
        * Get the crane that comes first of a conflicting request pair by calling "getPrioritizedCrane(reqIndexCrane1, reqIndexCrane2)". Returns a crane index if the pair exists. Returns "None" else.
    """
    global requests
    requests = [requestsCrane1, requestsCrane2]

    states = [State(startpos, 0, 0, [-1, 0])]

    finished = False
    nextstate = 0
    while not finished:

        nextransitions = _transitions(states[nextstate])

        for s in nextransitions:
            # Version 2.0 Add the previous state to the states in order to derive a sequence of priorities
            s.prevStateIndex = nextstate
            # Add the new states to the set of states
            _addOrRefresh(s, states)

        nextstate += 1

        finished = (states[nextstate].confRequest[0] >= len(requests[0]) and states[nextstate].confRequest[1] >= len(requests[1]))

    return _stagePrioritySequence(states, states[-1]), states[-1].makespan
