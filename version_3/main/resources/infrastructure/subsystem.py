"""
The subsystem.py module is part of the infrastructure package.  It contains a set of 2 classes that serve
as an abstraction for a subsystem that is widely used across the app.  In this subsystem, a collection of
classes are inherited from a base class and together compose a manager class.  That manager class runs a
standardized method for all concrete subclasses of that base class.  This allows for a collection of objects
to be updated in one action, using a standardized method.  The modules that use this subsystem include:
    game_stats.py
    user_metrics.py
    concept_manager.py
    math_concept.py
    application_analytics.py
    data.py
    application_text.py
    text_displayers.py
    log.py

Classes:
    BaseClass
    Manager
"""


class BaseClass:
    """
    The BaseClass class is the base class used within a subsystem.  Each class that serves as a base class
    inherits the BaseClass class.  It contains 2 attributes that are defined in this class and implemented
    by the concrete subclasses of the BaseClass class.
    
    Attributes:
        _obj_id_method: An unexecuted method that identifies the specific subclass of the base class.
        _standardized_method: An unexecuted method that represents the standardized method shared among all subclasses of
            the base class.
    """
    
    def __init__(self):
        self._obj_id_method = None
        self._standardized_method = None



class Manager:
    """
    The Manager class serves as the manager within a subsystem.  Its main role is to run the standardized
    method of the appropriate subclass of the base class.  The subclasses of the Manager class instantiate
    all of the subclasses of the base class and saves them as attributes.  It also has the base class
    as an attribute.
    
    Attributes:
        _base_class: The class that serves as the base class for the subsystem.
        _subclass_list: A list of objects of the subclasses of the base class.
        _subclass_dict: A dictionary of objects of the subclasses of the base class.
    """
    
    def __init__(self, base_class):
        self._base_class = base_class
        self._subclass_list = self.get_class_instances(self._base_class)
        self._subclass_dict = self._get_class_instance_dict()
    
    def run_all_subclass_methods(self, *args):
        results = []
        for subclass_obj in self._subclass_list:
            obj_result = subclass_obj._standardized_method(*args)
            results.append(obj_result)
        
        return results
    
    def run_subclass_method(self, object_id, *args):
        class_instance = self.get_subclass_obj(object_id)
        result = class_instance._standardized_method(*args)
        return result
    
    def get_subclass_obj(self, object_id):
        for class_instance in self._subclass_list:
            if class_instance._obj_id_method() == object_id:
                return class_instance
    
    def get_class_instances(self, target_class):
        attributes = list(self.__dict__.values())
        class_instances = [attr for attr in attributes if isinstance(attr, target_class)]
        return class_instances
    
    def _get_class_instance_dict(self):
        class_instance_dict = {instance._obj_id_method(): instance for instance in self._subclass_list}
        return class_instance_dict