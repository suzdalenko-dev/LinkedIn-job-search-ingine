from functions.a_open_brouser import (open_brouser, )
from functions.general import (click_text_button, )



PAGE = open_brouser()

click_text_button(PAGE, 'Mostrar todo')


while True:
    PAGE.wait_for_timeout(1000)