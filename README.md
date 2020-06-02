### Overview

The challange with this programme is that frame processing was single threaded and FPS performance was limited by the raw Mhz of single core of the CPU. Moreove, there are actually quite a lot of expensive I/O operations, such as network request/response, database operation, filesystem operation and may be GPU inference in the future.
So, the change to this system was to break up the processing into separate threads and begin processing the next frame before the last frame was finished. 
This enables more work to be done on frames without dropping the frame rate so much and also allows more efficient use of a multi-cored system where there might be many, more power efficient but lower performing cores.

This is the Python process that  consists of a set of engines and several controllers for the frame processing pipeline. Each engine or controller runs in its own thread.


## Application engine
The application engine:
- receives the json data based on the image frames from queue buffer
- assesses the detection by checking the plate confidence, the vehicle orientation and filtering wrong plate result for each given json result
- remove the outdated plates list so as to clean the wrong detection results and to avoid other uncertain issues.
- insert key data from the detection result into the sqlite database
- save the image and json result for further review and testing


### Engine component

An engine components is a unit of processing that works on a frame.  
They can be dependant on other components, this is managed by where in the pipeline they are inserted.  
The core engines job is to startup the components and chain them together in the desired order.  
Each engine component gets passed every frame and its the components responsibility to decide if they can process it.  
The engine will start and stop the components as it enters and leaves different states.  
The abstract component is ```BaseQueueEngine```.   
This manages the core structure of the component and supplies the requirements for participating in the core engines architecture.   
Its starts the thread and runs the ```process``` method that each component should implement.

### Frame Grabber

The frame grabber is not an engine per se, but a producer of frames to the pipeline.  
It follows the same interface that the engines do but of course lacks a input queue to receive data.  
It does not inherit from ```BaseQueueEngine```.   
It opens a connection to the camera and starts and stops the stream of data from it to produce frames.

### Frame data


### Preprocessing Engine

This engines responsibility is to track the grey value delta as the frames pass through the pipe.  
It has an exponentially weighted moving average filter to track the grey value and reports that the frames grey value delta is "Okay"


### Openalpr Engine

This engines responsibility is to detect plates in the frame.  I adds the ticket data and coordinates to the frame.

### Json result Testing Engine

This engines responsibility is to read image file and detection result json file from previous saving which is only for easy testing.

###


## Controllers
There are a set of controllers, each with their own responsibilities:
- insert detection result to sqlite database (sqlite_controller)
- save captured images and metadata files to disk (filesystem_controller)
- display a GUI view of the images that are received from the camera (opencv_controller)
- accept commands typed on the keyboard (console_controller)

Controllers exist in the `controllers` subdirectory of the source tree and they all inherit from either the `engine_controller` or `threaded_engine_controller` abstract base classes.

Controllers are initialized in the `main` entry point in `main.py` and are registered to the capture engine's `register_controller()` function.

`EngineController` is the ultimate base class of all controllers and has the following capabilities:
- a reference to the single instance of the application engine.
- a set of `signal` functions that are to be used for posting commands to the capture engine. These work by posting a message to the command queue of the capture engine.
- a set of `notify` functions that are called by the capture engine upon certain events occurring. The notify functions in the base class are empty (no-op) implementations and are designed to be overridden in derived classes.

The above forms an event bus architecture whereby controllers are notified of events (via the `notify` callbacks) and are able to emit events (via the `signal` functions).

`ThreadedEngineController` extends `EngineController` to introduce threading capability.
It overrides the `notify_start` event notification with code to launch a worker thread. The actual implementation of the worker thread must be provided in a `run` function by a derived class.






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

rewrite new main with an application engine and controllers using multiple threads
build pipeline with frame_grabber, frame_data, application_engine: 6 hours
add jsonresult_testing_engine for easy testing
add sqlite engine
convert  sqlite engine to a controller
refactoring engine and controller
add filesystem controller for debugging and backup

add openalpr engine to get other frames' json result from openalpr cloud
add preprocessing engine for denoising and image quality check

refactoring jsonresult_testing_engine for multple frames
only consider one plate in one image for now!! So, 2-3 frames for confirmation is easy to avoid detection

motion blur

todo: what command do we really need??

add log system
add opencv controller for debugging: display the detection area
add console controller and commands for debugging  ??? why need this ??, Yes, so that sometimes we need to stop or frame by frame for debugging, 
and we can also save the image by command??

add shutdown function to end engines and controllers properly 
tidy up code


todo:
sqliteController can be implemented as a db manager with queue for multiple threads insertions.


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