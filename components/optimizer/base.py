import abc
from common.minimodel import Plan



class BaseOptimizer(metaclass=abc.ABCMeta):
    """
    Base class for all Optimizer components.
    Each optimizing algorithm needs to implement the following methods:

    schedule: methods that triggers the formation of the plan
    get_visits: methods that updates the plan 

    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'schedule') and
                callable(subclass.schedule) and
                hasattr(subclass, 'add') and
                callable(subclass.add) and
                hasattr(subclass, 'get_visits') and
                callable(subclass.get_visits) and
                hasattr(subclass, '_run') and
                callable(subclass, '_run'))

    @property
    def get_visits(self):
        return self._visits

    @abc.abstractmethod
    def schedule(self) -> Plan:
        plan = Plan()
        while not plan.is_full():
            self._run(plan)
        return plan
    
    @abc.abstractmethod
    def _run(self):
        ...
