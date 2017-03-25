"""
This module allows fair distribution of any number of **objects** through a group of **targets**.
By means of a linear programming solver, the module takes into consideration the **weights**/self._weights of the **targets** relative to the **objects**.
and distributes them in the **fairest way possible**.
"""
from pulp import *


class FairDistributor():
  """
  This class represents a general fair distributor.
  Objects of this class allow solving fair distribution problems. 
  """
  def __init__(self, targets, objects, weights):
    """
    This constructor is simply a way to simplify the flow of solving a problem.
    """
    super(FairDistributor, self).__init__()
    set_data(targets, objects, weights)

  def set_data(self, targets, objects, weights):
    """
    This method is a general setter for the data associated with the problem.
    Data is being validated by the validator method.
    """
    # Test inputted data
    self._targets = targets
    self._things = objects
    self._weights = weights 

  def distribute(self, fairness=True):
    """
    This method is responsible for actually solving the linear programming problem.
    It uses the data in the instance variables.
    The optional parameter **fairness** indicates if the solution should minimize individual effort. By default the solution will enforce this condition.
    """
    # State problem
    problem = LpProblem("Fair Distribution Problem", LpMinimize)

    # Prepare variables
    users_tasks_variables = {'x'+str(u)+str(t): LpVariable('x' + str(u) + str(t), lowBound=0, cat='Binary')
                             for (u, user) in enumerate(self._objects) for (t, task) in enumerate(self._targets)}

    # Generate linear expression for self._weights (Summation #1)
    preferences_variables = [(users_tasks_variables['x' + str(u) + str(t)], self._weights[u][t])
                             for (u, user) in enumerate(self._objects) for (t, task) in enumerate(self._targets)]
    effort_expression = LpAffineExpression(preferences_variables)

    # Generate linear expression for effort distribution (Summation #2)
    effort_diff_vars = []
    if fairness :
      total_users = len(self._objects)
      for (u, user) in enumerate(self._objects):
          effort_diff_aux_variable = LpVariable('effort_diff_'+str(u), lowBound=0)
          effort_diff_vars.append(effort_diff_aux_variable)

          negative_factor = -1 * total_users
          negative_effort_diff = LpAffineExpression([(users_tasks_variables[
                                                    'x' + str(u) + str(t)], negative_factor * self._weights[u][t]) for (t, task) in enumerate(self._targets)]) + effort_expression
          positive_factor = 1 * total_users
          positive_effort_diff = LpAffineExpression([(users_tasks_variables[
                                                    'x' + str(u) + str(t)], positive_factor * self._weights[u][t]) for (t, task) in enumerate(self._targets)]) - effort_expression

          problem += negative_effort_diff <= effort_diff_aux_variable, 'abs negative effort diff ' + \
              str(u)
          problem += positive_effort_diff <= effort_diff_aux_variable, 'abs positive effort diff ' + \
              str(u)

    # Constraints
    # Each task must be done
    task_constraints = [lpSum([users_tasks_variables['x' + str(u) + str(t)] for (u, self._objects)
                               in enumerate(self._objects)]) for (t, task) in enumerate(self._targets)]
    for (tc, task_constraint) in enumerate(task_constraints):
        problem += task_constraint == 1, 'Task ' + str(tc) + ' must be done'


    # Set objective function
    problem += effort_expression + \
        lpSum(effort_diff_vars), "obj"

    problem.writeLP('problem.lp')
    problem.solve()

    # Output
    print("Status:", LpStatus[problem.status])
    # Print the value of the variables at the optimum
    for v in problem.variables():
        print(v.name, "=", v.varValue)
    # Print the value of the objective
    print("objective=", value(problem.objective))

