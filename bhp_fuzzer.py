from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator
from java.util import List, ArrayList
import random


class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.registerIntruderPayloadGeneratorFactory(self)
        return

    @staticmethod
    def getGeneratorName():
        return "BHP Payload Generator"

    def createNewInstance(self, attack):
        return BHPFuzzer(self, attack)


class BHPFuzzer(IIntruderPayloadGenerator):
    def __init__(self, extender, attack):
        self._extender = extender
        self._helpers = extender._helpers
        self._attack = attack
        print("BHP Fuzzer initialized")
        self.max_payloads = 1000
        self.num_payloads = 0

        return

    def hasMorePayloads(self):
        print("hasMorePayloads called.")
        if self.num_payloads == self.max_payloads:
            print("No hay mas payloads.")
            return False
        else:
            print("Mas payloads. Continuando.")
            return True

    def getNextPayload(self, current_payload):

        # convirtiendo a string
        payload = "".join(chr(x) for x in current_payload)

        # llamamos nuestro simple mutador para hacer fuzz en el POST
        payload = self.mutate_payload(payload)

        # incrementamos el numero de intentos de fuzzing
        self.num_payloads += 1
        return payload

    def reset(self):
        self.num_payloads = 0
        return

    @staticmethod
    def mutate_payload(original_payload):
        # escogemos un mutador simple
        picker = random.randint(1, 3)

        # seleccionamos un offset aleatorio en la payload para mutar
        offset = random.randint(0, len(original_payload) - 1)
        payload = original_payload[:offset]

        # offset aleatorio para insertar un intento de inyeccion SQL aleatorio
        if picker == 1:
            payload += "'"

            # jam an XSS attempt in
        if picker == 2:
            payload += "<script>alert('BHP!');</script>"

            # repeat a chunk of the original payload a random number
        if picker == 3:
            chunk_length = random.randint(len(payload[offset:]),
                                          len(payload) - 1)
            repeater = random.randint(1, 10)
            for i in range(repeater):
                payload += original_payload[offset:offset + chunk_length]

        # agregamos los bits restantes de la payload
        payload += original_payload[offset:]
        return payload
