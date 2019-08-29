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


if __name__ == '__main__':
    random_nums = [4, 54, 63, 79, 13, 55, 76, 11, 14, 45]

    for i in range(3, 10):
        break_rand(random_nums[:i], random_nums[i])