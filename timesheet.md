have a glance at the paper
 
check the openALPR website and their GitHub
try openalpr api via docker(https://github.com/openalpr/openalpr)

create a condo env(py3.6) for this project
install opencv via pip
install matplotlib, numpy and other libs on conda(optional)

write a simple loop to capture every frame and display  from the test video for the first start.

install/compile openalpr(https://github.com/openalpr/openalpr/wiki/Compilation-instructions-(Ubuntu-Linux)) and tesseract-ocr(https://tesseract-ocr.github.io/tessdoc/Home.html)
But, failed on alpr -c us ea7the.jpg (https://github.com/openalpr/openalpr/wiki/Compilation-instructions-(Ubuntu-Linux)), seem tesseract or lib installation not complete

try docker way to test openalpr for now, althoug it is 

install sqlite and sqlite-browser
create database and table
insert data into the table

build the first application by combining the video, openalpr and sqlite

issue: openalpr can't detect any plate number from the test video
test openalpr cloud api successfully: maybe the cloud api has some improvement based on the open source. That's why the cloud api is not free.

investigating:
the previous is OpenALPR  CarCheck API which is very slow, about 10 second per request

I'm also checking commercial SDK.....  

alter the database table so that the whole json result can be saved in db.

coding



question: 
how to deal with multiple cars? should be fine, because the json_result is an array based on vehicles, not plates.
bad angle: using orientation from openalpr_result

todo:
compile install openalpr for performance, need to fix tesseract install issue

install commercial SDK


