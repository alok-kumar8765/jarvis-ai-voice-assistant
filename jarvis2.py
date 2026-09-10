import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import pyttsx3
import webbrowser
import requests
import screen_brightness_control as sbc
import ctypes
import urllib.parse
import re


# =========================================================
# VOICE ENGINE
# =========================================================

engine = pyttsx3.init()
engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)


def speak(text):
    status_label.config(
        text=f"Jarvis: {text}",
        fg="#00ffcc"
    )
    root.update()

    engine.say(text)
    engine.runAndWait()


# =========================================================
# VOICE RECOGNITION
# =========================================================

def take_command():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        status_label.config(
            text="🎙️ Listening...",
            fg="#2ecc71"
        )
        root.update()

        try:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )

            status_label.config(
                text="🔄 Recognizing...",
                fg="#3498db"
            )
            root.update()

            query = recognizer.recognize_google(
                audio,
                language="en-in"
            )

            query = query.lower().strip()

            command_label.config(
                text=f"You said: {query}"
            )

            print("Recognized:", query)

            return query

        except sr.WaitTimeoutError:

            status_label.config(
                text="No voice detected.",
                fg="#e74c3c"
            )

            return "none"

        except sr.UnknownValueError:

            status_label.config(
                text="Sorry, I couldn't understand.",
                fg="#e74c3c"
            )

            return "none"

        except sr.RequestError as e:

            print("Speech Recognition Error:", e)

            status_label.config(
                text="Speech service unavailable.",
                fg="#e74c3c"
            )

            return "none"

        except Exception as e:

            print("Microphone Error:", e)

            status_label.config(
                text="Microphone error.",
                fg="#e74c3c"
            )

            return "none"


# =========================================================
# BRIGHTNESS
# =========================================================

def get_brightness():

    try:

        value = sbc.get_brightness()

        if isinstance(value, list):
            value = value[0]

        return int(value)

    except Exception as e:

        print("Brightness Error:", e)
        return None


def set_brightness(value):

    try:

        value = max(0, min(100, int(value)))

        sbc.set_brightness(value)

        speak(
            f"Brightness set to {value} percent."
        )

    except Exception as e:

        print("Brightness Error:", e)

        speak(
            "Sorry, I could not control the brightness."
        )


def brightness_up():

    current = get_brightness()

    if current is not None:

        set_brightness(
            min(100, current + 10)
        )

    else:

        speak(
            "I could not read the current brightness."
        )


def brightness_down():

    current = get_brightness()

    if current is not None:

        set_brightness(
            max(0, current - 10)
        )

    else:

        speak(
            "I could not read the current brightness."
        )


# =========================================================
# WINDOWS VOLUME
# =========================================================

def press_volume_key(key_code, times=5):

    try:

        for _ in range(times):

            ctypes.windll.user32.keybd_event(
                key_code,
                0,
                0,
                0
            )

            ctypes.windll.user32.keybd_event(
                key_code,
                0,
                2,
                0
            )

    except Exception as e:

        print("Volume Error:", e)


def volume_up():

    press_volume_key(0xAF, 5)

    speak("Volume increased.")


def volume_down():

    press_volume_key(0xAE, 5)

    speak("Volume decreased.")


def volume_mute():

    press_volume_key(0xAD, 1)

    speak("Volume muted.")


# =========================================================
# GOOGLE SEARCH
# =========================================================

def google_search(query):

    query = query.strip()

    if not query:

        speak("What should I search on Google?")

        return

    speak(
        f"Searching Google for {query}"
    )

    encoded_query = urllib.parse.quote_plus(query)

    url = (
        "https://www.google.com/search?q="
        + encoded_query
    )

    webbrowser.open(url)


# =========================================================
# YOUTUBE SEARCH / PLAY
# =========================================================

def youtube_play(query):

    query = query.strip()

    if not query:

        speak(
            "What should I play on YouTube?"
        )

        return

    speak(
        f"Searching YouTube for {query}"
    )

    encoded_query = urllib.parse.quote_plus(query)

    # YouTube search page
    url = (
        "https://www.youtube.com/results?search_query="
        + encoded_query
    )

    webbrowser.open(url)


# =========================================================
# EXTRACT YOUTUBE QUERY
# =========================================================

def extract_youtube_query(query):

    patterns = [

        r"play (.+?) on youtube",

        r"play (.+?) in youtube",

        r"play youtube (.+)",

        r"youtube play (.+)",

        r"search youtube (.+)",

        r"search (.+?) on youtube",

        r"play (.+)",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            query,
            re.IGNORECASE
        )

        if match:

            result = match.group(1).strip()

            # Remove leftover words
            result = result.replace(
                "on youtube",
                ""
            ).strip()

            result = result.replace(
                "in youtube",
                ""
            ).strip()

            return result

    return ""


# =========================================================
# WIKIPEDIA API
# =========================================================

def wikipedia_search(search_query):

    search_query = search_query.strip()

    if not search_query:

        speak(
            "Please tell me what you want to search on Wikipedia."
        )

        return

    speak(
        f"Searching Wikipedia for {search_query}"
    )

    try:

        # -------------------------------------------------
        # STEP 1: Wikipedia search API
        # -------------------------------------------------

        search_url = (
            "https://en.wikipedia.org/w/api.php"
        )

        search_params = {

            "action": "query",

            "list": "search",

            "srsearch": search_query,

            "format": "json",

            "utf8": 1,

            "srlimit": 5
        }

        response = requests.get(
            search_url,
            params=search_params,
            headers={
                "User-Agent":
                "Jarvis-AI-Assistant/1.0"
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        search_results = data.get(
            "query",
            {}
        ).get(
            "search",
            []
        )

        if not search_results:

            speak(
                "I could not find an article on Wikipedia."
            )

            messagebox.showinfo(
                "Wikipedia",
                "No article found."
            )

            return

        # First matching article
        title = search_results[0]["title"]

        print("Wikipedia article:", title)

        # -------------------------------------------------
        # STEP 2: Get article summary
        # -------------------------------------------------

        summary_url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + urllib.parse.quote(
                title,
                safe=""
            )
        )

        summary_response = requests.get(
            summary_url,
            headers={
                "User-Agent":
                "Jarvis-AI-Assistant/1.0"
            },
            timeout=10
        )

        summary_response.raise_for_status()

        article_data = summary_response.json()

        summary = article_data.get(
            "extract",
            ""
        )

        article_url = (
            article_data.get(
                "content_urls",
                {}
            )
            .get(
                "desktop",
                {}
            )
            .get(
                "page",
                ""
            )
        )

        # -------------------------------------------------
        # STEP 3: Show result
        # -------------------------------------------------

        if summary:

            messagebox.showinfo(
                f"Wikipedia - {title}",
                summary
            )

            speak(
                "According to Wikipedia."
            )

            # Don't make Jarvis speak an extremely long article
            speech_text = summary

            if len(speech_text) > 700:

                speech_text = (
                    speech_text[:700]
                    + "..."
                )

            speak(speech_text)

        # -------------------------------------------------
        # STEP 4: Open article
        # -------------------------------------------------

        if article_url:

            open_article = messagebox.askyesno(
                "Wikipedia",
                f"Do you want to open the full article?\n\n"
                f"{title}"
            )

            if open_article:

                webbrowser.open(
                    article_url
                )

    except requests.exceptions.RequestException as e:

        print(
            "Wikipedia Network Error:",
            e
        )

        speak(
            "I could not connect to Wikipedia."
        )

        messagebox.showerror(
            "Wikipedia Error",
            "Could not connect to Wikipedia.\n\n"
            "Please check your internet connection."
        )

    except ValueError as e:

        print(
            "Wikipedia JSON Error:",
            e
        )

        speak(
            "Wikipedia returned an invalid response."
        )

        messagebox.showerror(
            "Wikipedia Error",
            str(e)
        )

    except Exception as e:

        print(
            "Wikipedia Error:",
            e
        )

        speak(
            "Sorry, I could not search Wikipedia."
        )

        messagebox.showerror(
            "Wikipedia Error",
            str(e)
        )


# =========================================================
# OPEN WEBSITES
# =========================================================

def open_google():

    speak("Opening Google.")

    webbrowser.open(
        "https://www.google.com/"
    )


def open_youtube():

    speak("Opening YouTube.")

    webbrowser.open(
        "https://www.youtube.com/"
    )


def open_wikipedia():

    speak("Opening Wikipedia.")

    webbrowser.open(
        "https://www.wikipedia.org/"
    )


# =========================================================
# MAIN JARVIS LOGIC
# =========================================================

def run_jarvis():

    speak("How can I help you?")

    query = take_command()

    if query == "none":
        return


    # =====================================================
    # WIKIPEDIA
    # =====================================================

    if "wikipedia" in query:

        if (
            "open wikipedia" in query
            and len(query) < 20
        ):

            open_wikipedia()

        else:

            wikipedia_query = query

            wikipedia_query = re.sub(
                r"search wikipedia",
                "",
                wikipedia_query
            )

            wikipedia_query = re.sub(
                r"wikipedia",
                "",
                wikipedia_query
            )

            wikipedia_query = re.sub(
                r"search",
                "",
                wikipedia_query
            )

            wikipedia_query = wikipedia_query.strip()

            wikipedia_search(
                wikipedia_query
            )

        return


    # =====================================================
    # YOUTUBE
    # =====================================================

    youtube_words = [
        "youtube",
        "play on youtube",
        "play youtube",
        "search youtube"
    ]

    if any(
        word in query
        for word in youtube_words
    ):

        if "open youtube" in query:

            open_youtube()

            return

        youtube_query = extract_youtube_query(
            query
        )

        if youtube_query:

            youtube_play(
                youtube_query
            )

        else:

            # Fallback
            youtube_query = query

            youtube_query = youtube_query.replace(
                "youtube",
                ""
            )

            youtube_query = youtube_query.replace(
                "play",
                ""
            )

            youtube_query = youtube_query.strip()

            if youtube_query:

                youtube_play(
                    youtube_query
                )

            else:

                open_youtube()

        return


    # =====================================================
    # GOOGLE
    # =====================================================

    if "open google" in query:

        open_google()

        return


    if (
        "search google" in query
        or "google search" in query
    ):

        google_query = query

        google_query = google_query.replace(
            "search google",
            ""
        )

        google_query = google_query.replace(
            "google search",
            ""
        )

        google_query = google_query.strip()

        google_search(
            google_query
        )

        return


    # =====================================================
    # BRIGHTNESS
    # =====================================================

    if (
        "increase brightness" in query
        or "brightness increase" in query
        or "brightness up" in query
    ):

        brightness_up()

        return


    if (
        "decrease brightness" in query
        or "brightness decrease" in query
        or "brightness down" in query
    ):

        brightness_down()

        return


    if "set brightness" in query:

        numbers = re.findall(
            r"\d+",
            query
        )

        if numbers:

            set_brightness(
                int(numbers[0])
            )

        else:

            speak(
                "Please tell me the brightness percentage."
            )

        return


    # =====================================================
    # VOLUME
    # =====================================================

    if (
        "volume up" in query
        or "increase volume" in query
        or "volume increase" in query
    ):

        volume_up()

        return


    if (
        "volume down" in query
        or "decrease volume" in query
        or "volume decrease" in query
    ):

        volume_down()

        return


    if (
        query == "mute"
        or "mute volume" in query
        or "volume mute" in query
    ):

        volume_mute()

        return


    # =====================================================
    # DEFAULT GOOGLE SEARCH
    # =====================================================

    google_search(query)


# =========================================================
# TKINTER GUI
# =========================================================

root = tk.Tk()

root.title(
    "Jarvis AI Assistant"
)

root.geometry(
    "520x450"
)

root.configure(
    bg="#1e272e"
)

root.resizable(
    False,
    False
)


# =========================================================
# TITLE
# =========================================================

title_label = tk.Label(
    root,
    text="JARVIS AI",
    font=("Arial", 28, "bold"),
    fg="#00d2d3",
    bg="#1e272e"
)

title_label.pack(
    pady=(25, 5)
)


subtitle_label = tk.Label(
    root,
    text="Your Personal Voice Assistant",
    font=("Arial", 12),
    fg="#d2dae2",
    bg="#1e272e"
)

subtitle_label.pack(
    pady=5
)


# =========================================================
# STATUS
# =========================================================

status_label = tk.Label(
    root,
    text="Click 'Tap to Speak' to Start",
    font=("Arial", 13, "italic"),
    fg="#d2dae2",
    bg="#1e272e",
    wraplength=450
)

status_label.pack(
    pady=20
)


# =========================================================
# COMMAND
# =========================================================

command_label = tk.Label(
    root,
    text="",
    font=("Arial", 12),
    fg="white",
    bg="#1e272e",
    wraplength=450
)

command_label.pack(
    pady=10
)


# =========================================================
# MIC BUTTON
# =========================================================

mic_button = tk.Button(
    root,
    text="🎙️  Tap to Speak",
    font=("Arial", 16, "bold"),
    bg="#e74c3c",
    fg="white",
    activebackground="#c0392b",
    activeforeground="white",
    padx=30,
    pady=15,
    bd=0,
    cursor="hand2",
    command=run_jarvis
)

mic_button.pack(
    pady=25
)


# =========================================================
# HELP
# =========================================================

help_label = tk.Label(
    root,
    text=(
        "Try:\n"
        "\"Wikipedia Albert Einstein\"\n"
        "\"Play Arijit Singh on YouTube\"\n"
        "\"Search Google Python tutorial\"\n"
        "\"Increase brightness\"  •  \"Volume up\""
    ),
    font=("Arial", 9),
    fg="#808e9b",
    bg="#1e272e",
    justify="center"
)

help_label.pack(
    pady=5
)


# =========================================================
# START
# =========================================================

root.mainloop()
