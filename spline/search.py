from whoosh.fields import ID, DATETIME, TEXT, Schema

schema = Schema(
    id=ID(stored=True),
    type=ID(stored=True),
    creator_id=ID(stored=True),
    timestamp=DATETIME(),
    # TODO what about stuff with multiple contents
    # TODO what about pastebin which should really use a source-code analyzer
    content=TEXT(),
)

search_source_registry = {}

def register_for_fulltext_search(orm_class, name, creator_id, timestamp, content):
    # TODO make me work
    pass
