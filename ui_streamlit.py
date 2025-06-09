import streamlit as st
from main import build_workflow_manager

manager = build_workflow_manager()

st.title("Agent Workflow Demo")

if 'stage' not in st.session_state:
    st.session_state.stage = 'prompt'
    st.session_state.prompt = ''
    st.session_state.answer = ''
    st.session_state.log = []

if st.session_state.stage == 'prompt':
    st.session_state.prompt = st.text_input('Enter your request:')
    if st.button('Start') and st.session_state.prompt:
        clarifier = manager.agents['Clarifier']
        res = clarifier.run_with_retries(st.session_state.prompt)
        st.session_state.log.append(('Clarifier', res['output']))
        st.session_state.clarifier_question = res['output']
        st.session_state.stage = 'clarifier'

elif st.session_state.stage == 'clarifier':
    st.write('Clarifier asks:', st.session_state.clarifier_question)
    st.session_state.answer = st.text_input('Your answer:')
    if st.button('Continue') and st.session_state.answer:
        clarified = f"{st.session_state.prompt} | {st.session_state.answer}"
        manager.run_workflow('Designer', clarified)
        st.session_state.stage = 'done'

if st.session_state.stage == 'done':
    st.write('Workflow complete. See console for details.')

