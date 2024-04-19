<img src="./streamlit/assets/MHacks_header.png" alt="MHacks!" height="180"/></br>
# GutEmotions for Google x [MHacks!](https://safe-banon-80d.notion.site/Hacker-Guide-079b584c6deb446e88c53712dc0f9ecb)

Submission for Spring 2024 hackathon with Travis.

This hackathon required the use of the just released [Google Gemini 1.5](https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/) API. It has a context window of 1 million tokens, so the goal was to use large-ish data. This could be 700,000 words, 11 hours of audio, or 1 hour of video.

The Gutenberg book archive was the first thing to come to mind for large, freely available data. We wanted to do a little more than just summarization of a book, so we tried pulling out the important emotions in the book and having Gemini attach a score based on how positive or negative it was, and return something useable in python. The prompt used here was:
```
prompt = "You are an english literature professor. Please read this book and find near forty most important events. From those events, find the main emotion portrayed. Given the events and emotions, can you create a python list of tuples. The first element in each tuple is the emotion as a string enclosed in double-quotation marks, the second element is your ranking of that emotion on a scale of -1 to +1, with +1 being the most positive emotion and -1 being the most negative emotion, and the third element being a short utf8-encoded string summary of the event enclosed in double-quotation marks. This list of tuples should be assignable to a python list using: ast.literal_eval(). Only this list should be returned."
```
This worked pretty well after trimming it down to just the list.

Our next goal was to use a drawing or squiggle to be interpreted by Gemini and used as search input to have the system find similar emotional arcs or paths in analyzed books and return the nearest ones. This prompt could use more work, Gemini has a hard time with this.

[Devpost](https://mhacks-x-google.devpost.com/) site

Get a list of emotions mentioned in books, then recommend a book
