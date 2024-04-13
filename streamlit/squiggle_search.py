import pandas as pd
from PIL import Image
import streamlit as st
import time
import base64
import uuid
import os
from io import BytesIO
from pathlib import Path
from streamlit_drawable_canvas import st_canvas
import Gemini_funcs as gf
import matplotlib.pyplot as plt

def main():

    if 'clicked' not in st.session_state:
        st.session_state.clicked = False

    PAGES = {
        "Search": search,
        "About": about,
    }

    page = st.sidebar.selectbox("Page:", options=list(PAGES.keys()))
    PAGES[page]()

    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by Oleg and Travis</h6>',
            unsafe_allow_html=True,
        )

def click_button():
    st.session_state.clicked = True

def search():

    st.markdown("Draw a squiggle to represent the arc of emotions you want the plot of your next book to follow.")

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=3,
        stroke_color="#000",
        background_color="#fff",
        update_streamlit=True,
        height=150,
        drawing_mode="freedraw",
        point_display_radius=0,
        key="search",
        )

    # Do something interesting with the image data and paths
    if canvas_result.image_data is not None:
        print("show image")
        st.image(canvas_result.image_data)


    try:
        print("Creating tmp/ directory")
        Path("tmp/").mkdir()
    except FileExistsError:
        print("tmp/ already exists")
        pass

    # Regular deletion of tmp files
    # Hopefully callback makes this better
    now = time.time()
    N_HOURS_BEFORE_DELETION = .05
    for f in Path("tmp/").glob("*.png"):
        #st.write(f, os.stat(f).st_mtime, now)
        if os.stat(f).st_mtime < now - N_HOURS_BEFORE_DELETION * 3600:
            Path.unlink(f)

    if canvas_result is not None and canvas_result.image_data is not None:
        img_data = canvas_result.image_data
        im = Image.fromarray(img_data.astype("uint8"), mode="RGBA")

        file_path = f"tmp/{uuid.uuid4().hex}.png"

        im.save(file_path, "PNG")

        buffered = BytesIO()
        im.save(buffered, format="PNG")
        img_data = buffered.getvalue()
        try:
            # some strings <-> bytes conversions necessary here
            b64 = base64.b64encode(img_data.encode()).decode()
        except AttributeError:
            b64 = base64.b64encode(img_data).decode()

        #dl_link = (
        #    f'<a download="{file_path}" id="button_id" href="data:file/txt;base64,{b64}">Export PNG</a><br></br>'
        #)
        #st.markdown(dl_link, unsafe_allow_html=True)

        if st.button('Submit', on_click=click_button):
            arr_to_plot = gf.get_gemini_img_approx(file_path)
            plt = get_plot_from_squiggle(arr_to_plot)
            st.pyplot(plt)

def get_plot_from_squiggle(arr_to_plot):
    # data to be plotted
    x = arr_to_plot[:,0]
    y = arr_to_plot[:,1]

    # plotting
    plt.title("Drawn Line")
    plt.xlabel("X axis")
    plt.ylabel("Y axis")
    plt.plot(x, y, color ="red")
    plt.ylim(-1, 1)
    return plt

def about():

    st.markdown(
        """We used Gemini's API to search for books based on the squiggle you drew.
    """
    )

if __name__ == "__main__":
    #st.set_page_config(
    #    page_title="Squiggle Search!", page_icon=":pencil2:"
    #)
    st.title("Squiggle Search!")
    st.sidebar.subheader("Navigation")
    main()
