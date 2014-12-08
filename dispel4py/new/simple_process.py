import types
from dispel4py.core import GenericPE
from processor import GenericWrapper, SimpleProcessingPE
import processor


def simpleLogger(self, msg):
    print("%s: %s" % (self.id, msg))

def process_and_return(workflow, inputs, resultmappings=None):
    numnodes = 0
    for node in workflow.graph.nodes():
        numnodes += 1
        node.getContainedObject().numprocesses = 1
    processes, inputmappings, outputmappings = processor.assign_and_connect(workflow, numnodes)
    # print 'Processes: %s' % processes
    # print inputmappings
    # print outputmappings
    proc_to_pe = {}
    for node in workflow.graph.nodes():
        pe = node.getContainedObject()
        proc_to_pe[processes[pe.id][0]] = pe
    
    simple = SimpleProcessingPE(inputmappings, outputmappings, proc_to_pe)
    simple.id = 'SimplePE'
    simple.result_mappings = resultmappings
    wrapper = SimpleProcessingWrapper(simple, [inputs])
    wrapper.targets = {}
    wrapper.sources = {}
    wrapper.process()
    return wrapper.outputs
    
def process(workflow, inputs, args, resultmappings=None):
    print 'Inputs: %s' % { pe.id: data for pe, data in inputs.iteritems() }
    results = process_and_return(workflow, inputs, resultmappings)
    print 'Outputs: %s' % results
    
class SimpleProcessingWrapper(GenericWrapper):
    
    def __init__(self, pe, provided_inputs=None):
        GenericWrapper.__init__(self, pe)
        self.pe.log = types.MethodType(simpleLogger, pe)
        self.provided_inputs = provided_inputs
        self.outputs = {}

    def _read(self):
        result = super(SimpleProcessingWrapper, self)._read()
        if result is not None:
            return result
        else:
            return None, processor.STATUS_TERMINATED

    def _write(self, name, data):
        self.outputs[name] = data        
                
class SimpleWriter(object):
    def __init__(self, pe, output, output_mappings):
        self.pe = pe
        self.output = output
        self.output_mappings = output_mappings
    def write(self, result):
        for output_name in result:
            destinations = self.output_mappings[output_name]
            for input_name, comm in destinations:
                for p in comm.destinations:
                    self.output[p] = result[output_name]
     
