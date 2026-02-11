# streamlit_reminders.py
"""
example streamlit function
#uses logger.py
"""
import streamlit as st
from datetime import datetime
#from logger import read_log, read_log, clear_log, verify_session, prompt_for_log, get_log_total_size, get_log_total_lines
from logger import verify_session, get_log_total_size, get_log_total_lines
import pandas as pd
import numpy as np

def do_basics():
    # button Starting: Basics
    #st.text("title, header, and subheader")
    basics_col1, basics_col2, basics_col3 = st.columns(3)
    with basics_col1:
        st.title("title")
    with basics_col2:
        st.header("header")
    with basics_col3:
        st.subheader("subheader")

    basics_col4, basics_col5 = st.columns(2)
    with basics_col4:
        st.write("https://streamlit.io/")
    with basics_col5:
        st.markdown(
            '<a href="https://streamlit.io/" target="_blank">or open in new tab</a>',
            unsafe_allow_html=True
        )

    st.code('X = ["A", "B", "C"]  # I am also setting X in the code')
    X = ["A", "B", "C"]

    basics_c6, basics_c7 = st.columns(2)
    with basics_c6:
        st.text("st.text(X)")
        st.text("st.write(X)")
        st.text("(notice how st.write is object aware)")
    with basics_c7:
        st.text(X)
        st.write(X)

    st.text("let's add a divider")
    st.divider()

    st.write("I can use asterisks once, twice or three times to do *italics* **bold** or ***both***")


def do_markdown():            
    st.markdown("you can do a lot of :cool: stuff in markdown.  It's >= doing it manually.  :sunglasses:")
    st.markdown("want more ex? --> :green[colors] :rainbow[rainbows] :red-badge[badges] :small[text] :red-background[highlights]")
    #st.markdown("markdown :sunglasses: and :cool:") # $\boxed{\pi=\frac c d}$ $\frac{22}{7}$") 

    st.markdown("colors :red[red] :orange[orange] :yellow[yellow] :green[green] :blue[blue] :violet[violet] :gray[gray] :grey[grey] :rainbow[rainbow] :primary[primary]")
    st.markdown("highlights...  :red-background[red] :orange-background[orange] :yellow-background[yellow] :green-background[green] :blue-background[blue] :violet-background[violet] :gray-background[gray] :grey-background[grey] :rainbow-background[rainbow] :primary-background[primary]")
    st.markdown("badges...:red-badge[red] :orange-badge[orange] :yellow-badge[yellow] :green-badge[green] :blue-badge[blue] :violet-badge[violet] :gray-badge[gray] :grey-badge[grey] no-rainbow :primary-badge[primary]")
    st.markdown("you can make :small[some text smaller] and revert back")
    
    st.markdown("typographical symbols: <- -> <-> -- >= <= ~=  and :monocle: 1500+ [emoji-shortcodes:](https://share.streamlit.io/streamlit/emoji-shortcodes) :eyes:")
    st.markdown("Google's [material symbols:](https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded) :sunglasses:")

    st.markdown("~~strikethrough~~")
    st.markdown("# Heading 1")
    st.markdown("## Heading 2") 
    st.markdown("### Heading 3") 
    st.markdown("#### Heading 4") 
    st.markdown("##### Heading 5") 
    st.markdown("###### Heading 6") 

    st.markdown("add a tooltip", help="my tool tip")


    st.markdown("and inline code `print(\"hello, world\")`")

    st.markdown(r"and inline latex: $ \pi \approx \frac{22}{7} $")


    st.markdown("And, by passing `unsafe_allow_html=True` you can render html... ur use st.html if you don't need css")
    st.markdown("like this... <ins>underlined text</ins>", unsafe_allow_html=True)

    st.html("st.html like mardown but allows text-decoration...s")
    st.html("underline, overline, line-through, none")
    st.html("solid, double, dotted, dashed, wavy")


    st.html(
        "<p><span style='text-decoration: line-through double red;'>Oops</span>!</p>"
    )

    st.html(
        "<p><span style='text-decoration: overline green;'>hello there</span></p>"
    )

    st.html(
        "<p><span style='text-decoration: underline wavy green;'>hello there</span></p>"
    )




def do_code():
    import textwrap

    st.markdown("using escaped quotes")
    code_frag = textwrap.dedent(r"""
        st.code("import ada\nprint(\"hello, ada\")\n")
    """)
    #st.code("import ada\\nprint(\"hello, ada\")\\n")
    #""")
    st.code(code_frag)
    st.code("import ada\nprint(\"hello, ada\")\n")



    st.markdown("using double quotes")
    code_frag = textwrap.dedent(r"""
        st.code('import lovelace\nprint("hello, lovelace")\n
    """)
    st.code(code_frag)
    st.code('import lovelace\nprint("hello, lovelace")')


    st.text("using triple quotes (and optionally textwrap.dedent)")

    # code_frag = r"""
    #     st.code(r\"""
    #     import ada, lovelace
    #     print("hello, world")
    #     \""")
    # """
    # st.code(code_frag)

    code_frag = textwrap.dedent(r"""
        st.code(\"""
            import ada, lovelace
            print("hello, ms ada lovelace")
        \""")
        """)
    st.code(code_frag)


    code_frag = textwrap.dedent(r"""
        import ada, lovelace
        print("hello, ms ada lovelace")
    """)
    st.code(code_frag)

    # st.code("""
    #     import ada, lovelace
    #     print("hello, world")
    # """)

def get_sample_dataframe(rows, cols):
    col_names = []
    for i in range(cols):
        col_names.append(f"col{i}")

    df = pd.DataFrame(np.arange(rows * cols).reshape(rows, cols), columns = col_names)
    return df


def do_input_1():
    st.title("Basic Inputs...")

    st.header("Example 1")
    st.markdown("[st.button](https://docs.streamlit.io/develop/api-reference/widgets/st.button) using [st.text_input](https://docs.streamlit.io/develop/api-reference/widgets/st.text_input)")
    # Remember to render widgets and then trigger action with button
    name = st.text_input("What is your name?", max_chars=99, width=399)
    age_text = st.text_input("Age", max_chars=4, width=99)
    make_younger = st.checkbox("Make me younger")
    age = None
    if age_text.isdigit():
        age = int(age_text)
    # 2. Use a button just to trigger the action
    if st.button("Submit"):
        if name and (age is not None):
            st.write(f"Hello, **{name}**")
            if make_younger:
                age = max(age - 10, 0)
            st.write(f"You are **{age}** years old.")
        elif name and age_text:
            st.warning("Please enter a valid number for age.")
            
    st.header("Example 2")
    name2 = st.text_input("Name")
    age2 = st.slider("Select your age:", 0, 120, 30)
    make_younger2 = st.checkbox("Make me younger (Section 2)")

    if st.button("Submit Section 2"):
        if make_younger2:
            age2 = max(age2 - 10, 0)
        st.success(f"Hello {name2}, you are **{age2}** years old.")



    st.header("button to download")
    st.write("download files with [st.download_button](https://docs.streamlit.io/develop/api-reference/widgets/st.download_button)")
    df = get_sample_dataframe(3,4)
    csv_data = df.to_csv()
    # df.to_csv().encode("utf-8")
    st.download_button(
        label = "download dataframe as csv",
        data = csv_data,
        file_name = "data.csv",
        mime="text/csv",
        icon=":material/download:",
    )

    st.header("button link out")
    # button link
    st.link_button("Go to nytimes.com (in new page)", "https://www.nytimes.com")

def do_input_2():
    st.header("select single")
    st.markdown("select from dropdown with [st.selectbox](https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox)")
    st.markdown("options include index, placeholder, accept_new_options")
    optionA = st.selectbox(
        "How would you like to be contacted?",
        ("Email", "Home phone", "Mobile phone"),
    )
    st.write("You selected:", optionA)

    optionB = st.selectbox(
        "Default email",
        ["foo@example.com", "bar@example.com", "baz@example.com"],
        index=None,
        placeholder="Select a saved email or enter a new one",
        accept_new_options=True,
    )
    st.write("You selected:", optionB)


    st.header("multiselect")

    # multiselect
    st.write("mutliselect with [st.multiselect](https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect)")
    # st.write('st.multiselect("what are your favorite colors?",["Green", "Yellow", "Red", "Blue"],default=["Yellow", "Red"])'
    st.code('st.multiselect("what are your favorite colors?",\n\t["Green", "Yellow", "Red", "Blue"],\n\tdefault=["Yellow", "Red"]\n)')
    options = st.multiselect(
        "What are your favorite colors?",
        ["Green", "Yellow", "Red", "Blue"],
        default=["Yellow", "Red"],
    )
    st.write("You selected:", options)


    st.header("multiselect + new")
    st.write("[st.multiselect](https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect) with max=5 and accept_new = True")
    options = st.multiselect(
        "What are your favorite cat names?",
        ["Jellybeans", "Fish Biscuit", "Madam President"],
        max_selections=5,
        accept_new_options=True,
    )
    st.write("You selected:", options)



    st.header("Radio")
    st.write("single select radio witih [st.radio_button](https://docs.streamlit.io/develop/api-reference/widgets/st.radio)")
    genre = st.radio(
        "What's your favorite movie genre",
        [":rainbow[Comedy]", "***Drama***", "Documentary :movie_camera:"],
        index=None,
    )
    st.write("You selected:", genre)



def do_input_3():
    st.header("pill buttons 1")
    st.write("pill button (multi select) with [st.pills](https://docs.streamlit.io/develop/api-reference/widgets/st.pills)")
    st.write("options... keys, formatting function, selection_mode (single/)")
    st.code('selection = st.pills("Directions", options, selection_mode="multi")')
    options = ["North", "East", "South", "West"]
    selection = st.pills("Directions", options, selection_mode="multi")
    st.markdown(f"Your selected options: {selection}.")



    st.header("pill buttons 2")
    st.code('selection = st.pills(option_map.keys(), format_func, selection_mode))')

    option_map = {
        0: ":material/add:",
        1: ":material/zoom_in:",
        2: ":material/zoom_out:",
        3: ":material/zoom_out_map:",
    }
    selection = st.pills(
        "or as icons and single selection",
        options=option_map.keys(),
        format_func=lambda option: option_map[option],
        selection_mode="single",
    )
    st.write(
        "Your selected option: "
        f"{None if selection is None else option_map[selection]}"
    )




def do_input_4():
    st.header("Color Picker")
    # pick a color
    st.write("pick a color with [st.color_picker](https://docs.streamlit.io/develop/api-reference/widgets/st.color_picker)")
    color = st.color_picker("Pick A Color", "#00f900")
    st.write("The current color is", color)


    # ODDITIES: feedback
    st.header("Ratings")
    st.write("rate with thumbs, stars, or smiles with [st.feedback](https://docs.streamlit.io/develop/api-reference/widgets/st.feedback)")
    sentiment_mappingA = ["one", "two", "three", "four", "five"]
    selectedA = st.feedback("stars")
    if selectedA is not None:
        st.markdown(f"You selected {sentiment_mappingA[selectedA]} star(s).")

    sentiment_mappingB = [":material/thumb_down:", ":material/thumb_up:"]
    selectedB = st.feedback("thumbs")
    if selectedB is not None:
        st.markdown(f"You selected: {sentiment_mappingB[selectedB]}")



# ENTRY

st.title("Streamlit Reminders")
verify_session()

# Initialize log in session state
if "log" not in st.session_state:
    st.session_state.log = []

st.markdown("[Streamlit.com](https://streamlit.io/) is great for quickly building interactive python apps!  I put this page together to learn/remember stuff.  No AI stuff here...- Jeremy")
#st.text("https://docs.streamlit.io/develop/api-reference")
#st.write("https://streamlit.io/")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Displaying", "Input Buttons", "Input Selectors", "Input Pills", "Misc Inputs", "Advanced"])

with tab1:
    #st.subheader("viewing...")
    col1, col2, col3, col4 = st.columns(4)
    
    btn_basics = col1.button("Basics")
    btn_markdown = col2.button("Markdown")
    btn_code = col3.button("Code")
    btn_dataframes = col4.button("pandas")

    # move to tab2    
    #col5, col6 = st.columns(2)
    #btn_latex = col5.button("Latex")

    if btn_basics:
        do_basics()
    if btn_markdown:
        do_markdown()
    if btn_code:
        do_code()
    if btn_dataframes:
        st.text("pandas and dataframes...")
        df = get_sample_dataframe(3,4)
        st.write(df)


with tab2:
    do_input_1()

with tab3:
    do_input_2()
with tab4:
    do_input_3()
with tab5:
    do_input_4()

with tab6:
    st.text("tab 6... here")

    with st.expander("click to expand"):
        st.write("This content is hidden until you click the expander.")
        #st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png")
    col7, col8 = st.columns(2)
    btn_latex = col7.button("Latex")
    if btn_latex:


        st.latex(r"\frac{22}{7} \approx \pi")

        st.latex(r"""
        \begin{array}{l}
        \textbf{Gradient Descent Algorithm} \\
        \hline
        \text{Initialize } \theta_0 \\
        \text{for } t = 0, 1, 2, \dots \text{ do} \\
        \qquad g_t = \nabla_\theta J(\theta_t) \\
        \qquad \theta_{t+1} = \theta_t - \alpha g_t \\
        \end{array}
        """)

st.write("[code](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/pages/001_streamlit_reminders.py)")
