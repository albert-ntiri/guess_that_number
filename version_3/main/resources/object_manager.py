"""
The object_manager.py module is part of the resources package.  It is for creating and accessing objects
of many of the commonly-used classes in the app.

Classes:
    ObjectManager
"""


from resources.infrastructure.log import LogFactory
from resources.infrastructure.number import Number
from resources.infrastructure.application_text import TextManager
from resources.infrastructure.data import DataManager
from resources.infrastructure.log_entries import ClassLogEntry
from app_data.data_storers.session import Session
from app_data.analytics.application_analytics import AnalyticsManager
from app_data.db import DBManager



class ObjectManager:
    """
    The ObjectManager class is a centralized location for commonly-accessed objects throughout the app.
    """
    
    def __init__(self, app):
        self._logs = LogFactory()
        
        self._object_dict = {"app": app, "obj_mgr": self, "logs": self._logs}
        
        self._numbers = self.create_object(Number, "numbers", ObjectManager)
        self._text = self.create_object(TextManager, "text", ObjectManager)
        self._data = self.create_object(DataManager, "data", ObjectManager, self._text)
        self._db_manager = self.create_object(DBManager, "db_manager", ObjectManager, self._numbers, self._data, self._logs)
        self._session = self.create_object(Session, "session", ObjectManager, self)
        if self._session.get_session_count() >= 10:
            self._analytics = self.create_object(AnalyticsManager, "analytics", ObjectManager, self)
    
    def get_object(self, obj_name):
        try:
            return self._object_dict[obj_name]
        except KeyError:
            return
    
    def create_object(self, class_name, obj_name, instantiator, *args):
        if obj_name == "text_display":
            if obj_name in self._object_dict:
                return
        
        obj = class_name(*args)
        class_log_entry = ClassLogEntry(self._logs, class_name.__name__, obj_name, instantiator.__name__)
        class_log_entry.add_log_entry("class")
        
        self.add_object(obj_name, obj)
        
        return obj
    
    def add_object(self, obj_name, obj):
        self._object_dict[obj_name] = obj