# Look for #IMPLEMENT tags in this file.
'''
All encodings need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = caged_csp(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the FunPuzz puzzle.

The grid-only encodings do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - An enconding of a FunPuzz grid (without cage constraints) built using only 
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - An enconding of a FunPuzz grid (without cage constraints) built using only n-ary 
      all-different constraints for both the row and column constraints. 

3. caged_csp (worth 25/100 marks) 
    - An enconding built using your choice of (1) binary binary not-equal, or (2) 
      n-ary all-different constraints for the grid.
    - Together with FunPuzz cage constraints.

'''
from cspbase import *
import itertools


def binary_ne_grid(fpuzz_grid):
    size = fpuzz_grid[0][0]
    csp = CSP("FunPuzz_Binary_Ne_Grid")
    vars = []

    # First, create and add all variables to the CSP
    for row in range(size):
        row_vars = []
        for col in range(size):
            variable = Variable(f'V{row}{col}', range(1, size + 1))
            csp.add_var(variable)  # Add variable to CSP here
            row_vars.append(variable)
        vars.append(row_vars)

    # Now, add all constraints to the CSP
    for i in range(size):
        for j in range(size):
            for k in range(j + 1, size):
                # Row constraints
                c1 = Constraint(f'Row_{i}_{j}_{k}', [vars[i][j], vars[i][k]])
                c1.add_satisfying_tuples([t for t in itertools.product(range(1, size + 1), repeat=2) if t[0] != t[1]])
                csp.add_constraint(c1)

                # Column constraints
                c2 = Constraint(f'Col_{j}_{i}_{k}', [vars[j][i], vars[k][i]])
                c2.add_satisfying_tuples([t for t in itertools.product(range(1, size + 1), repeat=2) if t[0] != t[1]])
                csp.add_constraint(c2)

    return csp, vars


def nary_ad_grid(fpuzz_grid):
    size = fpuzz_grid[0][0]
    csp = CSP("FunPuzz_Nary_Ad_Grid")
    vars = []

    for row in range(size):
        row_vars = []
        for col in range(size):
            variable = Variable(f'V{row}{col}', range(1, size + 1))
            csp.add_var(variable)
            row_vars.append(variable)
        vars.append(row_vars)

    for i in range(size):
        row_vars = [vars[i][j] for j in range(size)]
        col_vars = [vars[j][i] for j in range(size)]

        row_constraint = Constraint(f'Row_{i}_AllDiff', row_vars)
        col_constraint = Constraint(f'Col_{i}_AllDiff', col_vars)

        all_diff_tuples = list(itertools.permutations(range(1, size + 1), size))
        row_constraint.add_satisfying_tuples(all_diff_tuples)
        col_constraint.add_satisfying_tuples(all_diff_tuples)

        csp.add_constraint(row_constraint)
        csp.add_constraint(col_constraint)
    return csp, vars


def caged_csp(fpuzz_grid):
    size = fpuzz_grid[0][0]
    csp = CSP("FunPuzz_Caged_CSP")
    vars = []

    # Create and add all variables to the CSP
    for row in range(size):
        row_vars = []
        for col in range(size):
            variable = Variable(f'V{row}{col}', range(1, size + 1))
            csp.add_var(variable)  # Add variable to CSP here
            row_vars.append(variable)
        vars.append(row_vars)

    # Add binary not-equal constraints for rows and columns
    for i in range(size):
        for j in range(size):
            for k in range(j + 1, size):
                # Row constraints
                c1 = Constraint(f'Row_{i}_{j}_{k}', [vars[i][j], vars[i][k]])
                c1.add_satisfying_tuples([(a, b) for a in range(1, size + 1) for b in range(1, size + 1) if a != b])
                csp.add_constraint(c1)

                # Column constraints (corrected to use column variables)
                c2 = Constraint(f'Col_{j}_{i}_{k}', [vars[j][i], vars[k][i]])
                c2.add_satisfying_tuples([(a, b) for a in range(1, size + 1) for b in range(1, size + 1) if a != b])
                csp.add_constraint(c2)

    # Add cage constraints
    for cage in fpuzz_grid[1:]:
        cage_vars = [vars[int(str(cell)[0]) - 1][int(str(cell)[1]) - 1] for cell in cage[:-2]]
        target = cage[-2]
        operation = cage[-1]

        cage_constraint = create_cage_constraint(cage_vars, target, operation)
        csp.add_constraint(cage_constraint)

    return csp, vars


def create_cage_constraint(cage_vars, target, operation):

    def exist_subtraction(assign):
        for per in itertools.permutations(assign, len(assign)):
            result = per[0]
            for i in range(1, len(per)):
                result -= per[i]
            if result == target:
                return True
        return False

    def exist_division(assign):
        for per in itertools.permutations(assign, len(assign)):
            result = per[0]
            for i in range(1, len(per)):
                result /= per[i]
            if result == target:
                return True
        return False

    def prod(iterable):
        result = 1
        for x in iterable:
            result *= x
        return result

    def is_valid_cage_assignment(assignment):
        if operation == 0:
            return sum(assignment) == target
        elif operation == 1:
            return exist_subtraction(assignment)
        elif operation == 2:
            return exist_division(assignment)
        elif operation == 3:
            return prod(assignment) == target

    cage_constraint = Constraint("CageConstraint", cage_vars)
    possible_values = list(itertools.product(*(var.cur_domain() for var in cage_vars)))
    satisfying_tuples = [t for t in possible_values if is_valid_cage_assignment(t)]
    cage_constraint.add_satisfying_tuples(satisfying_tuples)

    return cage_constraint
