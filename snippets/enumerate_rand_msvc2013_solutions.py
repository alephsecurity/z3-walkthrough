import z3 as z


def break_rand(nums: list, next_num: int):
    n_nums = len(nums)
    # print(f'len nums: {n_nums}')

    states = {f'state_{i}': z.BitVec(f'state_{i}', 32) for i in range(1, n_nums + 2)}
    # print(states)
    output_next = z.BitVec('output_next', 32)

    s = z.Solver()

    for i in range(2, n_nums + 2):
        s.add(states[f'state_{i}'] == states[f'state_{i - 1}'] * 214013 + 2531011)

    for i in range(1, n_nums + 1):
        s.add(z.URem((states[f'state_{i}'] >> 16) & 0x7FFF, 100) == nums[i - 1])

    s.add(output_next == z.URem((states[f'state_{n_nums + 1}'] >> 16) & 0x7FFF, 100))

    # print(s)

    if s.check() == z.sat:
        print(f'For the sequence: {nums}, problem is satisfiable')
        print(f'We were expecting: {next_num} and got: {s.model()[output_next]}\n')
    else:
        print(f'For the sequence: {nums}, problem is unsatisfiable')

    return s, states, output_next


def enumerate_solutions(nums: list, next_num: int, print_model: bool = False, print_solutions: bool = False):
    s, states, output_next = break_rand(nums=nums, next_num=next_num)

    counter = 0
    solution_list = []

    while s.check() == z.sat:
        counter += 1
        solution_list.append(s.model()[output_next].as_long())

        print(f'Solution #{counter}')
        if print_model:
            print(f'{s.model()}\n')

        # Create constraints using string concatenation
        or_expression = 'z.Or('
        for i in states.keys():
            if i == 'output_next': continue
            or_expression += f'states[i] != s.model()[states[i]], '
        or_expression += ')'

        s.add(eval(or_expression))

    print(f'Found a total of {counter} solutions')
    if print_solutions:
        print(f'The solutions are: \n{solution_list}')
        print(f'The solution set is: \n{set(solution_list)}')


if __name__ == '__main__':
    random_nums = [4, 54, 63, 79, 13, 55, 76, 11, 14, 45]

    enumerate_solutions(random_nums[:5], random_nums[5], print_model = True)
