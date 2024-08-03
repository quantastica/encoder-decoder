# This code is part of quantastica.encoder_decoder
#
# (C) Copyright Quantastica 2024.
# https://quantastica.com/
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from collections import Counter

def quantize(value, min_val, max_val, num_bits):
    if value < min_val or value > max_val:
        raise ValueError("Value out of range")

    num_levels = 2 ** num_bits
    interval = (max_val - min_val) / (num_levels - 1)
    quantized_value = round((value - min_val) / interval)
    
    return quantized_value


def dequantize(quantized_value, min_val, max_val, num_bits):
    num_levels = 2 ** num_bits
    interval = (max_val - min_val) / (num_levels - 1)
    dequantized_value = quantized_value * interval + min_val
    return dequantized_value


def encode_value(col_def, qubit, value):
    quantized_value = quantize(value, col_def["min"], col_def["max"], col_def["bits"])    
    quantized_binary = bin(quantized_value)[2:].zfill(col_def["bits"])

    qasm = ""
    for bit_index in range(col_def["bits"]):
        if(quantized_binary[col_def["bits"] - bit_index - 1] == "1"):
            qasm += "x q[" + str(qubit + bit_index) + "];\n"

    return qasm


def decode_value(outcome, col_def, qubit):
    quantized_value = 0
    for bit_index in range(col_def["bits"]):
        if(outcome[qubit + bit_index]):
            quantized_value += pow(2, bit_index)

    value = dequantize(quantized_value, col_def["min"], col_def["max"], col_def["bits"])
    if(col_def["type"] == "integer"):
        value = int(value)
    return value


def most_frequent(counts):
    most_frequent = []
    most_common = Counter(counts).most_common(1)[0][0]
    # Assuming that bitstrings from multiple classical registers are split by space
    # And our register of interest is last register which is first bitstring
    most_common = most_common.split(" ")[0]
    for c in most_common:
        if(c == "1"):
            most_frequent.append(1)
        else:
            most_frequent.append(0)

    most_frequent.reverse()

    return most_frequent
        

def encode_input_basis(input_data_row, input_encoding):
    qasm = ""
    
    qubit = input_encoding["qubitOffset"]
    for col_def in input_encoding["colDefs"]:

        if(col_def["structure"] == "scalar"):
            value = input_data_row[col_def["name"]]
            qasm += encode_value(col_def, qubit, value)
            qubit += col_def["bits"]

        elif(col_def["structure"] == "vector"):
            vector = input_data_row[col_def["name"]]
            for element_index in range(col_def["dimensions"][0]):
                value = vector[element_index]
                qasm += encode_value(col_def, qubit, value)
                qubit += col_def["bits"]

        elif(col_def["structure"] == "matrix"):
            matrix = input_data_row[col_def["name"]]
            for row_index in range(col_def["dimensions"][0]):
                row = matrix[row_index]
                for col_index in range(col_def["dimensions"][1]):
                    value = row[col_index]
                    qasm += encode_value(col_def, qubit, value)
                    qubit += col_def["bits"]
    
    input_qasm = ""
    input_qasm += "OPENQASM 2.0;\n"
    input_qasm += "include \"qelib1.inc\";\n"
    input_qasm += "qreg q[" + str(qubit) + "];\n"
    input_qasm += qasm

    return input_qasm


def encode_input_custom(input_data_row, input_encoding):
    encoding_function = input_encoding["customFunction"]["python"]
    return encoding_function(input_data_row, input_encoding)


def encode_input(input_data_row, input_encoding):
    if(input_encoding["type"] == "basis"):
        return encode_input_basis(input_data_row, input_encoding)

    if(input_encoding["type"] == "custom"):
        return encode_input_custom(input_data_row, input_encoding)

    return ""


def decode_output_basis(counts, output_decoding):
    output_data_row = {}

    outcome = most_frequent(counts)

    qubit = output_decoding["qubitOffset"]
    for col_def in output_decoding["colDefs"]:
        if(col_def["structure"] == "scalar"):
            value = decode_value(outcome, col_def, qubit)
            qubit += col_def["bits"]
            output_data_row[col_def["name"]] = value
        elif(col_def["structure"] == "vector"):
            vector = []
            for element_index in range(col_def["dimensions"][0]):
                value = decode_value(outcome, col_def, qubit)
                vector.append(value)
                qubit += col_def["bits"]
            output_data_row[col_def["name"]] = vector
        elif(col_def["structure"] == "matrix"):
            matrix = [];
            for row_index in range(col_def["dimensions"][0]):
                row = []
                for col_index in range(col_def["dimensions"][1]):
                    value = decode_value(outcome, col_def, qubit)
                    row.append(value)
                    qubit += col_def["bits"]
                matrix.append(row)
            output_data_row[col_def["name"]] = matrix
    
    return output_data_row


def decode_output_custom(counts, output_decoding):
    decoding_function = output_decoding["customFunction"]["python"]
    return decoding_function(counts, output_decoding)


def decode_output(counts, output_decoding, unpack_values=False):
    output_data_row = {}
    if(output_decoding["type"] == "basis"):
        output_data_row = decode_output_basis(counts, output_decoding)
    elif(output_decoding["type"] == "custom"):
        output_data_row = decode_output_custom(counts, output_decoding)
    else:
        raise Exception("Unknown decoding scheme \"" + output_decoding["type"] + "\".")

    if(unpack_values):
        if(len(output_decoding["colDefs"]) == 1):
            return output_data_row[output_decoding["colDefs"][0]["name"]]
        else:
            output_list = []
            for col_def in output_decoding["colDefs"]:
                output_list.append(output_data_row[col_def["name"]])
            return tuple(output_list)

    return output_data_row
