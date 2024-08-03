# Encoder/Decoder

Helper library for encoding classical data into quantum state and vice versa. Primarily built for [Quantum Programming Studio](https://quantum-circuit.com).


## encode_input(input_data_row, input_encoding)

Function returns OpenQASM 2.0 code which prepares quantum state with input data encoded.

**Arguments:**

`input_data_row` dictionary containing single row of data to be encoded into quantum state in a form `{ "column_name": value, ... }`.

Example:

```json

{
    "a": 11,
    "b": 14
}

```

(in this example, we have two columns: `a` with value `11` and `b` with value `14`).


`input_encoding` dictionary describing encoding scheme and column definitions.

Fields:

- `type` encoding scheme. Currently, only two encoding schemes are implemented: 

    - `basis` basis encoding

    - `custom` custom encoding, which expects you to provide encoding function

- `customFunction.python` used with `custom` encoding. Your custom encoding function, which receives the same arguments as this `encode_input` function and returns OpenQASM 2.0 string.

- `qubitOffset` used by `basis` encoding. For example, if input data requires 8 bits to be encoded and qubitOffset is 3, then data will be encoded into qubits [3..10] (from fourth to eleventh qubit).

- `colDefs` list of column definitions. Column definition is dictionary containing following fields:

    - `name` column name string. Must be valid identifier consisting of letters, numbers or underscores and must start with a letter or underscore.

    - `structure` string describing structure of a value. Can be one of: `scalar`, `vector` or `matrix`.

    - `dimensions` dimension of a vector or matrix. List of integers. Empty if structure is `scalar`, single integer if structure is `vector` (number of elements in a vector) and two integers if structure is `matrix` (number of rows and number of columns in a matrix).

    - `type` data type string of a scalar value or data type of the elements of a vector/matrix. Can be `integer` or `float`.

    - `min` minimal value. Used by built-in `basis` encoder (or you can use it in your custom encoding function).

    - `max` maximal value. Used by built-in `basis` encoder (or you can use it in your custom encoding function).

    - `bits` number of (classical) bits. Used by built-in `basis` encoder: floating point numbers and integers whose range defined by min...max is out of range `[0..2**bits]` will be quantized to range `[0..2**bits]`. Or, you can use this field in your custom encoding function as Your Majesty wishes.


**Example for `basis` encoding:**

```python

from quantastica.encoder_decoder import encode_input

input_encoding = {
    "type": "basis",
    "qubitOffset": 1,
    "colDefs": [
        {
            "name": "a",
            "structure": "scalar",
            "dimensions": [],
            "type": "integer",
            "min": 0,
            "max": 15,
            "bits": 4
        },
        {
            "name": "b",
            "structure": "scalar",
            "dimensions": [],
            "type": "integer",
            "min": 0,
            "max": 15,
            "bits": 4
        }
    ]
}

input_data_row = { "a": 11, "b": 14 }

qasm = encode_data(input_data_row, input_encoding)

```


Example will return following OpenQASM 2.0 string:

```

OPENQASM 2.0;
include "qelib1.inc";
qreg q[9];
x q[1];
x q[2];
x q[4];
x q[6];
x q[7];
x q[8];

```


**Example for `custom` encoding:**

```python

from quantastica.encoder_decoder import encode_input

def custom_encoder(input_data_row, input_encoding):
    qasm = ""
    qasm += "OPENQASM 2.0;\n"
    qasm += "include \"qelib1.inc\";\n"

    # ... your code here ..

    return qasm


input_encoding = {
    "type": "custom",
    "customFunction": {
        "python": custom_encoder
    },
    "qubitOffset": 1,
    "colDefs": [
        {
            "name": "a",
            "structure": "scalar",
            "dimensions": [],
            "type": "integer",
            "min": 0,
            "max": 15,
            "bits": 4
        },
        {
            "name": "b",
            "structure": "scalar",
            "dimensions": [],
            "type": "integer",
            "min": 0,
            "max": 15,
            "bits": 4
        }
    ]
}

input_data_row = { "a": 11, "b": 14 }

qasm = encode_data(input_data_row, input_encoding)

```

## decode_output(counts, output_decoding, unpack_values=False)

Function returns output data which is decoded from sampling results of a quantum computer (or simulator).

**Arguments:**

`counts` dictionary in a form `{ "bitstring": occurrences, ... }`. For example: `{ "011010111": 970, "001101001": 30 }`.

`output_decoding` distionary describing encoding scheme and column definitions.

Fields:

- `type` decoding scheme. Currently, only two decoding schemes are implemented: 

    - `basis` basis decoding

    - `custom` custom decoding, which expects you to provide decoding function

- `customFunction.python` used with `custom` decoding. Your custom decoding function, which receives the same arguments as this `decode_output` function and returns data row.

- `qubitOffset` used by `basis` decoding. For example, if output data is 8 bits wide and qubitOffset is 3, then data will be decoded from qubits [3..10] (from fourth to eleventh qubit).

- `colDefs` list of column definitions. Column definition is dictionary containing following fields:

    - `name` column name string. Must be valid identifier consisting of letters, numbers or underscores and must start with a letter or underscore.

    - `structure` string describing structure of a value. Can be one of: `scalar`, `vector` or `matrix`.

    - `dimensions` dimension of a vector or matrix. List of integers. Empty if structure is `scalar`, single integer if structure is `vector` (number of elements in a vector) and two integers if structure is `matrix` (number of rows and number of columns in a matrix).

    - `type` data type string of a scalar value or data type of the elements of a vector/matrix. Can be `integer` or `float`.

    - `min` minimal value. Used by built-in `basis` decoder (or you can use it in your custom decoding function).

    - `max` maximal value. Used by built-in `basis` decoder (or you can use it in your custom decoding function).

    - `bits` number of (classical) bits. Used by built-in `basis` decoder: floating point numbers and integers will be dequantized from range `[0..2**bits]` to the range defined by min..max. Or, you can use this field in your custom encoding function as you wish.

`unpack_data` boolean. When this argument is `False` (default), function will return dictionary. For example: `{ "c": 25 }`. If `unpack_data` is `True`, the function will simply return only value (or tuple of values if multiple columns are defined).


**Example for `basis` decoding:**

```python

from quantastica.encoder_decoder import decode_output

output_decoding = {
    "type": "basis",
    "qubitOffset": 5,
    "colDefs": [
        {
            "name": "c",
            "structure": "scalar",
            "dimensions": [],
            "type": "integer",
            "min": 0,
            "max": 31,
            "bits": 5
        }
    ]
}

counts = { "1100110110": 1024 } # output from quantum computer or simulator

output_data_row = decode_output(counts, output_decoding)

```

Example output:

```python

{ "c": 25 }

```

**Example for `custom` decoding:**

```python

from quantastica.encoder_decoder import decode_output

def custom_decoder(counts, output_decoding):
    output_data_row = {}

    # ... your code here ...
    
    return output_data_row


output_decoding = {
    "type": "custom",
    "customFunction": {
        "python": custom_decoder
    },
    "qubitOffset": 5,
    "colDefs": [
        {
            "name": "c",
            "structure": "scalar",
            "dimensions": [],
            "type": "integer",
            "min": 0,
            "max": 31,
            "bits": 5
        }
    ]
}

counts = { "1100110110": 1024 } # output from quantum computer or simulator

output_data_row = decode_output(counts, output_decoding)

```


That's it. Enjoy! :P
