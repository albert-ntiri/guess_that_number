import pytest
from main.resources.infrastructure.number import Number, Validator



class ObjectManagerFake:
    def __init__(self):
        self._object_dict = {"obj_mgr": self}
    
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
        
        self.add_object(obj_name, obj)
        
        return obj
    
    def add_object(self, obj_name, obj):
        self._object_dict[obj_name] = obj

@pytest.fixture
def objects_fake():
    objects = ObjectManagerFake()
    yield objects
    objects._object_dict.clear()

@pytest.fixture
def numbers_copy():
    return Number()


# Test get_object method
def test_get_object_found(objects_fake):
    assert objects_fake == objects_fake.get_object("obj_mgr")

def test_get_object_not_found(objects_fake):
    assert None == objects_fake.get_object("object_manager")


# Test add_object method
def test_add_object_original_length(objects_fake):
    assert 1 == len(objects_fake._object_dict)

def test_add_object_new_length(objects_fake, numbers_copy):
    objects_fake.add_object("numbers", numbers_copy)
    assert 2 == len(objects_fake._object_dict)

def test_add_object_correct_object_added(objects_fake, numbers_copy):
    objects_fake.add_object("numbers", numbers_copy)
    assert numbers_copy == objects_fake._object_dict["numbers"]


# Test create_object method
def test_create_object_no_args(objects_fake):
    num = objects_fake.create_object(Number, "num", ObjectManagerFake)
    assert True == isinstance(num, Number)

def test_create_object_text_display_existing_none(objects_fake):
    objects_fake.create_object(Number, "text_display", ObjectManagerFake)
    assert None == objects_fake.create_object(Validator, "text_display", ObjectManagerFake)

def test_create_object_text_display_does_not_replace(objects_fake):
    objects_fake.create_object(Number, "text_display", ObjectManagerFake)
    objects_fake.create_object(Validator, "text_display", ObjectManagerFake)
    text_display = objects_fake.get_object("text_display")
    assert False == isinstance(text_display, Validator)

def test_create_object_text_display_original_still_exists(objects_fake):
    objects_fake.create_object(Number, "text_display", ObjectManagerFake)
    objects_fake.create_object(Validator, "text_display", ObjectManagerFake)
    text_display = objects_fake.get_object("text_display")
    assert True == isinstance(text_display, Number)


