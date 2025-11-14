import streamlit as st

st.title("Add Two Numbers ➕")

a = st.number_input("Enter first number:", value=0.0)
b = st.number_input("Enter second number:", value=0.0)

if st.button("Add"):
    st.success(f"The sum is {a + b}")
