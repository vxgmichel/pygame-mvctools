from mvc.control import BaseControl
from examples.loadingscreen import LoadingState, LoadingModel
from examples.menuscreen import MenuState, MenuModel

class Test(BaseControl):
    first_state_type = LoadingState
    ressource_dir = "resource"

LoadingModel.next_state = MenuState
MenuModel.state_dct["Play"] = LoadingState
MenuModel.state_dct["Settings"] = MenuState
MenuModel.state_dct["Credits"] = MenuState
MenuModel.state_dct["Quit"] = None
    
if __name__ == "__main__":
    Test().run()
