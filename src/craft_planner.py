import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])

posIngred = {}


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.
        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.
    
    
    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        ingredients = {}
        if( 'Requires' in rule.keys()):
            ingredients.update(rule['Requires'])
        if( 'Consumes' in rule.keys()):
            ingredients.update(rule['Consumes'])
            
        for item in ingredients:
            if(not(item in state.keys() and ingredients[item]<=state[item])):
                return False
            
        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = State.copy(state)
        for item in rule['Produces']:
            if(item in next_state.keys()):
                next_state[item] = next_state[item] + rule['Produces'][item]
        if('Consumes' in rule.keys()):
            for item in rule['Consumes']:
                if(item in next_state.keys()):
                    next_state[item] = next_state[item] - rule['Consumes'][item]
        if(next_state==None):
            print("cant do that")
        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for item in goal:
            if(not (item in state.keys() and state[item] >= goal[item])):
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state):
    # Implement your heuristic here!
    for item in state:
        if(state[item]==0):
            continue
        if ((not(item in posIngred)) or (state[item]>posIngred[item])):
            return -1
    return 0

def search(graph, state, is_goal, limit, heuristic):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    path = []
    notDone = True
    queue = [(state,heuristic(state),0)]
    visited = {state: (None,0,'None')}
    total = 0
    while ((time() - start_time < limit) and (len(queue)>0) and notDone):
        current = queue[0][0]
        currentCost = queue[0][2]
        queue.remove(queue[0])
        for node in graph(current):
            newCost = currentCost+node[2] 
            if(is_goal(node[1])):
                visited[node[1]] = (current,newCost,node[0])
                current = node[1]
                print(currentCost, 'was cost')
                notDone = False
                break
            elif(not (node[1] in visited)):
                total = total+1
                visited[node[1]] = (current,newCost,node[0])
                heur = heuristic(node[1])
                #print(node)
                #print(heur)
                if(heur >= 0):
                    queue.append((node[1],heur,newCost+heur))
            elif(newCost<visited[node[1]][1]):
                visited[node[1]] = (current,newCost,node[0])   
            queue.sort(reverse=True,key=byVal)
                
           
    print(total)    
    if(not notDone):
        while (visited[current][0]!=None):
            path.append((current,visited[current][2]))
            current = visited[current][0]
        path.reverse()
        print(time() - start_time, 'seconds.')
        print(len(path), "is length")
        return path
        
    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None
    
    
def byVal(e):
    return e[2]
    
def makePosIngred(goal,rules):
    listGoal = list(goal.keys())
    for item in listGoal:
        for rule in rules:
            if(item in rule['Produces']):
                if('Consumes' in rule.keys()):
                    for item2 in rule['Consumes'].keys():
                        if (not(item2 in goal)):
                            goal[item2] = rule['Consumes'][item2]*goal[item]
                            listGoal.append(item2)
                        else:
                            goal[item2] = goal[item2]+rule['Consumes'][item2]*goal[item]
                if('Requires' in rule.keys()):
                    for item2 in rule['Requires'].keys():
                        if (not(item2 in goal)):
                            goal[item2] = rule['Requires'][item2]
                            listGoal.append(item2)
    return goal
    

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    # print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    rules = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)
        rules.append(rule)
        

    # Create a function which checks for the goal
    goal=(Crafting['Goal'])
    is_goal = make_goal_checker(Crafting['Goal'])
    


    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])
    posIngred.update(makePosIngred(goal.copy(),rules))
    
    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)
