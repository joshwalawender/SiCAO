# pypaca

Pypaca is a simple python wrapper around the [ASCOM Alpaca](https://ascom-standards.org/Developer/Alpaca.htm) REST [API](https://ascom-standards.org/api/#/).

Each Alpaca device type has an object associated with it which has the GET and PUT methods translated to methods on the object.  Some GET methods which are static and don't change on a given connection, may not be implemented as methods, but rather are queried once at instantiation and the result is stored as a property of the object.

Objects may have a few convenience methods designed for interoperability with another project in addition to the standard Alpaca methods.

