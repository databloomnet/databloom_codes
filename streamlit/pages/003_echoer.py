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
st.markdown("A simple echoer.  No AI stuff here...- Jeremy")

msg = st.text_input("Say something", value="the quick brown fox jumped over the lazy dog")
if st.button("Send") and msg:
    out = []
    out.append( f"(yelling):    {msg.upper()}" )
    out.append( f"(whisper):    {msg.lower()}")
    out.append( f"(alt):        {mixcase_alternate(msg)}")
    out.append(f"(camel):      {camelcase(msg)}")
    out.append(f"(upsidedown): {flip_upside_down(msg)}")
    out.append(f"(flipvowels): {flip_vowels(msg)}")
    out.append(f"(upvowels):   {upcase_vowels(msg.lower())}")
    out.append(f"(coded):      {encoded_emoji(msg)}")

    outc = ""
    for s in out:
        outc += f"{s}\n\n"
    st.success(outc)



st.write("[code](https://github.com/databloomnet/databloom_codes/blob/main/pages/003_echoer.py)")
