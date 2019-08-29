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


def find_seed_nextLong(sequence_length: int, slope: int = 0x5DEECE66D, intercept: int = 0xB):
    # Define some constants
    addend = z.BitVecVal(intercept, 64)
    multiplier = z.BitVecVal(slope, 64)
    mask = z.BitVecVal((1 << 48) - 1, 64)

    # Note we're generating double the constraints in the sequence_length + 1
    # This is required since we'll be using seed_0 to extract the Random() instantiation value
    # Furthermore, each nextLong call consumes two outputs from next()
    next_constraints, seeds, next_outputs = make_constraints_next(n_constraints=2 * sequence_length + 1, gen_bits=32)

    # Define a symbolic variable that we'll use to get the value that instantiated Random()
    original_seed = z.BitVec('original_seed', 64)

    # Build a solver object
    s = z.Solver()

    # Build a constraint that relates seed_0 and the value used to instantiate Random()
    s.add(seeds[f'seed_0'] == (original_seed ^ multiplier) & mask)

    # Next let's add the constraints we've built for next()
    s.add(next_constraints)

    # Define symbolic variables for the output from nextLong
    # Notice: we're using a symbolic variable of type Int
    # Since nextLong does a sum on ints, it's easier to model this using Z3 arithmetic models
    # This differs from previous examples where we used BitVec objects exclusively
    # Consequently, we'll be using the conversion method BV2Int that takes a BitVec object and turns it into an Int object
    nextLong_outputs = {f'nextLong_output_{i}': z.Int(f'nextLong_output_{i}') for i in range(1, sequence_length + 1)}

    # Finally, let's add the constraints for nextLong
    for i, j in zip(range(1, sequence_length + 1), range(1, sequence_length * 2 + 1, 2)):
        # Notice: we've replaced the bit shift operator in the source with an enquivalent multiplication
        # Z3 doesn't support bit shift operations on Int objects
        first_next = z.BV2Int(next_outputs[f'next_output_{j}'], is_signed=True) * 2 ** 32
        second_next = z.BV2Int(next_outputs[f'next_output_{j + 1}'], is_signed=True)
        s.add(nextLong_outputs[f'nextLong_output_{i}'] == first_next + second_next)

    # Lastly, let's return all the objects we've constructed so far
    return s, original_seed, nextLong_outputs


if __name__ == '__main__':
    known_longs = [-6273188232032513096, -5732460968968632244, -2153239239327503087, -1872204974168004231]

    solver, original_seed, nextLong_outputs = find_seed_nextLong(sequence_length=len(known_longs))

    # As mentioned before, we should have enough information in one long to extract the instantiation value
    solver.add(nextLong_outputs[f'nextLong_output_{1}'] == known_longs[0])

    # Lets take a look at our constraints before trying to solve them
    print(solver)

    # Check if there is a solution
    print(solver.check())

    # Print the calculated seed if we found a solution
    if solver.check() == z.sat:
        print(solver.model()[original_seed])
    else:
        print("Didn't find a solution")