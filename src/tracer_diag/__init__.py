"""tracer_diag: read-only on-board diagnostics for a 2022 Yamaha Tracer 9 GT.

Talks to the bike's ISO 19689 6-pin diagnostic socket through an ELM327/STN-class
adapter (primary: OBDLink EX) and an ISO 19689 -> SAE J1962 moulded adapter lead.
See plan/DECISIONS.md for every public interface. Stubs raise NotImplementedError.
"""
__version__ = "0.1.0"
