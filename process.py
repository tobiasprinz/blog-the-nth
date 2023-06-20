import glob
import markdown
import re
from string import Template
from extensions.handlers.category import Category as CategoryHandler


META_APPENDIX_PATTERN = re.compile(r'\n-+\n((?:\s*.+?\s*:\s*.+?\s*\n)+)')
META_KV_PATTERN = re.compile(r'^\s*(.+?)\s*:\s*(.+?)\s*$')


class Page:
	def __init__(self, raw_content=None, content=None, meta=None, filename=None):
		self.content = content
		self.meta = meta
		self.raw_content = raw_content
		self.filename = filename


	@classmethod
	def from_file(cls, filename):
		with open(filename) as file:
			raw_content = file.read()
		content = '\n'.join(raw_content.splitlines())  # make all newlines unix style
		content = re.sub('\n+$', '\n', content)  # remove newlines at EOF
		meta = cls.extract_meta(content)
		content = cls.cut_off_meta(content)
		return Page(raw_content=raw_content, content=content, meta=meta, filename=filename)


	@classmethod
	def extract_meta(cls, content):
		matcher = re.search(META_APPENDIX_PATTERN, content)
		if not matcher:
			return None

		meta = dict()
		meta_lines = matcher.group(1).splitlines()
		for line in meta_lines:
			matcher = re.search(META_KV_PATTERN, line)
			key = matcher.group(1)
			val =  matcher.group(2)
			if not key in meta:
				meta[key] = []
			meta[key].append(val)
		return meta


	@classmethod
	def cut_off_meta(cls, content):
		return re.sub(META_APPENDIX_PATTERN, '', content)

	def get_title(self):
		return page.raw_content.splitlines()[0]

	def to_html(self):
		return markdown.markdown(self.content)

	def __repr__(self):
		return 'Page(filename="{}")'.format(filename)



def insert_page_into_template(page=None, template='default.html'):
	with open('extensions/templates/' + template, "r") as text_file:
	     template =  Template(text_file.read())
	return template.substitute(content=page.to_html(), title=page.get_title(), navigation=None)


def write_page(page):
	output_filename = page.filename.replace('input', 'output').replace('.md', '.html')  # TODO: regex to avoid replacing input/appreciate_my_input.md
	page_content = insert_page_into_template(page=page, template='default.html')
	with open(output_filename, "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
		output_file.write(page_content)
	print('Writing {}'.format(output_filename))


#------------------- TODO: MAKE THIS A MAIN -------------------#
input_files = glob.glob('input/*.md')

for filename in input_files:
	page = Page.from_file(filename)
	write_page(page)