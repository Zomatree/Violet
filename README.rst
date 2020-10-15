Violet
======
A statically typed, interpreted language in Python.

⚠️ This language is still a work in progress, and mostly just a learning experience. ⚠️

Sample "Hello World" example:

.. code-block:: none

   import { io } from std;

   fun main(argv: List[String]) {
       let a = io.out.write("Hello, world!\n");
   };

Other examples can be found in the `examples/` directory.

Clone the repo, and use `python -m violet <file>` to invoke the interpreter.