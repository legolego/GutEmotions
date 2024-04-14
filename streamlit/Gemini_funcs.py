import os
import google.generativeai as genai
import requests
import ast
import re
import numpy as np
from PIL import Image

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

def get_gemini_img_approx(img_path):

    print(f"Getting approximations for image: {img_path}")
    image_path = img_path
    image_name = image_path[image_path.rindex('/')+1:image_path.rindex('.')]

    file_up = genai.upload_file(path=image_path,
                                    display_name=image_name)

    print(f"Uploaded file '{file_up.display_name}' as: {file_up.uri}")

    prompt = "Can you break this line into about 30 points, including a point for the very beginning and a point for the very end, into a number of points needed for a smooth approximation. Give me approximate x,y coordinates for each important point in order, starting with x equal to 0, and with the vertical center equal to 0 on the y-axis, returning an array that should be assignable to a python variable using: ast.literal_eval()?"

    response = model.generate_content([prompt, file_up])

    print(response.text)

    arr = np.array(ast.literal_eval(response.text[
        response.text.index('['):response.text.rindex(']')+1]))
    print('returned!')
    return scale_numbers(arr[:,1])

def scale_numbers(numbers):
    """
    Scales a list of numbers to be between -1 and 1.

    Args:
        numbers: A list of numbers.

    Returns:
        A new list of numbers scaled between -1 and 1.
    """
    min_val = min(numbers)
    max_val = max(numbers)
    scaled_numbers = [(2 * (num - min_val) / (max_val - min_val)) - 1 for num in numbers]
    return scaled_numbers