# pygame-mvctools

MvcTools is a high-level set of Python modules designed for writing games
using the model-controller-view design pattern. It is written on top of Pygame.

The main purpose of this library is to easily design a game as a succession of
states. Each of these states owns its own model, view and controller for which
base classes are provided. Other high level features are available, like
resource handling and automatically updated sprites.

## Requirement

 - Python 2.7
 - Pygame 1.9

## Installation

    $ python setup.py install

## Example

A fully refactored version of
[this game](https://github.com/webshinra/Port-Tales)
is included in the project directory as an example.
Run the following command to launch it:

    $ python run_example.py

## Documentation

A sphinx generated documentation is available
[here](http://vxgmichel.github.io/pygame-mvctools)

## License

pygame-mvctools is licensed under the
[GPLv3](http://www.gnu.org/licenses/gpl-3.0-standalone.html)

## Author

[Vincent Michel](https://github.com/vxgmichel)
