from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Paste(Base):
    __tablename__ = 'pastes'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    author = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    syntax = Column(Text, nullable=False)
    content = Column(Text, nullable=False)

    @property
    def nice_syntax(self):
        if not self.syntax:
            return u"plain-text"

        return self.syntax

    @property
    def nice_title(self):
        if not self.title:
            return u"unnamed " + self.nice_syntax

        return self.title

    @property
    def nice_author(self):
        if not self.author:
            return u"anon"

        return self.author

    # TODO this sucks and doesn't belong here and etc but whatever.
    @classmethod
    def search(cls, terms):
        """Given the user's input, returns a list of 3-tuples: blog post object,
        a list of fragments containing search terms with <span class="highlight">
        </span> around the search terms and the blog title also containing
        <span class="highlight"></span> around each search term. """

        # search_vector is a ts_vector column. To search for terms, you use the
        # @@ operator. plainto_tsquery turns a string into a query that can be
        # used with @@. So this adds a where clause like "WHERE search_vector
        # @@ plaint_tsquery(<search string>)"
        q = session.query(cls).filter(
            cls.__tablename__ + '.search_vector @@ plainto_tsquery(:terms)')
        q = q.params(terms=terms)

        # This adds an extra column containing a "headline" (bunch of
        # fragments) using the postgresql function ts_headline. The 4th
        # argument is a string giving options to the function. StartSel and
        # StopSel give the strings the search terms will be highlighted with.
        # MaxFragments gives the maximum number of fragments returned and
        # FragmentDelimiter give a string that will separate the fragments. We
        # use this to split the fragments into a list later.
        # TODO the docs suggest that using ts_headline here will call it for
        # every row (expensive!) *before* a LIMIT is applied.  but this doesn't
        # actually support a limit yet, so.
        # TODO splitting on ||| is pretty fuckin hokey, especially when the
        # documents are code.  i don't like the before/after tokens either; xss
        # problems ahoy.
        # TODO both of these problems are solved if we just do the highlighting
        # in-process, though then we lose any e.g. stemming, but for pastes maybe
        # that makes more sense
        q = q.add_column(
            func.ts_headline(
                'pg_catalog.english',
                cls.content,
                func.plainto_tsquery(terms),
                'MaxFragments=5,FragmentDelimiter=|||,'
                    'StartSel="<span class=""highlight"">",'
                    'StopSel="</span>",',
                type_=Text))

        # This is very similar to above, only instead of using fragments, we
        # pass the option HighlightAll=TRUE which means the whole field will be
        # returned with highlighting instead of a section of the title.
        q = q.add_column(
            func.ts_headline('pg_catalog.english',
                cls.title,
                func.plainto_tsquery(terms),
                'HighlightAll=TRUE,'
                    'StartSel="<span class=""highlight"">",'
                    'StopSel="</span>"',
                type_=Text))

        # This calls ts_rank_cd with the search_vector and the query and gives
        # a ranking to each row. We order by this descending. Again, the :terms
        # placeholder is used to insert user input.
        q = q.order_by('ts_rank_cd(pastes.search_vector, plainto_tsquery(:terms)) DESC')

        # Because of the two add_column calls above, the query will return a
        # 3-tuple consisting of the actual entry objects, the fragments for the
        # contents and the highlighted headline. In order to make the fragments
        # a list, we split them on '|||' - the FragmentDelimiter.
        return [(entry, fragments.split('|||'), title) for entry, fragments, title in q]


# thanks! http://lowmanio.co.uk/blog/entries/postgresql-full-text-search-and-sqlalchemy/
def setup_fulltext(event, schema_item, bind):
    # SQLA won't understand this column; add it manually
    bind.execute("ALTER TABLE pastes ADD COLUMN search_vector tsvector")

    # This indexes the tsvector column
    bind.execute("""CREATE INDEX pastes_search_index ON pastes USING gin(search_vector)""")

    # This sets up the trigger that keeps the tsvector column up to date.
    bind.execute("""
        CREATE TRIGGER pastes_search_update
        BEFORE UPDATE OR INSERT ON pastes
        FOR EACH ROW
        EXECUTE PROCEDURE tsvector_update_trigger('search_vector', 'pg_catalog.english', 'content', 'title')
    """)

Paste.__table__.append_ddl_listener('after-create', setup_fulltext)





### Core stuff

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True, index=True)
