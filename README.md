# aws_FaaS_machine_learning_application
this is a aws FaaS(Lambda) application

FaaS structure::
![alt text](https://github.com/yunxxxx/aws_FaaS_machine_learning_application/blob/main/image.png)

This is the function for the FaaS application. The function it self is very simple and the docerfile will set up the enviroment with pyuthon3 slim, ffmpeg, torch 1.9.0 CPU, torchvision 0.10.0 CPU, facenet-pytorch --no-deps, opencv-python-headless
In total, the docker environment will take about 800MG witch is around 0.05$ at the time(2024)
