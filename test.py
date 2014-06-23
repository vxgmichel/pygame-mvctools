from mvc.control import BaseControl
from examples.loadingscreen import LoadingState

class Test(BaseControl):
    first_state_type = LoadingState
    ressource_dir = "resource"

    
if __name__ == "__main__":
    Test().run()
