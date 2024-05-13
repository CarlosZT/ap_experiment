from numpy import clip


class MapFun():
    """
    Determina las funciones de mapeo asociadas a alguna característica o parámetro de un estímulo.

    ==Parametros==
    - map_function: Any -> Función utilizada para evaluar el estímulo.

    - activation_bias: float -> Umbral de activación. Determina qué símbolo de activation_symb se utilizará como salida.

    - output_symbols: list -> Simbolos para representar activaciones positivas (primer símbolo) y negativas (segundo símbolo).

    - bias_update_mode: str -> Modo de actualización del valor de bias. 'positive': si se supera el bias este aumentará, en caso opuesto disminuirá. 'negative' igual que el anterior pero inverso. Si no se supera el umbral, este aumentará y viceversa.

    - bias_update_rate: float -> Factor de actualización del bias. Valores pequeños ayudan a que el bias se mantenga 'estable' en el tiempo, pero requiere más repeticiones para cambiar significativamente.

    - bias_limits: tuple -> Limites para el valor del bias. Si no se desean límites, se debe establecer en None. En caso opuesto, se asigna una tupla de flotantes tal que: (limite_inferior, limite_superior).
    """
    def __init__(self,
                map_function,
                activation_bias: float, 
                output_symbols: list = ['1', '0'], 
                bias_update_mode: str = 'activ',
                bias_limits: tuple = None) -> None:
        
        self.map_function: function = map_function
        self.activation_bias: float = activation_bias
        self.output_symbols: list = output_symbols

        self.bias_update_mode: str = bias_update_mode
        self.bias_limits: tuple = bias_limits
        self.bias_update_rate: float = 0.01



    def evaluate(self, input: object)-> str:
        """
        ==Parametros==
        - input: object -> Entrada a evaluar en la función de mapeo. Puede ser cualquier tipo que la propia función admita.

        ==Retorno==
        - str -> Símbolo asociado a la entrada.
        """
        activation:float = self.map_function(input)
        rate = ((activation - self.activation_bias)**2)
        if activation >= self.activation_bias:
            self.update(rate)
            return self.output_symbols[0]
        self.update(-rate)
        return self.output_symbols[1]
    

    
    def update(self, activation:float) -> None:
        match self.bias_update_mode:
            case 'activ':
                self.activation_bias += self.bias_update_rate * activation
            case 'inv_activ':
                self.activation_bias -= self.bias_update_rate * activation
            case 'none':
                return
            case _:
                print(f'Not a valid mode: {self.bias_update_mode}')
 
        
        self.activation_bias = clip(self.activation_bias, self.bias_limits[0], self.bias_limits[1]) if self.bias_limits != None else self.activation_bias
