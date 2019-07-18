#   Copyright (c) 2019  PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from x2paddle.core.graph import GraphNode


class Layer(object):
    def __init__(self):
        self.op = None
        self.param_attr = dict()
        self.inputs = dict()
        self.output = None

    def get_code(self):
        layer_code = ""
        if self.output is not None:
            if isinstance(self.output, str):
                layer_code = self.output + " = "
            else:
                layer_code = self.output.layer_name + " = "

        layer_code = layer_code + "fluid.layers." + self.op + "("

        if isinstance(self.inputs, list):
            in_list = "["
            for input in self.inputs:
                assert isinstance(
                    input, GraphNode), "Type of input should be GraphNode"
                if hasattr(input, "index"):
                    in_list += (input.layer_name + "[{}]".format(input.index) +
                                ", ")
                else:
                    in_list += (input.layer_name + ", ")
            inlist = in_list.strip(", ") + "], "
        elif isinstance(self.inputs, dict):
            for key, input in self.inputs.items():
                assert isinstance(
                    input, GraphNode), "Type of input should be GraphNode"
                if hasattr(input, "index"):
                    layer_code = layer_code + key + "={}, ".format(
                        input.layer_name + "[{}]".format(input.index))
                else:
                    layer_code = layer_code + key + "={}, ".format(
                        input.layer_name)
        elif isinstance(self.inputs, GraphNode):
            if hasattr(self.inputs, "index"):
                layer_code += (self.inputs.layer_name +
                               "[{}]".format(self.inputs.index) + ", ")
            else:
                layer_code += (self.inputs.layer_name + ", ")
        elif isinstance(self.inputs, str):
            layer_code += (self.inputs + ", ")
        else:
            raise Exception("Unknown type of inputs.")

        for key, value in self.param_attr.items():
            layer_code = layer_code + key + "={}, ".format(value)
        layer_code = layer_code.strip(", ")

        return layer_code + ")"


class FluidCode(object):
    def __init__(self):
        self.layers = list()

    def add_layer(self, op, inputs, output, param_attr=None):
        layer = Layer()
        layer.op = op
        if inputs is not None:
            layer.inputs = inputs
        layer.output = output
        if param_attr is not None:
            layer.param_attr = param_attr
        self.layers.append(layer)

    def add_note(self, note):
        # note should be string
        self.layers.append(note)

    def clear(self):
        self.layers = list()

    def gen_codes(self):
        codes = list()
        for layer in self.layers:
            if isinstance(layer, Layer):
                codes.append(layer.get_code())
            elif isinstance(layer, str):
                codes.append(layer)