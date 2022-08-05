import pytest
from main.resources.infrastructure.subsystem import *



class BaseClassFake(BaseClass):
    def __init__(self, n):
        self._id = n
        self._obj_id_method = self.get_id
        self._standardized_method = self.get_string
    
    def get_string(self):
        return str(self._id)
    
    def get_id(self):
        return self._id



class ManagerFake(Manager):
    def __init__(self):
        self._one = BaseClassFake(1)
        self._two = BaseClassFake(2)
        self._three = BaseClassFake(3)
        super().__init__(BaseClassFake)



### Manager Tests

@pytest.fixture
def manager_fake():
    return ManagerFake()

@pytest.fixture
def class_instance_list(manager_fake):
    return manager_fake.get_class_instances(BaseClassFake)

@pytest.fixture
def class_instance_dict(manager_fake):
    return manager_fake._get_class_instance_dict()


# Test get_class_instances method
def test_get_class_instances_list(class_instance_list):
    assert True == isinstance(class_instance_list, list)

def test_get_class_instances_correct_length(class_instance_list):
    assert 3 == len(class_instance_list)

@pytest.mark.parametrize("n", [0, 1, 2])
def test_get_class_instances_base_class_object(class_instance_list, n):
    class_instance = class_instance_list[n]
    assert True == isinstance(class_instance, BaseClassFake)

@pytest.mark.parametrize("n", [0, 1, 2])
def test_get_class_instances_correct_id(class_instance_list, n):
    class_instance = class_instance_list[n]
    assert n + 1 == class_instance.get_id()

def test_get_class_instances_no_arguments_raises_error(manager_fake):
    with pytest.raises(TypeError):
        manager_fake.get_class_instances()

def test_get_class_instances_too_many_arguments_raises_error(manager_fake):
    with pytest.raises(TypeError):
        manager_fake.get_class_instances(BaseClassFake, "extra")


# Test _get_class_instance_dict method
def test_get_class_instance_dict_dict(class_instance_dict):
    assert True == isinstance(class_instance_dict, dict)

def test_get_class_instance_dict_correct_length(class_instance_dict):
    assert 3 == len(class_instance_dict)

@pytest.mark.parametrize("n", [1, 2, 3])
def test_get_class_instance_dict_base_class_object(class_instance_dict, n):
    class_instance = class_instance_dict[n]
    assert True == isinstance(class_instance, BaseClassFake)

def test_get_class_instance_dict_too_many_arguments_raises_error(manager_fake):
    with pytest.raises(TypeError):
        manager_fake._get_class_instance_dict(BaseClassFake, "extra")


# Test get_subclass_obj method
@pytest.mark.parametrize("n", [1, 2, 3])
def test_get_subclass_obj_base_class_object(manager_fake, n):
    subclass_obj = manager_fake.get_subclass_obj(n)
    assert True == isinstance(subclass_obj, BaseClassFake)

@pytest.mark.parametrize("n", [1, 2, 3])
def test_get_subclass_obj_correct_id(manager_fake, n):
    subclass_obj = manager_fake.get_subclass_obj(n)
    assert n == subclass_obj.get_id()

def test_get_subclass_obj_not_found(manager_fake):
    assert None == manager_fake.get_subclass_obj(4)

def test_get_subclass_obj_no_arguments_raises_error(manager_fake):
    with pytest.raises(TypeError):
        manager_fake.get_subclass_obj()

def test_get_subclass_obj_too_many_arguments_raises_error(manager_fake):
    with pytest.raises(TypeError):
        manager_fake.get_subclass_obj(1, "extra")


# Test run_subclass_method method
@pytest.mark.parametrize("n", [1, 2, 3])
def test_run_subclass_method(manager_fake, n):
    assert str(n) == manager_fake.run_subclass_method(n)

def test_run_subclass_method_no_arguments_raises_error(manager_fake):
    with pytest.raises(TypeError):
        manager_fake.run_subclass_method()


# Test run_all_subclass_methods method
def test_run_all_subclass_methods(manager_fake):
    assert ["1", "2", "3"] == manager_fake.run_all_subclass_methods()



