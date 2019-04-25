import sys
import Queue

class NFA:

    def __init__(self, n_states, alphabet, start_state, accept_states):
        self.start_state = start_state
        self.n_states = n_states
        self.alphabet = alphabet
        self.accept_states = accept_states
        self.trans_set = []
        self.closure_trans = []

    def get_start_state(self):
        return self.start_state
        
    def get_n_states(self):
        return self.n_states

    def get_alphabet(self):
        return self.alphabet

    def get_accept_states(self):
        return self.accept_states

    def get_trans_set(self):
        return self.trans_set

    def add_transition(self, trans):
        self.trans_set.append(trans)

    def add_closure_trans(self, transition):
        self.closure_trans.append(transition)

    def get_closure_trans(self):
        return self.closure_trans
        

class DFA:

    def __init__(self, alphabet, start_state, accept_states):
        self.states = None
        self.alphabet = alphabet
        self.start_state = start_state
        self.accept_states = []
        self.trans_set = []
	
    def set_n_states(self, num_states):
        self.states = num_states

    def get_n_states(self):
        return self.states

    def add_transition(self, trans):
        self.trans_set.append(trans)

    def get_trans_set(self):
        return self.trans_set

    def add_accept_states(self, new_accept_state):
        self.accept_states.append(new_accept_state)

    def get_accept_states(self):
        return self.accept_states

    def get_alphabet(self):
        return self.alphabet

    def get_start_state(self):
        return self.start_state

    def set_start_state(self, new_start_state):
        self.start_state = new_start_state


def closure(NFA, start_state):
    '''
    Closure method: For given start_state, follow the epsilon transitions all the way through and add the new qb states to the final_set 
        Params: NFA is the NFA machine and start_state is the beginning start state (qa state)
        Return final set which is the set where start_state can get to on epsilon transitions.
    '''
    
    final_set = []
    track = [start_state]
    # Run a DFS, if a state can be reached via epsilon, push onto stack and continue
    while track:
        state = track.pop()
        for move in NFA.get_trans_set():
            if (move[0] == state) and (move[1] == 'e') and ((move[2] not in final_set) and (move[2] != start_state)):
                track.append(move[2])
                final_set.append(move[2])
    return final_set


def init_NFA(NFA, state, alphabet):
    '''
    init_NFA: takes state and goes through the alphabet, appending qb states to final set of qb states
    if there exists a state and symbol already defined.
        Params: NFA is the NFA machine, state is the qa state, and alphabet is the set of symbols
        Returns final set which is the set a specified state on a specified symbol can get to.
    ''' 
    # Append normal trans_set for each symbol in the alphabet
    final = [state, []]
    final[1].append(('e', closure(NFA, state)))
    #for each letter in the alphabet create the places that it can get to
    for symbol in alphabet:
        results = []
        for transition in NFA.get_trans_set():
            if (transition[0] == state) and (transition[1] == symbol):
                results.append(transition[2])
        # append current set to add new qb state
        final[1].append((symbol, results))
    return final


def move(NFA, new_state, symbol):
    '''
    Move: Finds all the states the new_state can get to on the specified symbol.
        Params: NFA is the NFA machine, new_state is the start state (which can be a set of states)
        and symbol is the input symbol in the alphabet
        Returns new_set which is the set of qb states new_state can get to on symbol
    '''

    # new set is the set that state_at can get to on symbol
    new_set = []
    state_at = [new_state]
    for transition in NFA.get_trans_set():
        for state in state_at:
            if (transition[0] == state) and (transition[1] == symbol):
                new_set.append(transition[2])
    
    new_set.sort() 
    return new_set
        
        
def init_DFA(NFA, NFA_start_state):
    '''
    init_DFA: uses information from NFA machine to build a new DFA machine. Keeps track of states to be be handed in states_queue
    and assigns the "id's" of the set of states to be the state you can transition to or from.
        Params: NFA is the NFA machine, NFA_start_state is the beginning state of the DFA machine
        Returns newDFA which is the initialized new DFA machine
    '''

    new_trans = []
    new_accept = []
    # keep track of num new states and do similar thing for qa and qb stack 
    start = NFA.get_closure_trans()[NFA_start_state - 1]
    start_state = [NFA_start_state]
    for transition in start[1]:
        if transition[0] == 'e':
            start_state.extend(transition[1])
    start_state.sort()
    new_states = [start_state]
    # state_stack adds states to be handled and pops states that are handled using FIFO strategy
    # tried queue but realized that a stack would work better for what we are trying to do
    states_stack = [start_state]
    
    newDFA = DFA(NFA.get_alphabet(), NFA_start_state, None)
    
    while states_stack: # while there are still states in stack
        # for state in range(1, NFA.get_n_states()+1):
        state_to_be_handled = states_stack.pop()
        for letter in NFA.get_alphabet():
            results = []
            # go through each letter in the alphabet to see where the nfa can go 
            # save where the nfa can to a list to be set as a transtion state for the dfa
            for state in state_to_be_handled:
                closure_trans = NFA.get_closure_trans()[state-1]
                for trans in closure_trans[1]:
                    if trans[0] == letter:
                        for x in trans[1]:
                            if x not in results:
                                # append results
                                results.append(x)
                                x_closure = NFA.get_closure_trans()[x-1]
                                # check the closure of the new results
                                for y_closure in x_closure[1][0][1]:
                                    if y_closure not in results:
                                        # append results
                                        results.append(y_closure)                
                       
            # sort the results so that we can see if they are used in the dfa
            results.sort()
            dfa_trans = (state_to_be_handled, letter, results)
            new_trans.append(dfa_trans)
            # check to see if the results set is already defined as a state
            if (results not in new_states) and (results != state_to_be_handled):
                states_stack.append(results)
                new_states.append(results)
     
    # set id of dfa transitions
    for b in new_trans:
        temp = (new_states.index(b[0]) + 1, b[1], new_states.index(b[2]) + 1)
        newDFA.add_transition(temp)
    
    # define accepting states in dfa
    for a in new_states:
        for accept in NFA.get_accept_states():
            if accept in a:
                newDFA.add_accept_states(new_states.index(a) + 1)

    # set n states to length of new_states
    newDFA.set_n_states(len(new_states))
    # set the start state of dfa to correct id
    newDFA.set_start_state(new_states.index(start_state) + 1)
    
    return newDFA


def read_file(input_file):

    # read contents of file
    alphabet = []
    lines = input_file.read().splitlines()
    number_lines = int(lines[0])
    al = str(lines[1])
    for character in range(len(al)):
        alphabet.append(al[character])

    # get transitions from file
    trans_set = []
    for thing in range(2, len(lines)):
        string = lines[thing].split()
        if len(string) == 0:
            break
        start_state = int(string[0])
        end = int(string[2])
        transition = string[1][1:len(string[1]) - 1]
        trans_tuple = (start_state, transition, end)
        trans_set.append(trans_tuple)
	
    # reads the start_state and parses the set of accept states into an array
    start_state = int(lines[len(lines) - 2])
    set_of_accept = lines[len(lines) - 1].split()
    accept_states = []
    for state in set_of_accept:
        accept_states.append(int(state))

    # creates the NFA machine using the information from the file
    actual_NFA = NFA(number_lines, alphabet, start_state, accept_states)
    for trans in trans_set:
        actual_NFA.add_transition(trans)
    
    # calls closure on NFA transitions and adds them to the closure set of transitions
    for state in range(1, actual_NFA.get_n_states() + 1):
        actual_NFA.add_closure_trans(init_NFA(actual_NFA, state, alphabet))
    
    #print_nfa(actual_NFA)
    return actual_NFA
    
    
def write_file(output_file, DFA):
    
    # Print DFA to stdout
    ofp = open(output_file, 'w')
    ofp.write(str(DFA.get_n_states()))
    ofp.write("\n")
    dfa_alphabet = ""
    
    # writes the alphabet to file
    for character in DFA.get_alphabet():
        dfa_alphabet += character
    ofp.write(dfa_alphabet)
    ofp.write("\n")

    # writes the transitions to file
    for transition in DFA.get_trans_set():
        transition_append = "\'" + str(transition[1]) + "\'"
        output = str(transition[0]) + " " + transition_append + " " + str(transition[2])
        ofp.write(output)
        ofp.write("\n")
    ofp.write(str(DFA.get_start_state()))
    ofp.write("\n")
    counter = len(DFA.get_accept_states())

    # writes the accept states to file
    for accept_states in DFA.get_accept_states():
        ofp.write(str(accept_states))
        counter -= 1
        if counter != 0: ofp.write(" ")
    ofp.write("\n")

    # close file
    ofp.close()


def main(argv=sys.argv):

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    # try to open file
    try:
        ifp = open(input_file, 'r')
    except IOError:
        print("File not found. Please check to make sure that the file exists/path is correct")
        exit(1)

    # call read file method
    nfa = read_file(ifp)
    
    # build the dfa from the nfa
    dfa = init_DFA(nfa, nfa.get_start_state())
    write_file(output_file, dfa)


if __name__ == "__main__":
    sys.exit(main())
