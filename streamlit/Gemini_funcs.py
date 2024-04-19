import os
import google.generativeai as genai
import requests
import ast
import re
import numpy as np
import PIL.Image

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
prompt = "Can you break this line into about 30 points, including a point for the very beginning and a point for the very end, into a number of points needed for a smooth approximation. Give me approximate x,y coordinates for each important point in order, starting with x equal to 0, and with the vertical center equal to 0 on the y-axis, returning an array that should be assignable to a python variable using: ast.literal_eval()?"
prompt = "You are an image reader who specializes in the (x,y) cartesian plane. Parse the image and find enough (x,y) coordinates to make a smooth approximation of the hand-drawn black line on a white background in the each image. The top edge of each image has represents a value of +1 on the y-axis. The bottom edge of each image represents a value of -1 on the y-axis. Return a valid python list of only the y coordinates."


def get_gemini_img_approx(img_path):

    print(f"Getting approximations for image: {img_path}")
    image_path = img_path
    image_name = image_path[image_path.rindex('/')+1:image_path.rindex('.')]

    file_up = genai.upload_file(path=image_path,
                                    display_name=image_name)

    print(f"Uploaded file '{file_up.display_name}' as: {file_up.uri}")

    response = model.generate_content([prompt, file_up])

    print(response.text)

    arr = np.array(ast.literal_eval(response.text[
        response.text.index('['):response.text.rindex(']')+1]))
    print('raw array returned!')
    return arr


def norm_array(arr):
    """
    Scales a 1D array of numbers to be between -1 and 1.

    Args:
        arr: Numpy array of numbers.

    Returns:
        A new array of numbers scaled to between -1 and 1.
    """
    min_val = np.min(arr)
    max_val = np.max(arr)
    scaled_arr = (arr - min_val) / ( max_val - min_val ) * 2 - 1
    return scaled_arr


def get_line_from_image_PIL(img_path):
    # This transpose is needed because PIL opens the image with the origin in the top left corner
    img = PIL.Image.open(img_path).transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)
    img = img.convert("RGB")
    w, h = img.size
    data = img.load()

    # will be a list of tuples of x,y coordinates
    pieces = []
    for x in range(w):
        for y in range(h):
            if data[x,y] != (255, 255, 255):
                print(x, y)
                pieces.append((x, y))

    # get the mean y value for each x value
    # https://stackoverflow.com/questions/50950231/group-by-with-numpy-mean
    np_arr = np.array(pieces)
    xs = np.unique(np_arr[:,0])
    y_means = [np.mean(np_arr[np_arr[:,0] == x, 1:]) for x in xs]
    return (np.array(y_means)-(h/2))/(h/2) # normalized to -1 to 1