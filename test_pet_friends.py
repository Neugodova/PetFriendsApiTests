from api import PetFriends
from settings import valid_email, valid_password, incorrect_email, incorrect_password
import os

pf = PetFriends()


def test_api_key_for_valid_user(email=valid_email, password=valid_password):
    # Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key

    # Отправляем запрос и сохраняем полученный ответ с кодом ст
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


def test_all_pets_with_(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
       Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
       запрашиваем список всех питомцев и проверяем что список не пустой.
       Доступное значение параметра filter - 'my_pets' либо '' """

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # в status кладем код ответа от сервера, в result кладем список всех животных
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_photo_correct(name='Крысепупик Профессор', animal_type='крысёнок', age='26',
                                       pet_photo='images/1234.jpeg'):
    # Проверяем, что можно добавить питомца c всеми обязательными параментрами.

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert name == result['name']


def test_add_photo_of_pet_correct(pet_photo='images/1234.jpeg'):
    # Проверяем что можно добавить фото к имеющимуся питомцу в формате jpeg

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key, запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Если список не пустой, то пробуем добавить фото к выбраному питомцу
    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo_of_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['pet_photo'] is not None
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception('У вас нет животных')


def test_successful_delete_my_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3")
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'], [1], ['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_update_successful_pet_info(name='ааа', animal_type='ааа', age=2):
    """Проверяем возможность обновления питомца"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        assert status == 200
        assert result['name'] == name
    else:
        raise Exception('У вас нет животных')


def test_api_key_with_incorrect_email(email=incorrect_email, password=valid_password):
    # Проверяем что запрос api ключа возвращает статус 400 и в результате пусто

    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_api_key_with_incorrect_password(email=valid_email, password=incorrect_password):
    # Проверяем что запрос api ключа возвращает статус 400 и в результате пусто

    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


# Условие: что у этого пользователя есть добавленные питомцы
def test_my_pets_have_0_pet(filter='my_pets'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter='my_pets')
    assert status == 200
    assert len(result['pets']) != 0


# Условие: что у этого пользователя есть добавленные питомцы
def test_my_pets_have_min_1_pet(filter='my_pets'):
    # Проверяем, что фильтр 'my_pets' выводит только животных данного пользователя

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter='my_pets')

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_some_empty_values(name='', animal_type='', age='', pet_photo='images/4600311.png'):
    # Проверяем, что можно добавить питомца с пустыми данным, кроме фото животного

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['pet_photo'] is not None


def test_add_new_pet_without_photo_negative(name='', animal_type='', age=''):
    # Баг. Проверяем, что можно добавить питомца с корректными данным, но без обязательного параметра фото, также мы знаем что age = int по документации

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    assert status == 200
    assert result['name'] == name


def test_add_new_pet_with_negative_age(name='Кот', animal_type='Кот', age='-1', pet_photo='images/4600311.png'):
    # Баг. Проверяем, что можно добавить питомца с отрицательным возрастом. Ожидаем 200, так как знаем об этом баге

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['age'] == age


def test_add_pet_with_four_digit_age(name='КОТ', animal_type='cat', age='12345', pet_photo='images/cat.jpg'):
    # Баг. Добавление питомца с числом более трех знаков в переменной age

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    count = result['age']
    assert len(count) == 5

def test_add_photo_of_pet_negative_with_jpg(pet_photo='images/cat.jpg'):
    # Баг. Проверяем, что можно добавить фото к имеющимуся питомцу в формате jpg, ожидаем 200, но по факту добавить фото нельзя если уже оно есть нельзя
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo_of_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)

        assert status == 200
        assert result['pet_photo'] is not None
    else:
        raise Exception('У вас нет животных')


def test_update_negative_pet_(name= '111', animal_type='111', age='vfff'):
    # Баг. Проверяем возможность обновления питомца c age = str. По документации: age = int

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        assert status == 200
        assert result['name'] == name
    else:
        raise Exception('У вас нет животных')
