from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Collection(Base):

    __tablename__ = 'collection'

    id = Column(Integer, primary_key=True)
    date = Column(String)
    items = relationship('CollectionItem', back_populates='collection')

    def __repr__(self):
        return "<Collection(id={}, dates={}-{}')>".format(self.id, self.start_date, self.end_date)


class CollectionItem(Base):

    __tablename__ = 'collection_item'

    collection = relationship('Collection', back_populates='items')

    id = Column(Integer, primary_key=True)
    collection_id = (Integer, ForeignKey('collections.id'))
    b_content_to_cat = Column(String)
    b_descr_blocks = Column(String)
    b_descr_blocks_item = Column(String)
    b_descr_text = Column(String)
    b_footer_search_also = Column(String)
    b_header_top = Column(String)
    b_home_footer = Column(String)
    b_left = Column(String)
    b_similar = Column(String)
    canonical = Column(String)
    description = Column(String)
    error = Column(String)
    h1 = Column(String)
    h2 = Column(String)
    h3 = Column(String)
    h_cf_ray = Column(String)
    h_connection = Column(String)
    h_content_encoding = Column(String)
    h_content_type = Column(String)
    h_date = Column(String)
    h_server = Column(String)
    h_set_cookie = Column(String)
    h_transfer_encoding = Column(String)
    keywords = Column(String)
    load_time = Column(Float)
    p_gsarticle_promo_aside = Column(String)
    p_gsarticle_promo_footer = Column(String)
    redirects = Column(String)
    robots = Column(String)
    robots_txt = Column(String)
    size = Column(Integer)
    status_code = Column(Integer)
    title = Column(String)
    url = Column(String)

    def __repr__(self):
        return "<CacheItem(id={}, url='{}')>".format(self.id, self.url)


class Cache(Base):

    __tablename__ = 'cache'

    pages = relationship('CachePage', back_populates='cache')

    id = Column(Integer, primary_key=True)
    start_date = Column(String)
    end_date = Column(String)
    noindex_1 = Column(Integer)
    redirects_1 = Column(Integer)
    errors_1 = Column(Integer)
    disallowed_1 = Column(Integer)
    noindex_2 = Column(Integer)
    redirects_2 = Column(Integer)
    errors_2 = Column(Integer)
    disallowed_2 = Column(Integer)

    b_content_to_cat = Column(Integer)
    b_descr_blocks = Column(Integer)
    b_descr_blocks_item = Column(Integer)
    b_descr_text = Column(Integer)
    b_footer_search_also = Column(Integer)
    b_header_top = Column(Integer)
    b_home_footer = Column(Integer)
    b_left = Column(Integer)
    b_similar = Column(Integer)
    canonical = Column(Integer)
    description = Column(Integer)
    error = Column(Integer)
    h1 = Column(Integer)
    h2 = Column(Integer)
    h3 = Column(Integer)
    headers = Column(Integer)
    keywords = Column(Integer)
    load_time = Column(Integer)
    p_gsarticle_promo_aside = Column(Integer)
    p_gsarticle_promo_footer = Column(Integer)
    redirects = Column(Integer)
    robots = Column(Integer)
    robots_txt = Column(Integer)
    size = Column(Integer)
    status_code = Column(Integer)
    title = Column(Integer)

    def __repr__(self):
        return "<Cache(id={}, dates={}-{}')>".format(self.id, self.start_date, self.end_date)


class CachePage(Base):

    __tablename__ = 'cache_page'

    id = Column(Integer, primary_key=True)
    cache_id = Column(Integer, ForeignKey('cache.id'))
    status_code = Column(Integer)
    url = Column(String)

    cache = relationship('Cache', back_populates='pages')

    b_content_to_cat = Column(Boolean)
    b_descr_blocks = Column(Boolean)
    b_descr_blocks_item = Column(Boolean)
    b_descr_text = Column(Boolean)
    b_footer_search_also = Column(Boolean)
    b_header_top = Column(Boolean)
    b_home_footer = Column(Boolean)
    b_left = Column(Boolean)
    b_similar = Column(Boolean)
    canonical = Column(Boolean)
    description = Column(Boolean)
    error = Column(Boolean)
    h1 = Column(Boolean)
    h2 = Column(Boolean)
    h3 = Column(Boolean)
    headers = Column(Boolean)
    keywords = Column(Boolean)
    load_time = Column(Boolean)
    p_gsarticle_promo_aside = Column(Boolean)
    p_gsarticle_promo_footer = Column(Boolean)
    redirects = Column(Boolean)
    robots = Column(Boolean)
    robots_txt = Column(Boolean)
    size = Column(Boolean)
    title = Column(Boolean)

    def __repr__(self):
        return "<CachePage(id={}, parent_id={}', url={})>".format(self.id, self.cache_id, self.url)


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(id={}, email={}')>".format(self.id, self.email)

