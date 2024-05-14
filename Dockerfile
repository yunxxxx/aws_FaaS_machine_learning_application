#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

# Define global args
ARG FUNCTION_DIR="/home/app/"
ARG RUNTIME_VERSION="3.8"
ARG DISTRO_VERSION="3.12"

FROM python:${RUNTIME_VERSION}-slim AS python-slim

#RUN apt-get update \
#    && apt-get install -y cmake ca-certificates libgl1-mesa-glx
RUN python${RUNTIME_VERSION} -m pip install --upgrade pip

FROM python-slim AS build-image

# Include global args in this stage of the build
ARG FUNCTION_DIR
ARG RUNTIME_VERSION
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Install Lambda Runtime Interface Client for Python
RUN python${RUNTIME_VERSION} -m pip install awslambdaric --target ${FUNCTION_DIR}

# Stage 3 - final runtime image
# Grab a fresh copy of the Python image
FROM python-slim
# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}
# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie

# Install torch
RUN pip3 install torch==1.9.0+cpu torchvision==0.10.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install facenet-pytorch --no-deps
RUN pip install opencv-python-headless
RUN python${RUNTIME_VERSION} -m pip install --upgrade pip
# Install 
RUN apt-get update \
    && apt-get install -y python3-pil \
    && apt-get clean
# RUN apt-get install -y ffmpeg
#RUN apk --no-cache add ffmpeg

# Copy handler function
COPY requirements.txt ${FUNCTION_DIR}
#COPY ffmpeg ${FUNCTION_DIR}
#COPY ffmpeg /usr/bin

RUN python${RUNTIME_VERSION} -m pip install -r requirements.txt --target ${FUNCTION_DIR}
COPY entry.sh /

# Copy function code
COPY handler.py ${FUNCTION_DIR}
RUN chmod 777 /entry.sh

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
ENTRYPOINT [ "/entry.sh" ]
CMD [ "handler.handler" ]