"""Exception and warning types (D-010). Implemented at planning time: pure declarations."""


class DiagError(Exception):
    """Base class for every tracer_diag error."""


class AdapterNotFound(DiagError):
    """The serial device path does not exist or cannot be opened."""


class AdapterNoResponse(DiagError):
    """The adapter did not return a '>' prompt within the timeout."""


class ProtocolError(DiagError):
    """The adapter or vehicle returned an error or malformed response."""


class NoData(DiagError):
    """The vehicle returned 'NO DATA' (ECU silent or service/PID unsupported)."""


class UnsupportedPid(DiagError):
    """A PID has no decoder in tracer_diag.pids."""


class UnsafeCommand(DiagError):
    """A command was refused by the read-only allowlist (tracer_diag.safety)."""


class LowVoltageWarning(UserWarning):
    """Adapter-measured supply voltage below LOW_VOLTAGE_THRESHOLD (D-014)."""
