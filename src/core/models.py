from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class RobloxInstance:
        return {
            'ClassName': self.class_name,
            'Name': self.name,
            'Properties': self.properties,
            'Children': [child.to_dict() for child in self.children]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RobloxInstance':
        for child in self.children:
            if child.name == name:
                return child
        return None
    
    def find_children_by_class(self, class_name: str) -> List['RobloxInstance']:
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants


@dataclass
class RojoProject:
        return {
            'name': self.name,
            'tree': self.tree
        }
