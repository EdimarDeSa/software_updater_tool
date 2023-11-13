from dataclasses import dataclass


@dataclass(frozen=True)
class ViewSettings:
    bg: str = '#66d867'
    font: str = 'Arial 10 bold'
