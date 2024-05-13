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

    st.markdown(":pencil2: a squiggle to represent the arc of emotions of the plot of the :book: you would like to read next.")
    st.markdown(":smiley: emotions are at the `top, y=+1`")
    st.markdown(":expressionless: emotions are in the `middle, y=0`")
    st.markdown(":cry: emotions are at the `bottom, y=-1`")

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

        # st.image(img_data)

        im = Image.fromarray(img_data.astype("uint8"), mode="RGBA")

        file_path = f"tmp/{uuid.uuid4().hex}.png"

        im.save(file_path, "PNG")

        buffered = BytesIO()
        im.save(buffered, format="PNG")
        img_data = buffered.getvalue()


        if st.button('Search', on_click=click_button):
            st.markdown("Sending prompt and png to Gemini 1.5....")
            st.markdown("Prompt:" + "`" + gf.prompt + "`")
            arr_gemini = gf.get_gemini_img_approx(file_path)
            arr_PIL = gf.get_line_from_image_PIL(file_path)

            st.markdown("Gemini Representation of Squiggle:")
            plt = get_plot_from_squiggle(arr_gemini, color="blue")
            st.pyplot(plt)

            st.markdown("[PIL](https://python-pillow.org) Representation of Squiggle:")
            plt = get_plot_from_squiggle(arr_PIL)
            st.pyplot(plt)

            # print(arr_to_plot)

            # Load the books
            dfBooks = pd.read_parquet("streamlit/data/gutenberg_books.parquet").iloc[:, 1:]

            target = np.array(arr_PIL)
            all_dists = []
            for index, row in dfBooks[dfBooks['emotion_scores'].str.len() > 0].iterrows():
                bookArc = np.array(ast.literal_eval(row['emotion_scores']),
                                   dtype=float)
                #print("Arc:", bookArc)
                distance = dtw.distance_fast(target, bookArc)
                all_dists.append((row['title'], distance, bookArc, row['txt_link'], np.max(bookArc), np.min(bookArc) ))

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
                max = item[4]
                min = item[5]

                # Create a matplotlib plot of the array
                fig, ax = plt.subplots(figsize=(2, .3))
                ax.plot(array)
                #ax.plot([1,-1], color = "green")
                ax.set_ylim(-1.2, 1.2)
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
            st.markdown("Nearest 20 Books by [Dynamic Time Warping](https://en.wikipedia.org/wiki/Dynamic_time_warping) Distance vs PIL representation:")
            st.markdown(html_table, unsafe_allow_html=True)
            plt.close()


def get_plot_from_squiggle(arr_to_plot, color="red", title="Drawn Line"):
    plt.clf()
    # data to be plotted

    y = arr_to_plot#[:,1]

    # plotting

    fig = plt.figure(figsize=(8, .1))
    plt.axis('off')
    plt.tight_layout(pad=-8)
    plt.ylim(-1.2, 1.2)
    plt.plot(y, color = color, linewidth= 1.5)
    #plt.plot([1,-1], color = "green", linewidth= 10)

    return plt


def about():

    st.markdown(
        """We used Gemini's API to search for books based on the squiggle you drew.
    """
    )


if __name__ == "__main__":
    st.set_page_config(
       page_title="Gut-emotions Squiggle Search!", page_icon=":pencil2:"
    )
    st.title("Search with a Squiggle!")

    st.sidebar.markdown(
    """<a href="mhacks.org">
    <img src="data:image/png;base64,{}" width="100">
    </a>""".format(
        base64.b64encode(open("streamlit/assets/Frame_45.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
    )
    st.sidebar.subheader("Gut-Emotions powered by [Gemini 1.5](https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/)")
    st.sidebar.markdown("Searching for emotional arcs from books in the Gutenberg Archive with only a line.")
    main()
