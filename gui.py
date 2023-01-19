__version__ = "0.2"
app_name = "Ask my PDF"

DEFAULT_TASK = """
Task: Answer question based on context.
"""

# BOILERPLATE

import streamlit as st
st.set_page_config(layout='centered', page_title=f'{app_name} {__version__}')
ss = st.session_state
if 'debug' not in ss: ss['debug'] = {}
import css
st.write(f'<style>{css.v1}</style>', unsafe_allow_html=True)
header1 = st.empty()
header2 = st.empty()
header3 = st.empty()

# IMPORTS

import pdf
import ai
import model

# COMPONENTS

def ui_about():
	st.markdown(f"""
	# Ask my PDF
	version {__version__}
	
	Proof of Concept question answering system built on top of GPT3.
	""")

def ui_author():
	st.write("""
		Made by [Maciej Obarski](https://www.linkedin.com/in/mobarski/)<br>
		aka [@KerbalFPV](https://twitter.com/KerbalFPV)"""
		, unsafe_allow_html=True)


def ui_alpha():
	st.markdown("""
		❤️ Thank you for your interest in my application.
		Please be aware that it is currently in an early alpha version
		and may contain bugs 🐛 or unfinished features.
		""")


def ui_spacer(n=2, line=False, next_n=0):
	for _ in range(n):
		st.write('')
	if line:
		st.tabs([' '])
	for _ in range(next_n):
		st.write('')

def ui_api_key():
	st.write('## 1. Enter your OpenAI API key')
	def on_change():
		ai.use_key(ss['api_key'])
	st.text_input('OpenAI API key', type='password', key='api_key', on_change=on_change, label_visibility="collapsed")

def ui_pdf_file():
	st.write('## 2. Upload your PDF file')
	pg = st.progress(0)
	def on_change():
		if ss['pdf_file']:
			pages = pdf.pdf_to_pages(ss['pdf_file'])
			if ss['fix_text']:
				for i in range(len(pages)):
					pages[i] = model.fix_text_errors(pages[i], pg)
			ss['vectors'] = model.index_pages(pages, pg)
			ss['texts'] = pages
			ss['debug']['pages'] = pages
			#ss['debug']['vectors'] = vectors
	disabled = not ss.get('api_key')
	uploaded_file = st.file_uploader('pdf file', type='pdf', key='pdf_file', disabled=disabled, on_change=on_change, label_visibility="collapsed")

def ui_show_debug():
	st.checkbox('show debug section', key='show_debug')

def ui_fix_text():
	st.checkbox('fix common text errors', value=True, key='fix_text')

def ui_temperature():
	st.slider('temperature', 0.0, 1.0, 0.0, 0.1, key='temperature', format='%0.1f')

def ui_max_pages():
	st.number_input('max pages', 1, 5, 3, key='max_pages')


def ui_hyde():
	st.checkbox('use HyDE', key='use_hyde')

def ui_task():
	st.text_area('task / persona', DEFAULT_TASK.strip(), key='task')


def ui_question():
	st.write('## 3. Ask questions')
	disabled = not ss.get('api_key')
	st.text_area('question', key='question', height=100, placeholder='Enter question here', help='', label_visibility="collapsed", disabled=disabled)

# REF: Hypotetical Document Embeddings
def ui_hyde_answer():
	# TODO: enter or generate
	pass

def ui_output():
	output = ss.get('output','')
	st.markdown(output)

def ui_debug():
	if ss.get('show_debug'):
		st.write('### debug')
		st.write(ss.get('debug',{}))


def b_ask():
	disabled = not ss.get('api_key')
	if st.button('get answer', disabled=disabled, type='primary'):
		text = ss.get('question','')
		temperature = ss.get('temperature', 0.0)
		hyde = ss.get('use_hyde')
		max_pages = ss.get('max_pages',1)
		task = ss.get('task')
		resp = model.query(text, ss, task=task, temperature=temperature, hyde=hyde, max_pages=max_pages, limit=5)
		ss['debug']['model.query.resp'] = resp
		
		q = text.strip()
		a = resp['text'].strip()
		output_add(q,a)

def b_clear():
	if st.button('clear output'):
		ss['output'] = ''

def output_add(q,a):
	if 'output' not in ss: ss['output'] = ''
	new = f'#### {q}\n{a}\n\n'
	ss['output'] = new + ss['output']

# LAYOUT

with st.sidebar:
	ui_about()
	ui_spacer(2)
	ui_author()
	ui_spacer(0,False,1)
	ui_alpha()
	ui_spacer(2)
	with st.expander('advanced'):
		ui_show_debug()
		b_clear()
		ui_temperature()
		ui_max_pages()
		ui_fix_text()
		ui_hyde()
		ui_task()

ui_api_key()
ui_pdf_file()
ui_question()
ui_hyde_answer()
b_ask()
ui_output()
ui_debug()


# Popraw poniższy tekst łącząc niektóre słowa tak aby tworzyły poprawne wyrazy. Staraj się jak najmniej zmienić tekst.
# Fix common OCR problems in the text below.