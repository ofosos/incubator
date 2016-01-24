#!/usr/bin/env python2

from __future__ import unicode_literals, print_function
from pypeg2 import *
from struct import pack

class Comment(str):
    grammar = re.compile(r"^;.*")

class FinalStep(Keyword):
    grammar = Enum( K("finoff"), K("finstay") )

class ParameterType(Keyword):
    grammar = Enum( K("temp"), K("duration") )

class Parameter(str):
    grammar = attr("name", ParameterType), "=", re.compile(r"[^;]+"), ";"

class Step(Namespace):
    grammar = "(", some(Parameter), ")"

class Preset(List):
    grammar = name(), "{", "name", "=", attr("stepName", re.compile(r"[^;]+")), ";", attr("finalStep", FinalStep), ";", "steps", some(Step), "}"

class Version(str):
    grammar = "version", "=", word, ";"

class PresetList(List):
    grammar = ignore(maybe_some(Comment)), attr("version", Version), some(Preset)

content = parse(open('test.eet', 'r').read(), PresetList, filename='test.eet')

out = open('test.eep', 'w')

print("EEPROM Version: %s" % content.version)
out.write(pack('>h', int(content.version)))

for preset in content:
    print("\nStepname: %s" % (preset.stepName))
    out.write(pack('16s', preset.stepName))

    print("Finally: %s" % (preset.finalStep))
    fstep = 0
    if preset.finalStep == "finstay":
        fstep = 1

    out.write(pack('B', (len(preset) << 4) | fstep))

    for step in preset:
        print("== step temp=%s duration=%s" % (step['temp'], step['duration']))
        out.write(pack('bBBB', int(step['temp']),
                       (int(step['duration']) >> 16) & 255,
                       (int(step['duration']) >> 8) & 255,
                       int(step['duration']) & 255))
