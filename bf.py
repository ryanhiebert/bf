from __future__ import print_function
import sys

class Tape(list):
    """A self-expanding integer list."""
    class InvalidValueError(Exception): pass

    def __setitem__(self, key, val):
        if isinstance(key, int):
            if key >= 0 and len(self) <= key:
                self.extend([0] * (key - len(self) + 1))
            if not 0 <= val <= 255:
                raise Tape.InvalidValueError('Tape values must be 0-255')
        else:
            for val in val:
                if not 0 <= val <= 255:
                    raise Tape.InvalidValueError('Tape values must be 0-255')
        list.__setitem__(self, key, val)

    def __getitem__(self, key):
        if isinstance(key, int) and key >= 0 and len(self) <= key:
            self.extend([0] * (key - len(self) + 1))
        return list.__getitem__(self, key)


class BrainFuck(str):
    """
    Represents a BrainFuck program. Automatically removes any
    unneeded characters, typically used as commandments.
    """
    class MismatchedLoopError(Exception): pass
    class InvalidValueError(Exception): pass
    class InterpreterError(Exception): pass

    def __new__(cls, object=''):
        """
        Clean the input string of unneeded characters for
        a BrainFuck program.
        """
        ret = str.__new__(cls, ''.join(l for l in str(object) if l in '+-<>.,[]'))
        
        loops = {}
        stack = []
        for i, char in enumerate(ret):
            if char == '[':
                stack.append(i)
            if char == ']':
                try:
                    start = stack.pop()
                except IndexError:
                    raise BrainFuck.MismatchedLoopError('Too many \']\'s')
                loops[start] = i
                loops[i] = start
        if stack:
            raise BrainFuck.MismatchedLoopError('Too many \'[\'s')
        
        ret.loops = loops
        return ret

    def run(self, tape=None, input_prompt='', output_prompt=''):
        if not tape:
            tape = Tape()
        instruction = pointer = 0
        program = self
        
        if ',' in program:
            print(input_prompt, end='')

        output = ''

        while instruction < len(program):
            command = program[instruction]
            if command == '+':
                try:
                    tape[pointer] += 1
                except Tape.InvalidValueError:
                    msg = program[:instruction + 1] + ' ** ' + program[instruction + 1:]
                    raise BrainFuck.InvalidValueError(msg)
            if command == '-':
                try:
                    tape[pointer] -= 1
                except Tape.InvalidValueError:
                    msg = program[:instruction + 1] + ' ** ' + program[instruction + 1:]
                    raise BrainFuck.InvalidValueError(msg)
            if command == '<':
                pointer -= 1
            if command == '>':
                pointer += 1
            if command == '.':
                output += chr(tape[pointer])
            if command == ',':
                tape[pointer] = ord(sys.stdin.read(1))
            if command == '[':
                if not tape[pointer]:
                    instruction = program.loops[instruction]
            if command == ']':
                if tape[pointer]:
                    instruction = program.loops[instruction]
            if pointer < 0:
                msg = program[:instruction + 1] + ' ** ' + program[instruction + 1:]
                raise BrainFuck.InterpreterError('Invalid Tape Index at {}'.format(msg))
            instruction += 1

        print('{}{}'.format(output_prompt, output))


if __name__ == '__main__':
    tape = Tape()
    while True:
        try:
            BrainFuck(raw_input('! ')).run(tape, input_prompt='? ')
        except (KeyboardInterrupt, EOFError):
            break
