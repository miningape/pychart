from dataclasses import dataclass

from typing import Any, Callable, Dict, List


class StackFrame:
    memory: List[Any] = []


class VirtualMachine:
    class Stack:
        memory: List[StackFrame] = []

        def __init__(self) -> None:
            self.memory.append(StackFrame())

        def push(self, value: Any):
            # Really bad implementation lol
            frame = self.memory.pop()
            frame.memory.append(value)
            self.memory.append(frame)

        def get_at(self, depth: int, index: int):
            return self.memory[depth].memory[index]

        def get(self, index: int):
            return self.get_at(len(self.memory) - 1, index)

        def set_at(self, depth: int, index: int, value: Any):
            self.memory[depth].memory[index] = value

        def set(self, index: int, value: Any):
            self.set_at(len(self.memory) - 1, index, value)

        def pop(self):
            vals = self.memory.pop()
            return vals.memory[0]

    class Environment:
        memory: Dict[str, Any] = {}

        def create(self, identifier: str):
            self.memory[identifier] = None

        def get(self, identifier: str):
            return self.memory[identifier]

        def set(self, identifier: str, value: Any):
            self.memory[identifier] = value

    bytecodes: List["Bytecode"]
    environment = Environment()
    stack = Stack()
    program_counter = 0

    def __init__(self, bytecodes: List["Bytecode"]):
        self.bytecodes = bytecodes

    def get_instruction(self):
        return self.bytecodes[self.program_counter]

    def increment_pointer(self):
        self.program_counter += 1

    def execute(self, bytecode: "Bytecode"):
        return bytecode.execute(self)


class Bytecode:
    def execute(self, virtual_machine: VirtualMachine) -> Any:
        raise Exception()


class Value:
    def get(self, virtual_machine: VirtualMachine) -> Any:
        raise Exception()

    def set(self, virtual_machine: VirtualMachine, value: Any) -> Any:
        raise Exception()


@dataclass()
class Register(Value):
    name: str

    def get(self, virtual_machine: VirtualMachine) -> Any:
        return virtual_machine.environment.get(self.name)

    def set(self, virtual_machine: VirtualMachine, value: Any) -> Any:
        virtual_machine.environment.set(self.name, value)


@dataclass()
class LiteralValue(Value):
    value: Any

    def get(self, virtual_machine: VirtualMachine) -> Any:
        return self.value

    def set(self, virtual_machine: VirtualMachine, value: Any) -> Any:
        raise Exception("Cannot set literal value")


@dataclass()
class StackValue(Value):
    pos: int

    def get(self, virtual_machine: VirtualMachine) -> Any:
        return virtual_machine.stack.get(self.pos)

    def set(self, virtual_machine: VirtualMachine, value: Any) -> Any:
        virtual_machine.stack.set(self.pos, value)


@dataclass()
class StackFrameValue(Value):
    pos: int
    depth: int

    def get(self, virtual_machine: VirtualMachine) -> Any:
        return virtual_machine.stack.get_at(self.depth, self.pos)


@dataclass()
class Label(Bytecode):
    position: int = -1

    def execute(self, virtual_machine: VirtualMachine) -> Any:
        pass


@dataclass()
class Create(Bytecode):
    identifier: Register

    def execute(self, virtual_machine: VirtualMachine) -> Any:
        virtual_machine.environment.create(self.identifier.name)


@dataclass()
class Push(Bytecode):
    value: Any

    def execute(self, virtual_machine: VirtualMachine) -> Any:
        virtual_machine.stack.push(self.value)


# @dataclass()
# class JumpToSubRoutine(Bytecode):
#     args: List[]


@dataclass()
class BinaryCode(Bytecode):
    description: str
    identifier: Value
    left: Value
    right: Value
    action: Callable[[Any, Any], Any]

    def execute(self, virtual_machine: VirtualMachine) -> Any:
        self.identifier.set(
            virtual_machine,
            self.action(
                self.left.get(virtual_machine), self.right.get(virtual_machine)
            ),
        )


@dataclass()
class Jump(Bytecode):
    label: Label

    def execute(self, virtual_machine: VirtualMachine) -> Any:
        virtual_machine.program_counter = self.label.position


@dataclass()
class JumpIf(Bytecode):
    condition: Value
    label: Label

    def execute(self, virtual_machine: VirtualMachine) -> Any:
        if self.condition.get(virtual_machine):
            virtual_machine.program_counter = self.label.position


@dataclass()
class JumpIfNot(Bytecode):
    condition: Value
    label: Label

    def execute(self, virtual_machine: VirtualMachine) -> Any:
        if not self.condition.get(virtual_machine):
            virtual_machine.program_counter = self.label.position


def bytecode_interpreter(bytecodes: List[Bytecode]):
    vm = VirtualMachine(bytecodes)

    while vm.program_counter < len(vm.bytecodes):
        bytecode = vm.get_instruction()

        vm.execute(bytecode)

        vm.increment_pointer()

    print(vm.environment.memory)
    print([frame.memory for frame in vm.stack.memory])
