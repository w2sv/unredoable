# __unredoable__

[![Build](https://github.com/w2sv/unredoable/actions/workflows/build.yaml/badge.svg)](https://github.com/w2sv/unredoable/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/w2sv/unredoable/branch/master/graph/badge.svg?token=9EESND69PG)](https://codecov.io/gh/w2sv/unredoable)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
![PyPI](https://img.shields.io/pypi/v/unredoable)
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)

## Download
```
pip install unredoable
```

## Usage

```python
from unredoable import Unredoable

class StateManager:
    def __init__(self, state_variable):
        """ state_variable may be of whatever type, whether custom or not, 
        the sole restraint it's subject to, is that is needs to implement 
        either __copy__ or __deepcopy__, depending on the passed 
        'craft_deep_copies' parameter """
        
        self.unredoable_state_variable = Unredoable(state_variable, max_stack_depths=10, craft_deep_copies=False)
        
    def alter_state_variable(self):
        self.unredoable_state_variable.push_state()
        
        self.unredoable_state_variable.obj += 1

if __name__ == '__main__':
    manager = StateManager(69)
    
    manager.alter_state_variable()
    manager.alter_state_variable()
    
    manager.unredoable_state_variable.undo()  # unredoable_state_variable = 70
    manager.unredoable_state_variable.redo()  # unredoable_state_variable = 71
```


## Author
Janek Zangenberg

## License
[MIT](LICENSE)
