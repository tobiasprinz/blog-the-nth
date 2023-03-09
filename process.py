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


	def to_html(self):
		return markdown.markdown(self.content)

	def __repr__(self):
		return 'Page(filename="{}")'.format(filename)


class Site():
	def __init__(self, pages=None, template=None):
		self.pages = pages
		if not pages:
			self.pages = list()

		self.template = template
		self.handlers = [CategoryHandler(site=self)]

	def add_page(self, page):
		self.pages.append(page)

	def get_page(self, filename):
		filtered = filter(lambda p: p.filename == filename, self.pages)
		if not filtered:
			return None
		return next(filtered)

	def prep(self):
		for page in self.pages:
			for handler in self.handlers:
				handler.analyse(page)

		for handler in self.handlers:
			handler.update(self.template)

	def get_rendered_page(self, filename):
		p = self.get_page(filename)
		rendered = self.template.substitute(
			content=p.to_html(),
			title=p.filename,
		)
		return rendered

	def get_all_pages(self):
		return {p.filename: p for p in self.pages}

	def get_all_rendered_pages(self):
		return {p.filename: p.to_html() for p in self.pages}

	def write(self):
		pages = self.get_all_rendered_pages()
		for filename, html in pages:
			output_filename = filename.replace('input', 'output').replace('.md', '.html')  # TODO: regex to avoid replacing input/appreciate_my_input.md
			with open("output_filename.html", "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
				output_file.write(html)
			print('Writing {}'.format(output_filename))

	def __str__(self):
		return 'Site(pages=[{}])'.format(', '.join(self.pages))


#------------------- TODO: MAKE THIS A MAIN -------------------#
input_files = glob.glob('input/*.md')

with open('extensions/templates/default.html') as tmpl:
	site = Site(template=Template(tmpl.read()))

for filename in input_files:
	page = Page.from_file(filename)
	site.add_page(page)

site.prep()
site.write()