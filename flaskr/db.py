import sqlite3
import click
from flask import current_app, g

def get_db():
    if 'db' not in g: # g is a special object that is unique for each request. It is used to store data that might be accessed by multiple functions during the request. The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES # This makes sure that the connection will return rows that behave like dicts. This allows accessing the columns by name.
        )
        g.db.row_factory = sqlite3.Row # This tells the connection to return rows that behave like dicts. This allows accessing the columns by name.
        
    return g.db

def close_db(e=None):
    db = g.pop('db', None) # g.pop() method returns the value of the item with the specified key, removes the item from the dictionary.
    
    if db is not None:
        db.close()
        
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
    
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)