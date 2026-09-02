from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SourceLocation:
    file: str
    line: int
    col: int

@dataclass
class Diagnostic:
    level: str  # "error", "warning", "note"
    message: str
    location: SourceLocation
    # In a full implementation, we might add labels, notes, etc.

class Emitter:
    def __init__(self):
        self.diagnostics: List[Diagnostic] = []
        self.has_error = False

    def emit(self, diagnostic: Diagnostic):
        self.diagnostics.append(diagnostic)
        if diagnostic.level == "error":
            self.has_error = True

    def error(self, message: str, location: SourceLocation):
        self.emit(Diagnostic("error", message, location))

    def warning(self, message: str, location: SourceLocation):
        self.emit(Diagnostic("warning", message, location))

    def note(self, message: str, location: SourceLocation):
        self.emit(Diagnostic("note", message, location))

    def format(self) -> str:
        out = []
        for d in self.diagnostics:
            out.append(f"{d.level}: {d.message}")
            out.append(f" --> {d.location.file}:{d.location.line}:{d.location.col}")
            # In a full implementation, we would show the source line and a caret
            out.append("")
        return "\n".join(out)