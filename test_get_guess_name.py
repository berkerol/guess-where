from guess_where import get_guess_name


def test_get_guess_name_city_as_last_directory_without_subdirectories():
    assert get_guess_name('Bayern/München/IMG_20180404_180516.jpg') == 'München'


def test_get_guess_name_city_as_last_directory_with_subdirectories():
    assert get_guess_name('Bayern/München/Deutsches Museum/IMG_20180823_122349.jpg') == 'München'


def test_get_guess_name_city_as_last_element_without_subdirectories():
    assert get_guess_name('2022-01-30 - 1 - Bayern - Nürnberg/IMG_20220130_112607.jpg') == 'Nürnberg'


def test_get_guess_name_city_as_last_element_with_subdirectories():
    assert get_guess_name('2022-08-20 - 1 - Bayern - Ingolstadt/Audi Museum/IMG_20220820_134031.jpg') == 'Ingolstadt'
