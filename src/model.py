from ap_experiment.src.dfa import Automata
class Layer():
    def __init__(self, automata:Automata = None,
                autobuild_buffer:int = None,
                base_layer:bool = True,
                use_quad:bool = False) -> None:
        
        self.is_base_layer:bool = base_layer
        if automata == None:
            if autobuild_buffer == None:
                raise Exception('Layer must have an automata. Provide an Automata object or set autobuild_buffer to the input size for enable autobuild.')
            else:
                automata = Automata()
                automata.autobuild(autobuild_buffer, use_quad=use_quad)

        self.automata:Automata = automata
        self.input_buffer:list = []

        if automata.input_size != None:
            self.buffer_size:int = self.automata.input_size
        else:
            raise Exception('Automata must have defined an input size')
        
        self.output:list
        self.id:str = 'lyr_' + str(self)[-16:-1]
        

    def add_input(self, input:list)->None:
        for s in input:
            self.input_buffer.append(s)
            if len(self.input_buffer) == self.buffer_size:
                r:tuple = self.automata.run(self.input_buffer)
                self.input_buffer = []
                if not r[1]:
                    print(f'>Execution failed at {self.id}.')
                    return
                
                self.output = r[0]


class Model():
    def __init__(self) -> None:
        self.layers:list = []
        self.id:str = 'model_' + str(self)[-16:-1]
        self.output: list
        self.path_logs: list

        self.feedback_rate:float = 0.1 #How fast the agent learns
        self.mitigation_rate:float = 0.001 #How fast the agent forgets

        self.pa_neutral:float = 0.3 #Neutral value for pa
        self.na_neutral:float = 0.3 #Neutral value for na

    def add_layer(self, autobuild_buffer:int = 0)->None:
        
        layer:Layer = Layer(autobuild_buffer=autobuild_buffer,
                             use_quad=len(self.layers) > 0)

        self.layers.append(layer)
        print(f'>Layer {layer.id} added at position {self.layers.index(layer)}')

    def clear_outputs(self)->None:
        for layer in self.layers:
            layer.output = None


    def get_values(self, input:list)->None:
        if len(self.layers)==0:
            raise Exception('No layers available in the model.')
        value:list = []

        self.clear_outputs()
        
        l:Layer = self.layers[0]

        if len(input) != l.buffer_size:
            raise Exception('First input must be equals to layer\'s buffer size')
        
        self.path_logs = []
        
        l.add_input(input)
        response:list = l.output[-1][1]
        self.path_logs.append(l.output)
        
        value.append(response)
        symbol = self.interpreter(response)

        for layer in self.layers[1:]:
            layer.add_input(symbol)
            if layer.output == None:
                break
            response:list = layer.output[-1][1]
            value.append(response)
            symbol = self.interpreter(response)

        self.output = value
        print(f'>Model execution finished: {value}')

            
    def interpreter(self, response:list)->str:
        pa, na = response
        bias = 0.5

        if pa >= bias:
            if na >= bias:
                return '0'
            else:
                return '1'
        else:
            if na >= bias:
                return '2'
            else:
                return '3'
        # return '1' if pa>=na else '0'
    
    def clip(self, value:float, max:float, min:float):
        value = max if value >= max else value
        return min if value <= min else value
    

    def apply_gradient(self, feedback:tuple, verbose:bool = False)->None:
        print(f'>Updating responses for {feedback[0]}')
        #feedback shape: [[node1, node2, node3...], [gradient_pa, gradient_na]]
        
        
        labels:list = feedback[0]
        gradients: list = feedback[1]
        if verbose: print(f'>Gradients: {gradients}')
        i = 0

        for layer in self.layers:
            i+=1
            checked:list = []
            for terminal in layer.automata.terminal_nodes:

                pa, na = layer.automata.responses[terminal.name]

                if terminal.name in labels:
                    print(f'\nLyr[{i}]>Adjusting: {terminal.name}')
                    # if verbose: print('__activated__')
                    if verbose: print(f'>From: {[pa, na]}')

                    checked.append(terminal.name)
                    pa = pa - gradients[0] * self.feedback_rate
                    na = na - gradients[1] * self.feedback_rate
                    if verbose: print(f'>To: {[pa, na]}')

                    
                else:
                    pa = pa - (pa - self.pa_neutral) * self.mitigation_rate
                    na = na - (na - self.na_neutral) * self.mitigation_rate

                pa = self.clip(pa, 1, 0)
                na = self.clip(na, 1, 0)
            
                layer.automata.responses[terminal.name] = [pa, na]


            for l in checked: #To simplify
                labels.remove(l)

            




        # for layer in self.layers:
        #     checked: list = []
        #     for label in labels:
        #         if label in layer.automata.responses:
        #             checked.append(label)
        #             pa, na = layer.automata.responses[label]
        #             print(f'>From: {[pa, na]}')
        #             pa = pa - gradients[0] * self.feedback_rate
        #             na = na - gradients[1] * self.feedback_rate

        #             pa = self.clip(pa, 1, 0)
        #             na = self.clip(na, 1, 0)

        #             print(f'>To: {[pa, na]}')

        #             layer.automata.responses[label] = [pa, na]
                
        #     for l in checked:
        #         labels.remove(l)
        # print('>Gradients applied')
                    



