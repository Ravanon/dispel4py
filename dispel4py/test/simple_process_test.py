# Copyright (c) The University of Edinburgh 2014
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
Tests for simple sequential processing engine.

Using nose (https://nose.readthedocs.org/en/latest/) run as follows::

    $ nosetests dispel4py/test/simple_process_test.py 
    ...
    ----------------------------------------------------------------------
    Ran 3 tests in 0.006s

    OK
'''

from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.core import GenericPE, NAME
from dispel4py import simple_process

from dispel4py.examples.graph_testing.testing_PEs import TestProducer, TestOneInOneOut, TestTwoInOneOut

from nose import tools

def testPipeline():
    graph = WorkflowGraph()
    prod = TestProducer()
    prev = prod
    for i in range(5):
        cons = TestOneInOneOut()
        graph.connect(prev, 'output', cons, 'input')
        prev = cons
    results = simple_process.process(graph, { prod: [{}, {}, {}, {}, {}] })
    tools.eq_({(prev.id, 'output'):[1, 2, 3, 4, 5]}, results)
    
def testSquare():
    graph = WorkflowGraph()
    prod = TestProducer(2)
    cons1 = TestOneInOneOut()
    cons2 = TestOneInOneOut()
    last = TestTwoInOneOut()
    graph.connect(prod, 'output0', cons1, 'input')
    graph.connect(prod, 'output1', cons2, 'input')
    graph.connect(cons1, 'output', last, 'input0')
    graph.connect(cons2, 'output', last, 'input1')
    results = simple_process.process(graph, { prod : [{}]} )
    tools.eq_({(last.id, 'output'):['1', '1']}, results)
        
def testTee():
    graph = WorkflowGraph()
    prod = TestProducer()
    prev = prod
    cons1 = TestOneInOneOut()
    cons2 = TestOneInOneOut()
    graph.connect(prod, 'output', cons1, 'input')
    graph.connect(prod, 'output', cons2, 'input')
    results = simple_process.process(graph, {prod: [{}, {}, {}, {}, {}]})
    tools.eq_({(cons1.id, 'output'): [1, 2, 3, 4, 5], (cons2.id, 'output'): [1, 2, 3, 4, 5]}, results)
    
def testPipelineWithInput():
    graph = WorkflowGraph()
    first = TestOneInOneOut()
    prev = first
    for i in range(5):
        cons = TestOneInOneOut()
        graph.connect(prev, 'output', cons, 'input')
        prev = cons
    results = simple_process.process(graph, { first: [{'input': 1}, {'input': 2}, {'input': 3}] })
    tools.eq_({(prev.id, 'output'):[1, 2, 3]}, results)
    
def testPipelineWithInputId():
    graph = WorkflowGraph()
    first = TestOneInOneOut()
    prev = first
    for i in range(5):
        cons = TestOneInOneOut()
        graph.connect(prev, 'output', cons, 'input')
        prev = cons
    results = simple_process.process(graph, { first.id: [{'input': 1}] } )
    tools.eq_({(prev.id, 'output'):[1]}, results)
    
def testSimplePE():
    graph = WorkflowGraph()
    class TestPE(GenericPE):
        def __init__(self):
            GenericPE.__init__(self)
            self._add_input('input')
            self._add_output('output')
        def _process(self, data):
            return { 'output' : data['input'] }
    test = TestPE()
    graph.add(test)
    results = simple_process.process(graph, { test.id: [{'input': 1}] } )
    tools.eq_({(test.id, 'output'):[1]}, results)
    
def testOnePE():
    graph = WorkflowGraph()
    prod = TestProducer()
    graph.add(prod)
    results = simple_process.process(graph, { prod: [{}] })
    tools.eq_({(prod.id, 'output'):[1]}, results)
