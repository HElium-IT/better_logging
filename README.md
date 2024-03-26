# python_logger_module

There is a Main logger that has only one QueueHandler that handles the records in a separate thread.

All the other loggers are in propagate-mode and have their handler NOT REGISTERED, their handlers gets registered inside the MainQueueHandler: this should be done in the __init__.py script of the loggers module.

More over, the queue can activate handlers only when the records come from a certain logger (passing a list of loggers to the "add_handler_to_queue" main_logger function)

You probably need to change the imports.
