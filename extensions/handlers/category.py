from extensions.handlers import AbstractHandler


class Category(AbstractHandler):
	def __init__(self, site=None):
		self.site = site
		self.categories = dict()


	def analyse(self, page):
		if not 'category' in page.meta:
			return
		for cat in page.meta['category']:
			if not cat in self.categories:
				self.categories[cat] = list()
			self.categories[cat].append(page)


	def update(self, template):
		nav = ''
		for cat, pages in self.categories.items():
			page_html = ''
			for page in pages:
				page_html += '<li class="category-item">{}</li>'.format(page.filename)
			cat_html = '<a href="">{}</a>'.format(cat)
			nav += '<li class="category">{}<ul class="category-items">{}</ul></li>'.format(cat_html, page_html)
		nav = '<ul id="categories">' + nav + '</ul>'
		template.substitute(navigation=nav)
