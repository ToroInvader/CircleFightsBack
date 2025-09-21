from collections import  defaultdict

class Component:
    def __init__(self, ctype):
        self.type = ctype


class Remove(Component):

    def __init__(self):
        super().__init__("remove")

class ECS:

    def __init__(self):
        self.next_id = 0
        self.entities = set()
        self.components = defaultdict(dict)


    def create_entity(self):
        eid = self.next_id
        self.next_id += 1
        self.entities.add(eid)
        return eid

    def remove_entity(self, eid):
        for component_dict in self.components.values():  # <-- use .values()
            component_dict.pop(eid, None)

    def add_component(self, eid, component: Component):
        self.components[component.type][eid] = component

    def remove_component(self, eid, component:Component):
        self.components[component.type].pop(eid, None)

    def has_component(self, eid, *ctypes):
        for ctype in ctypes:
            if not eid in self.components[ctype].keys():
                return False
        return True


    def get_component(self, eid, ctype):
        return self.components[ctype][eid]


    def query(self, *ctypes):
        """return entity ids that have all given component types"""
        if not ctypes: # I assume this means ctypes is empty
            return set()
        if any(ct not in self.components for ct in ctypes):
            return set()  # bail early if any component type is unknown
        sets = [set(self.components[ct].keys()) for ct in ctypes if ct in self.components]
        if not sets: #we got no sets so the query must've failed
            return set()
        return set.intersection(*sets)



class RemoverSystem:
    def tick(self, ecs: ECS):
        eids = ecs.query("remove")
        for id in eids:
            ecs.remove_entity(id)