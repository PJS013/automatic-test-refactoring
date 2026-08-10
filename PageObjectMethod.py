from dataclasses import dataclass


@dataclass
class PageObjectMethod:
    class_name: str
    name: str
    body_nodes: list
    args: list