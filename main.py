import monkeytype
import sys
from lib import foo, nonint
from types import CodeType, FrameType
from typing import Any
from valuetypes import int8, int16, int32, int64


def get_type(obj, max_typed_dict_size) -> type:
    if type(obj) is not int:
        return monkeytype.tracing.get_type(obj, max_typed_dict_size)
    for ty in (int8, int16, int32, int64):
        if -(2**ty.width) <= obj <= 2**ty.width - 1:
            return ty
    return int


class ValueTracer(monkeytype.tracing.CallTracer):
    def handle_call(self, frame: FrameType) -> None:
        func = self._get_func(frame)
        if func is None:
            return
        code = frame.f_code
        # I can't figure out a way to access the value sent to a generator via
        # send() from a stack frame.
        if frame in self.traces:
            # resuming a generator; we've already seen this frame
            return
        arg_names = code.co_varnames[0 : code.co_argcount]
        arg_types = {}
        for name in arg_names:
            if name in frame.f_locals:
                arg_types[name] = get_type(
                    frame.f_locals[name], max_typed_dict_size=self.max_typed_dict_size
                )

        self.traces[frame] = monkeytype.tracing.CallTrace(func, arg_types)

    def handle_return(self, frame: FrameType, arg: Any) -> None:
        # In the case of a 'return' event, arg contains the return value, or
        # None, if the block returned because of an unhandled exception. We
        # need to distinguish the exceptional case (not a valid return type)
        # from a function returning (or yielding) None. In the latter case, the
        # the last instruction that was executed should always be a return or a
        # yield.
        typ = get_type(arg, max_typed_dict_size=self.max_typed_dict_size)
        last_opcode = frame.f_code.co_code[frame.f_lasti]
        trace = self.traces.get(frame)
        if trace is None:
            return
        elif last_opcode == monkeytype.tracing.YIELD_VALUE_OPCODE:
            trace.add_yield_type(typ)
        else:
            if last_opcode == monkeytype.tracing.RETURN_VALUE_OPCODE:
                trace.return_type = typ
            del self.traces[frame]
            self.logger.log(trace)


if __name__ == "__main__":
    config = monkeytype.config.DefaultConfig()
    logger = config.trace_logger()
    tracer = ValueTracer(
        logger=logger,
        max_typed_dict_size=config.max_typed_dict_size(),
    )
    sys.setprofile(tracer)
    for i in range(100):
        foo(3)
        nonint("hello")
    sys.setprofile(None)
    logger.flush()
