import z3 as z


def make_constraints_next(n_constraints: int, slope: int = 0x5DEECE66D, intercept: int = 0xB, gen_bits=31):
    # Define some constants
    addend = z.BitVecVal(intercept, 64)
    multiplier = z.BitVecVal(slope, 64)
    mask = z.BitVecVal((1 << 48) - 1, 64)

    # Define symbolic variables for the seed variable
    seeds = {f'seed_{i}': z.BitVec(f'seed_{i}', 64) for i in range(n_constraints)}

    constraints = []

    # Build constraints for the relation in row 175
    for i in range(1, n_constraints):
        constraints.append(seeds[f'seed_{i}'] == z.simplify((seeds[f'seed_{i - 1}'] * multiplier + addend) & mask))

    # Define symbolic variables for the output from next()
    next_outputs = {f'next_output_{i}': z.BitVec(f'output{i}', 32) for i in range(1, n_constraints)}

    # Build the constraints for the relation in row 176
    for i in range(1, n_constraints):
        constraints.append(
            next_outputs[f'next_output_{i}'] == z.simplify(z.Extract(31, 0, z.LShR(seeds[f'seed_{i}'], 48 - gen_bits))))

    return constraints, seeds, next_outputs


def find_seed(sequence_length: int, slope: int = 0x5DEECE66D, intercept: int = 0xB):
    # Define some constants
    addend = z.BitVecVal(intercept, 64)
    multiplier = z.BitVecVal(slope, 64)
    mask = z.BitVecVal((1 << 48) - 1, 64)

    # Note we're generating an extra constraint
    # This is required since we'll be using seed_0 to extract the Random() instantiation value
    next_constraints, seeds, next_outputs = make_constraints_next(n_constraints=sequence_length + 1, gen_bits=32)

    # Define a symbolic variable that we'll use to get the value that instantiated Random()
    original_seed = z.BitVec('original_seed', 64)

    # Build a solver object
    s = z.Solver()

    # Build a constraint that relates seed_0 and the value used to instantiate Random()
    s.add(seeds[f'seed_0'] == (original_seed ^ multiplier) & mask)

    # Next let's add the constraints we've built for next()
    s.add(next_constraints)

    # Lastly, let's return all the objects we've constructed so far
    return s, original_seed, seeds, next_outputs


if __name__ == '__main__':
    known_ints = [-1460590454, 747279288, -1334692577, -539670452, -501340078, -143413999]

    solver, original_seed, seeds, next_ouputs = find_seed(sequence_length=len(known_ints))

    # Notice: we setup the constraints so that next_outputs_1 is the result of seed_1 since we're using seed_0 for other uses
    # Consequently, the index in known_ints is smaller by 1 than the index for next_outputs
    solver.add(next_ouputs[f'next_output_{1}'] == known_ints[0])
    solver.add(next_ouputs[f'next_output_{2}'] == known_ints[1])

    # Lets take a look at our constraints before trying to solve them
    print(solver)

    # Check if there is a solution
    print(solver.check())

    # Print the calculated seed if we found a solution
    if solver.check() == z.sat:
        print(solver.model()[original_seed])
    else:
        print("Didn't find a solution")