
-------------------------

Ver 0.1  
This is the first version which is quite simple and naive, since this application is built from scatch. 

## About the current code
`test_scripts` contains all the simple script when I tried basic functions of sqlite, openalpr and video.
`running_data` is my running cache which saved the temporary json result and frame image for easy testing and debugging purpose.
`test_data` contains the test image file and video file.
main.py 

## TODO:
 - Currently, this app is a single main file with one for loop. So, multiple threads for I/O operation is urgent to be implemented.
 - Concurrency should be considered as well.
 - Object oriented style
 - sqlite and openalpr cloud api can be encapsulated more elegantly.
 - A lot of scenarios haven't been considered: e.g., multiple car/plates, dark/rain/fog/bad condition, robustness, etc.