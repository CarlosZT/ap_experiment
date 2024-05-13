from numpy.random import normal

class Node():
    def __init__(self) -> None:
        self.name: str
        self.next: list = []
        self.prev: Transition
        self.visit_count:int = 0

class Transition():
    def __init__(self) -> None:
        self.name: str
        self.next: Node
        self.prev: Node

class Automata():
    def __init__(self, verbose = False) -> None:

        self.executions:int = 0
        self.root: Node = Node()
        self.root.name = 'root'
        self.terminal_nodes: list = []
        self.responses: dict = {}
        self.verbose = verbose
        self.id:str = 'dfa_' + str(self)[-16:-1]

        self.output:list = []
        self.input_size:int = 0

    def add_response(self, asoc:tuple)->None:
        """
        Función para añadir respuestas. Las respuestas se asocian a etiquetas de nodos y secuencias.
        Es importante recordar que los nodos terminales tienen una etiqueta diferente a la del símbolo que nos permite llegar a él, por lo que usar ese símbolo para añadir respuestas no surtirá efecto en ningún caso.\n
        Las secuencias se utilizan para nodos no terminales.
        ==Parámetros==
        - asoc -> tuple: Tupla que contiene la etiqueta del nodo a reconocer y la respuesta asociadam -> (label, response).
        """
        label:str
        resp:list
        
        label, resp = asoc
        self.responses[label] = resp
        if self.verbose: print(f'>Response added:\n >>Sequence: {label}\n >>Response: {resp}\n')


    def run(self, input:list) -> tuple:
        print(f'>[{self.id}]Running on: {input}')
        n:Node = self.root
        visited:str = ''
        failed: bool
        self.output:list = []
        visited_nodes:list = []
        if self.input_size < len(input):
            print(f'>Input {input} exceeds input size {self.input_size}.')
            slicing = abs(self.input_size - len(input))
            print(f'>Slicing at index {slicing}: {input} -> {input[slicing:]}')
            input = input[slicing:]
        elif self.input_size > len(input):
            print(f'Not enough size input. Provided input size: {len(input)} (input), Required: {self.input_size}')

        for s in input:
            failed = True
            for t in n.next:
                if t.name == s:
                    failed = False
                    n = t.next
                    if self.verbose: 
                        print(f'>Reporting for: {s}')
                        print(f'>Sequence used: {visited}')
                    visited += n.name
                    self.call_response(visited if s == n.name else n.name)
                    visited_nodes.append(n)
            if failed:
                print(f'>Not found a transition for {s}. Breaking execution.')
                return (self.output, False)
        self.executions += 1
        for n in visited_nodes:
            n.visit_count +=1
        return (self.output, True)


    def call_response(self, label:str)->None:
        if label in self.responses.keys(): 
            if self.verbose: print(f'>Calling response for {label}')
            self.output.append((label, self.responses[label]))



    def build(self, words: list, labels: list) -> None:
        """
        Función para construir el autómata. Si no se tienen las cadenas a utilizar pero sí se conoce el tamaño de la entrada, se utiliza el método autobuild.\n
        ==Parametros==
        - words -> list: Lista de cadenas. Las cadenas son listas de símbolos o composiciones de ellos y deben ser únicas.
        - labels -> list: Lista de etiquetas ordenadas respecto a la cadena a la que se asocian.

        """
        print(f'\n===Build started===')
        self.input_size = len(words[0])

        if self.verbose: 
            print(f'>Building automata with following words:')
            for w in words:
                x:str = ''
                for s in w:
                    x += s
                print(f'>>{x}')

            print(f'\n>Labeling with:')
            for l in labels:
                print(f'>>{l}')

        for word in words:
            if self.verbose: print(f'\n>Working with: {word}')
            n: Node = self.root
            for w in word:
                
                if self.verbose: print(f'>Searching transitions for \'{w}\'')
                found = False
                for t in n.next:
                    if t.name == w:
                        found = True
                        if self.verbose: print(f'>Transition found. Accesing next node.')
                        n = t.next
                        break
                if not found:
                    if self.verbose: print(f'>Transition not found, creating...')

                    t_ = Transition()
                    n_ = Node()

                    t_.name = w
                    n_.name = w

                    t_.prev = n
                    t_.next = n_

                    n_.prev = t_                        
                    n.next.append(t_)
                    if self.verbose: print(f'>Accesing new node via: \'{w}\'')
                    n = n_
            label = labels[words.index(word)]
            if self.verbose: print(f'>Naming terminal node \'{label}\' for \'{word}\'\n')
            n.name = label
            self.terminal_nodes.append(n)
            
            asoc = (label, [normal(0.5, 0.1), normal(0.5, 0.1)])
            self.add_response(asoc)


        print('>Automata building finished')
        print(f'>>Terminal nodes: {len(self.terminal_nodes)}')
        if self.verbose: print('>>Print the graph inorder with function print_graph().\n')

    def autobuild(self, n:int, use_quad:bool = False) -> None:
        """
        Función para construir el autómata usando alfabeto binario {0, 1} y etiquetas por defecto. Si se cuentan con las cadenas y las etiquetas, usar en su lugar el método build\n
        ==Parametros==
        - n: int -> Tamaño de la cadena.

        """
        
        pkg = self.q_ary(n) if use_quad else self.binary(n)
        
        self.build(*pkg)


    def binary(self, k:int) -> tuple:
        words: list = []
        labels: list = []
        for n in range(2**k):
            x = str(bin(n))[2:]
            for i in range(k-len(x)):
                x = '0' + x
            words.append(list(x))

        for i in range(len(words)):
            labels.append('S' + str(i+1))
        return (words,labels)
    
    def quad(self, n:int)->str:
        s:str = ''
        q:int = 1
        m:int = 1
        while q > 0:
            q = n // 4
            m = n % 4
            s = str(m) + s
            if q < 4 and q > 0:
                s = str(q) + s
                break
            n = q
        return s

    def q_ary(self, k:int) -> tuple:
        words: list = []
        labels: list = []
        for n in range(4**k):
            x = str(self.quad(n))
            for i in range(k-len(x)):
                x = '0' + x
            words.append(list(x))

        for i in range(len(words)):
            labels.append('S' + str(i+1))
        return (words,labels)
    

    def print_graph(self, node) -> None:
        print(f'>{node.name}')
        for t in node.next:
            node = t.next
            self.print_graph(node)

    