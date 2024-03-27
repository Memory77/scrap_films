import scrapy
from imdb.items import AllocFilmsItem

class AllocFilmsSpider(scrapy.Spider):
    name = "alloc_films"
    allowed_domains = ["www.allocine.fr"]
    start_urls = ["https://www.allocine.fr/films/decennie-2020/"]

    #fonction doit s'occuper de parcourir la liste des produits sur chaque page et de suivre le lien de chaque produit
    #pour obtenir plus de détails.
    def parse(self, response):
        films = response.css('li.mdl')
        for film in films: #on parcours chaque film 
            titre = film.css('a.meta-title-link::text').get()
            film_url = film.css('a.meta-title-link::attr(href)').get() #on prend le href a chaque film
            # yield {
            #     'title': titre,
            #     'url': film_url
            # }
            
            
            yield response.follow(film_url, self.parse_product, meta = {'titre': titre})

        current_page = response.meta.get('current_page', 1)
        next_page = current_page + 1

        if next_page <= 975:
            next_page_url = f"https://www.allocine.fr/films/decennie-2020/?page={next_page}"
            yield scrapy.Request(next_page_url, callback=self.parse, meta={'current_page': next_page})


    #fonction est appelée pour parcourir chaque page de film. 
    def parse_product(self, response):
        titre = response.meta.get('titre')
        
        film_item = AllocFilmsItem()

        film_item['titre'] = titre
        film_item['box_office_url'] = response.urljoin(response.css('a[title="Box Office"]::attr(href)').get())
        # film_item['titre_original'] = response.css('h1 span.hero__primary-text::text').get()
        # film_item['score'] = response.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]//span/text()').get()
        # film_item['genre'] = response.css('span.ipc-chip__text::text').getall()
        # film_item['year'] = response.css('a[href*="releaseinfo"]::text').get()
        # film_item['duree'] = response.css('.ipc-inline-list__item::text').get()
        # film_item['description'] = response.xpath('//span[@data-testid="plot-l"]/text()').get()
        # film_item['acteurs'] = response.xpath('//div[@data-testid="title-cast-item"]//a[@data-testid="title-cast-item__actor"]/text()').extract()
        # film_item['langue_origine'] = response.xpath('//a[contains(@class, "ipc-metadata-list-item__list-content-item") and contains(@href, "primary_language")]/text()').get()
        # film_item['pays'] = response.css('li[data-testid="title-details-origin"] .ipc-metadata-list-item__list-content-item--link::text').get()
        # film_item['public'] = response.css('a[href*="certificates"]::text').get()
        # film_item['directeur'] = response.css('li.ipc-metadata-list__item:contains("Director") a::text').get()

        yield film_item
        
        if film_item['box_office_url']:
            yield response.follow(film_item['box_office_url'], callback=self.parse_box_office, meta={'film_item': film_item})


    def parse_box_office(self, response):
        #'response.meta' pour accéder aux métadonnées transmises
        film_item = response.meta['film_item']

        premiere_entree = response.css('table.box-office-table tr.responsive-table-row:first-of-type td:nth-child(2)::text').get()
        if premiere_entree:
            premiere_entree = premiere_entree.strip().replace('\xa0', '').replace(' ', '')
        film_item['entrees'] = premiere_entree
        
        yield film_item
