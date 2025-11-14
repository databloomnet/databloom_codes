import streamlit as st


def mixcase_alternate(s):
    s_out = ""
    for i, char in enumerate(s):
        if char.isalpha():
            if i % 2 == 0:
                s_out += char.upper()
            else:
                s_out += char.lower()
    return s_out

def camelcase(s):
    s_out = ""
    within_string = True
    for i, char in enumerate(s):
        if within_string:
            if char in [" ", "\t"]:
                within_string = False
                # s_out += char
            elif char.isalpha():
                s_out += char.lower()
            else:
                # s_out += char.lower()
                pass
        else:
            if char.isalpha():
                s_out += char.upper()
                within_string = True
            else:
                # s_out += char
                pass
    return s_out


FLIPPED_CHARS = { # ai
    'a': 'ɐ', 'b': 'q', 'c': 'ɔ', 'd': 'p', 'e': 'ǝ', 'f': 'ɟ', 'g': 'ƃ',
    'h': 'ɥ', 'i': 'ı', 'j': 'ɾ', 'k': 'ʞ', 'l': 'ꞁ', 'm': 'ɯ', 'n': 'u',
    'o': 'o', 'p': 'd', 'q': 'b', 'r': 'ɹ', 's': 's', 't': 'ʇ', 'u': 'n',
    'v': 'ʌ', 'w': 'ʍ', 'x': 'x', 'y': 'ʎ', 'z': 'z',
    'A': '∀', 'B': 'B', 'C': 'Ɔ', 'D': 'D', 'E': 'Ǝ', 'F': 'Ⅎ', 'G': 'פ',
    'H': 'H', 'I': 'I', 'J': 'ſ', 'K': 'K', 'L': '˥', 'M': 'W', 'N': 'N',
    'O': 'O', 'P': 'Ԁ', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': '⊥', 'U': '∩',
    'V': 'Λ', 'W': 'M', 'X': 'X', 'Y': '⅄', 'Z': 'Z',
    '0': '0', '1': 'Ɩ', '2': 'ᄅ', '3': 'Ɛ', '4': 'ㄣ', '5': 'ϛ', '6': '9',
    '7': 'ㄥ', '8': '8', '9': '6',
    '.': '˙', ',': '‘', '!': '¡', '?': '¿', "'": ',', '"': '„',
    '(': ')', ')': '(', '[': ']', ']': '[', '{': '}', '}': '{',
    '<': '>', '>': '<', '&': '⅋', '_': '‾',
    ' ': ' ' # Space remains a space
}

EMOJI_MAP = {
    'A': '🍎', 'B': '🍌', 'C': '🥕', 'D': '🐬', 'E': '🌍',
    'F': '🐸', 'G': '🦒', 'H': '🏠', 'I': '🍦', 'J': '🕹️',
    'K': '🔑', 'L': '🦁', 'M': '🐵', 'N': '🪺', 'O': '🐙',
    'P': '🍍', 'Q': '❓', 'R': '🌈', 'S': '🦈', 'T': '🌴',
    'U': '☂️', 'V': '🌋', 'W': '🍉', 'X': '❌', 'Y': '🛳️',
    'Z': '🦓', ' ': ' - '
}
EMOJI_MAP.update({k.lower(): v for k, v in EMOJI_MAP.items()})


def flip_upside_down(text):
    flipped_text = []
    for char in reversed(text): # Reverse the string first for true upside-down effect
        flipped_text.append(FLIPPED_CHARS.get(char, char)) # Use .get() for characters not in map

    return "".join(flipped_text)


def flip_vowels(s):
    s_out = ""
    for c in s:
        if c in ["A", "E", "I", "O", "U", "Y", "a", "e", "i", "o", "u", "y"]:
            s_out += FLIPPED_CHARS.get(c, c)
        else:
            s_out += c
    return s_out


def upcase_vowels(s):
    s_out = ""
    for c in s:
        if c in ["A", "E", "I", "O", "U", "Y", "a", "e", "i", "o", "u", "y"]:
            s_out += c.upper()
        else:
            s_out += c
    return s_out


def encoded_emoji(s):
    s_encoded = ""
    for c in s: 
        s_encoded += EMOJI_MAP.get(c, c)
        #s_encoded += "🍎"

    return s_encoded



st.title("Echoer")
msg = st.text_input("Say something", value="the quick brown fox jumped over the lazy dog")
if st.button("Send") and msg:
    st.success(f"(yelling):    {msg.upper()}")
    st.success(f"(whisper):    {msg.lower()}")
    st.success(f"(alt):        {mixcase_alternate(msg)}")
    st.success(f"(camel):      {camelcase(msg)}")
    st.success(f"(upsidedown): {flip_upside_down(msg)}")
    st.success(f"(flipvowels): {flip_vowels(msg)}")
    st.success(f"(upvowels):   {upcase_vowels(msg.lower())}")
    st.success(f"(coded):      {encoded_emoji(msg)}")

    # st.success(f"Echo: {msg_upcase}")
    # msg2 = mixcase_alternate(msg)
    # msg3 = camelcase(msg)
    # st.success(f"Echo: {msg2}")
    # st.success(f"Echo: {msg3}")
    # msg_yell = msg.upper()
    # msg_quiet = msg.lower()
    # msg_alt = mixcase_alternate(msg)
    # msg_camel = camelcase(msg)

    # msg_all = ""
    # msg_all += "(yelling):  " + msg_yell + "\n"
    # msg_all += "(whisper):  " + msg_quiet + "\n"
    # msg_all += "(alterate): " + msg_alt + "\n"
    # msg_all += "(camel):   " + msg_camel + "\n"
    # st.success(msg_all)

