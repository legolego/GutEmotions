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
import io
import ast

import numpy as np
from dtaidistance import dtw


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
            '<h6>Source in <a href="https://github.com/legolego/GutEmotions"> <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Github-desktop-logo-symbol.svg/128px-Github-desktop-logo-symbol.svg.png" alt="Github logo" height="40"></a></h6>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h6>See in <a href="https://devpost.com/software/project-gutenberg-emotional-analysis"> <img src="http://logo-logos.com/2016/10/Devpost_logo_image_picture.png" alt="Devpost logo" height="20"></a></h6>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by Oleg and Travis</h6>',
            unsafe_allow_html=True,
        )


def click_button():
    st.session_state.clicked = True


def search():

    st.markdown("Draw a squiggle to represent the arc of emotions you want the plot of your next book to follow.")
    st.markdown(":smiley: emotions are up, :cry: emotions are down.")

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
    # if canvas_result.image_data is not None:
    #   print("show image")
    #    st.image(canvas_result.image_data)

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
        # st.write(f, os.stat(f).st_mtime, now)
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


        if st.button('Search', on_click=click_button):
            arr_to_plot = gf.get_gemini_img_approx(file_path)
            plt = get_plot_from_squiggle(arr_to_plot)

            st.markdown("Gemini Representation of Squiggle:")
            st.pyplot(plt)

            # print(arr_to_plot)

            # Load the books
            dfBooks = pd.read_parquet("streamlit/data/gutenberg_books.parquet").iloc[:, 1:]


            target = np.array(arr_to_plot)
            all_dists = []
            for index, row in dfBooks[dfBooks['emotion_scores'].str.len() > 0].iterrows():
                bookArc = np.array(ast.literal_eval(row['emotion_scores']),
                                   dtype=float)
                print("Arc:", bookArc)
                distance = dtw.distance_fast(target, bookArc)
                all_dists.append((row['title'], distance, bookArc, row['txt_link']))

            sorted_by_second = sorted(all_dists, key=lambda tup: tup[1],
                                      reverse=False)

            # Create an empty list to store the HTML table rows
            table_rows = []

            # Iterate over each tuple in sorted_by_second
            for item in sorted_by_second[:20]:
                title = item[0]
                distance = item[1]
                array = item[2]
                link = item[3]

                # Create a matplotlib plot of the array
                fig, ax = plt.subplots(figsize=(2, .3))
                ax.plot(array)
                ax.set_title(title + " - " + str(round(distance, 2)))
                ax.get_xaxis().set_visible(False)
                ax.get_yaxis().set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)


                # Convert the plot to an image
                buf = io.BytesIO()
                # plt.figure(figsize=(1,1))
                plt.savefig(buf, format='png')
                buf.seek(0)
                plot_img = base64.b64encode(buf.getvalue()).decode('utf-8')

                # Create the HTML table row
                table_row = f"<tr><td><a href={link}>{title}</a></td><td>{distance}</td><td><img src='data:image/png;base64,{plot_img}'></td></tr>"

                # Append the row to the list of table rows
                table_rows.append(table_row)

            # Create the HTML table
            html_table = f"<table><tr><th>Title</th><th>Distance</th><th>Plot</th></tr>{''.join(table_rows)}</table>"

            # Display the HTML table
            st.markdown("Nearest 20 Books by Dynamic Time Warping Distance:")
            st.markdown(html_table, unsafe_allow_html=True)



def get_plot_from_squiggle(arr_to_plot, title="Drawn Line"):
    plt.clf()
    # data to be plotted

    # x = arr_to_plot[:,0]
    y = arr_to_plot#[:,1]

    # plotting

    # plt.xlabel("X axis")
    # plt.ylabel("Y axis")
    plt.figure(figsize=(2,.2))
    plt.axis('off')
    # plt.title(title, fontsize = 3)
    plt.plot(y, color ="red")


    # plt.ylim(-1, 1)
    return plt


def about():

    st.markdown(
        """We used Gemini's API to search for books based on the squiggle you drew.
    """
    )


if __name__ == "__main__":
    # st.set_page_config(
    #    page_title="Squiggle Search!", page_icon=":pencil2:"
    # )
    st.title("Squiggle Search!")
    st.sidebar.subheader("Navigation")
    main()
