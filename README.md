# Design and implementation of a GUI to manage a particle accelerator module


## Project Summary 📃

This is the result of a long investigation to carry out my Bachelor's Thesis. It consists of the design and development of a GUI capable of remotely controlling the Anritsu MS2830A machine (signal generator and spectrum analyzer mode) and the Agilent N9020A machine (spectrum analyzer mode), as well as a BLAS and that makes use of EPICS to keep everything coordinated in case there are several of these GUIs deployed on different devices on the same subnet.

## Starting 🚀

_These instructions will allow you to get a working copy of the project on your local machine for development and testing purposes.._

See **Deployment** to learn how to deploy the project.


### Pre requirements 📋

* Python version used during development : **3.9.13**
* Version of pip used during development: **22.1.2**
* 64-bit system architecture if possible


### Installation 🔧

Possible modes of use depending on the version of pip you have:

```
pip install -r requirements.txt
```

or
```
pip3 install -r requirements.txt
```


## Deployment 📦

### API Deployment 🔑

Possible modes of use depending on the version of python you have(means the same):

```
uvicorn api:api --reload
```

or
```
python -m uvicorn api:api --reload
```
or
```
python3 -m uvicorn api:api --reload
```

### EPICS IOC Deployment 🔓

We have to deploy it on a device where EPICS has been previously installed for it to work properly.

```
softIoc -d TFG_EPICS_IOC.txt
```

### GUI Deployment 🔒

Possible modes of use depending on the version of python you have:

```
python TFG_SALVADOR.py
```
or
```
python3 TFG_SALVADOR.py
```




## Testing Project - Click the images to see the videos ⚙️

### GUI working - Anritsu machine 🔩

<br>

[![Watch the video](https://img.youtube.com/vi/EyJyEqjn67A/hqdefault.jpg)](https://youtu.be/EyJyEqjn67A)           [![Watch the video](https://img.youtube.com/vi/PJkaKhMkvzs/hqdefault.jpg)](https://youtu.be/PJkaKhMkvzs) 

<br>


### GUI working - Agilent machine ⌨️

<br>

[![Watch the video](https://img.youtube.com/vi/OBzyULWWtBo/hqdefault.jpg)](https://youtu.be/OBzyULWWtBo)

<br>

### GUI working - BLAS 🔧

<br>

[![Watch the video](https://img.youtube.com/vi/F3Cda97Ct-Y/hqdefault.jpg)](https://youtu.be/F3Cda97Ct-Y)

<br>


### GUI working in Tablet Raspberry 💻

<br>

[![Watch the video](https://img.youtube.com/vi/_QuZN7sVWnI/hqdefault.jpg)](https://youtu.be/_QuZN7sVWnI)

<br>



### GUI translation example📢

<br>

[![Watch the video](https://img.youtube.com/vi/pacES_BvcD0/hqdefault.jpg)](https://youtu.be/pacES_BvcD0)

<br>


## Built with 🛠️


* [Python](https://www.python.org/) - Programming language used
    * [PyQT](https://pythonpyqt.com/what-is-pyqt/) - Tool to create the GUI
    * [FastAPI](https://fastapi.tiangolo.com/) - Tool to create the API
    * [pyEPICS](https://pyepics.github.io/pyepics/overview.html) - Tool to interact with the EPICS IOC in our EPICS server
    * [PyVISA](https://pyvisa.readthedocs.io/en/latest/) - Tool to create the libraries with which to control Anritsu MS2830A and Agilent N9020A machines via Ethernet
* [EPICS](https://epics-controls.org/) - to share GUI data across the entire subnet quickly and easily
* [OpenAPI](https://www.openapis.org/) - Standard to create the API

## Author ✒️

* **Salvador Jesús Megías Andreu** - [salvadorJMA](https://github.com/salvadorJMA)


## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details

## Expressions of Gratitude 🎁

* Tell others about this project 📢
* Buy me a beer 🍺 or a coffee ☕. 




---
⌨️ with ❤️ by [Salvador Megías Andreu](https://github.com/salvadorJMA) 😊
