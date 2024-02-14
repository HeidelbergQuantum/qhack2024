import itertools
import json
import pennylane as qml
import pennylane.numpy as np

# You can use auxiliary functions if you are more comfortable with them
# Put your code here #


def circuit(oracle):
    """
    Circuit whose output will determine the team that will carry out the project.

    Args:
        - oracle (callable): the oracle to use in the circuit. To use it, you can write ``oracle(wires = <wires>))``

    You do not have to return anything, just write the gates you need.
    """

    # Step 1: prepare a superposition between all states with exactly two ones.

    # Step 2: Use the Oracle to flip the sign of the solution states (when exactly the two ones correspond to two not lazy workers).

    # Step 3: Use an adapted version of (we didn't use a superposition of all possible states) the Grover diffusion operator 
    #         to increase the probability of the solution states in exchange for the minus sign.

    # Step 4: Do 2 to 3 as often as necessary to get the 95%

    # return qml.expval(endstate)



# These functions are responsible for testing the solution.

def run(case: str) -> str:
    workers = json.loads(case)

    def oracle_maker():
        """
        This function will create the Project oracle of the statement from the list of non-lazy workers.

        Returns:
            callable: the oracle function
        """

        def oracle(wires):

            class op(qml.operation.Operation):
                num_wires = 9
                grad_method = None

                def __init__(self, wires, id=None):
                    super().__init__(wires=wires, id=id)

                @property
                def num_params(self):
                    return 0

                @staticmethod
                def compute_decomposition(wires):
                    n_workers = 8
                    matrix = np.eye(2 ** n_workers)

                    for x in range(2 ** n_workers):
                        bit_strings = np.array([int(i) for i in f"{x:0{n_workers}b}"])
                        if sum(bit_strings[workers]) > 1:
                            matrix[x, x] = -1

                    ops = []
                    ops.append(qml.Hadamard(wires=wires[-1]))
                    ops.append(qml.ctrl(qml.QubitUnitary(matrix, wires=wires[:-1]), control=wires[-1]))
                    ops.append(qml.Hadamard(wires=wires[-1]))

                    return ops

            return op(wires=wires)

        return oracle

    dev = qml.device("default.qubit", wires=9)
    oracle = oracle_maker()
    @qml.qnode(dev)
    def circuit_solution(oracle):
        circuit(oracle)
        return qml.probs(wires = range(8))

    return json.dumps([float(i) for i in circuit_solution(oracle)] + workers)


def check(have: str, want: str) -> None:
    have = json.loads(have)
    probs = have[:2**8]
    workers = have[2**8:]
    sol = 0
    n_workers = 8
    for x in range(2 ** n_workers):
        bit_strings = np.array([int(i) for i in f"{x:0{n_workers}b}"])
        if sum(bit_strings[workers]) == 2:
            num_dec = int(''.join(map(str, bit_strings)), 2)
            sol += probs[num_dec]

    assert sol >= 0.95, "The probability success is less than 0.95"


# These are the public test cases
test_cases = [
    ('[0, 1, 3, 6]', 'No output'),
    ('[1,7]', 'No output'),
    ('[0, 1, 2, 3, 4, 5, 6, 7]', 'No output')
]

# This will run the public test cases locally
for i, (input_, expected_output) in enumerate(test_cases):
    print(f"Running test case {i} with input '{input_}'...")

    try:
        output = run(input_)

    except Exception as exc:
        print(f"Runtime Error. {exc}")

    else:
        if message := check(output, expected_output):
            print(f"Wrong Answer. Have: '{output}'. Want: '{expected_output}'.")

        else:
            print("Correct!")