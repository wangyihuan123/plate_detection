





------------------------

Ver 0.2

All the controller => debugger: opencv, terminal, filesystem 

todo: 
pipeline framework
every second
handful 2-3 frames
send them!!
log
py2 => py3
dynamic pipeline:


build pipeline with frame_grabber, frame_data, application_engine
add jsonresult_testing_engine for easy testing
add sqlite engine
convert  sqlite engine to a controller
refactoring engine and controller
add filesystem controller for debugging and backup



add openalpr engine to get other frames' json result from openalpr cloud

refactoring jsonresult_testing_engine for multple frames


add opencv controller for debugging
add console controller and commands for debugging
build dynamic pipeline frame work


add shutdown function to end engines and controllers properly 
add log system
tidy up code




using cascade pipeline framework, so that each engine can be implemented as a more efficient unit in the future, 
such as fork a process, using concurrent.future, invoke a build c/c++ lib



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