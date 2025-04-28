# import os
# os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"

# import streamlit as st
# from medpal import medpal, fetch_nearby_clinics

# st.set_page_config(page_title="MedPal Healthcare Assistant", page_icon="🩺")

# st.title("🩺 MedPal - Your Healthcare Companion")

# # Initialize session state variables if they don't exist
# if 'show_zip_input' not in st.session_state:
#     st.session_state.show_zip_input = False
# if 'zip_code' not in st.session_state:
#     st.session_state.zip_code = ""
# if 'show_clinics' not in st.session_state:
#     st.session_state.show_clinics = False

# user_input = st.text_input("Enter your health-related question:")

# if st.button("Ask MedPal"):
#     if user_input:
#         try:
#             with st.spinner("Thinking..."):
#                 answer, severity, synthetic_questions = medpal(user_input)
            
#             st.success(f"🧠 MedPal says:\n\n{answer}")
#             st.info(f"🚨 Estimated Severity: {severity} / 5")
            
#             # Display related questions
#             if synthetic_questions and len(synthetic_questions) > 0:
#                 st.subheader("You might also want to ask:")
#                 for question in synthetic_questions:
#                     st.write(f"• {question}")
            
#             # Set flag to show ZIP input if severity is high enough
#             if severity >= 2:
#                 st.session_state.show_zip_input = True
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")
#     else:
#         st.warning("Please enter a question!")

# # Outside the button action, check if we should display the ZIP input
# if st.session_state.show_zip_input:
#     st.write("Your symptoms seem serious. Enter ZIP code to find nearby clinics:")
#     zip_code = st.text_input("ZIP Code:", key="zip_input")
    
#     if zip_code:
#         if st.button("Find Clinics"):
#             clinics = fetch_nearby_clinics(zip_code)
#             st.write("🏥 Nearby Clinics:")
#             st.write(clinics)

import os
os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"

import streamlit as st
from medpal import medpal, fetch_nearby_clinics
import time

st.set_page_config(page_title="MedPal Healthcare Assistant", page_icon="🩺", layout="wide")

# ---- Custom background color ----
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #a3d5ff, #d0eaff);
        background-attachment: fixed;
        background-size: cover;
    }
    .stApp {
        background: linear-gradient(135deg, #a3d5ff, #d0eaff);
        background-attachment: fixed;
        background-size: cover;
    }
    .stButton>button {
        background-color: #0077b6;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    .stButton>button:hover {
        background-color: #005f86;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #f0f8ff;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---- Animated Welcome ----
placeholder = st.empty()
welcome_text = "Welcome to MedPal!"
animated_text = ""

for letter in welcome_text:
    animated_text += letter
    placeholder.markdown(f"<h1 style='text-align: center; color: #0077b6;'>{animated_text}</h1>", unsafe_allow_html=True)
    time.sleep(0.08)

st.write("")  # Add small spacer

# ---- Layout: 2 Columns ----
left_col, right_col = st.columns([1,2])

with left_col:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966487.png", width=150)  # Replace with your logo if you have one
    
    st.subheader("🔵 About MedPal")
    st.write(
        """
        MedPal is your trusted AI healthcare companion 🤖.  
        It provides general medical advice based on latest healthcare information.  
        
        **Note:** MedPal does not replace professional medical diagnosis or treatment.
        """)
    
    st.subheader("💡 Health Tip of the Day")
    st.success("Take short breaks every hour to stretch and rest your eyes!")

with right_col:
    st.subheader("💬 Enter your health-related question:")
    
    if 'show_zip_input' not in st.session_state:
        st.session_state.show_zip_input = False
    if 'zip_code' not in st.session_state:
        st.session_state.zip_code = ""
    if 'show_clinics' not in st.session_state:
        st.session_state.show_clinics = False

    user_input = st.text_input("Example: 'I have chest pain and shortness of breath'")

    if st.button("Ask MedPal"):
        if user_input:
            try:
                with st.spinner("Thinking..."):
                    answer, severity, synthetic_questions = medpal(user_input)
                
                st.success(f"🧠 MedPal says:\n\n{answer}")
                st.info(f"🚨 Estimated Severity: {severity} / 5")
                
                if synthetic_questions and len(synthetic_questions) > 0:
                    st.subheader("🔎 You might also want to ask:")
                    for question in synthetic_questions:
                        st.write(f"• {question}")
                
                if severity >= 2:
                    st.session_state.show_zip_input = True
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a question!")

    if st.session_state.show_zip_input:
        st.subheader("📍 Find nearby clinics")
        zip_code = st.text_input("Enter your ZIP code:", key="zip_input")
        
        if st.button("Find Clinics"):
            clinics = fetch_nearby_clinics(zip_code)
            st.success("🏥 Nearby Clinics:")
            st.write(clinics)
