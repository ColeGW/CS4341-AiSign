import os
import sys
import dill
import yaml
import base64
from src.logger import logging
from src.exception import CustomException


def save_objects(file_path: str, obj: object) -> None:
    logging.info("Entered the save_object method of utils")
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as file:
            dill.dump(obj, file)
        logging.info("Excited the save_object method of utils")

    except Exception as e:
        raise CustomException(e, sys) from e

def load_object(file_path: str) -> object:
    logging.info("Entered the load_object method of utils")
    try:
        with open(file_path, 'rb') as file:
            obj = dill.load(file)
        logging.info("Excited the load_object method of utils")
        return obj
    except Exception as e:
        raise CustomException(e, sys) from e

def image_to_base64(image):
    try:
        logging.info("Entered the image_to_base64 method of utils")
        with open(image, "rb") as imgFile:
            my_string = base64.b64encode(imgFile.read())
        logging.info("Exited the image_to_base64 method of utils")
        return my_string
    except Exception as e:
        raise CustomException(e, sys) from e

def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, 'rb') as yamlFile:
            return yaml.safe_load(yamlFile)
    except Exception as e:
        raise CustomException(e, sys) from e