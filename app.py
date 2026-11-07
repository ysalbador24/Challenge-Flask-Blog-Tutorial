import os
import sqlite3
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-change-this-key')
app.config['DATABASE'] = Path(__file__).resolve().parent / 'database.db'


def get_db_connection():
    """Open the SQLite database and allow column access by name."""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    try:
        posts = conn.execute('SELECT * FROM posts ORDER BY id').fetchall()
    finally:
        conn.close()
    return render_template('index.html', posts=posts)


@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                             (title, content))
                conn.commit()
            finally:
                conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')


def get_post(post_id):
    conn = get_db_connection()
    try:
        post = conn.execute('SELECT * FROM posts WHERE id = ?',
                            (post_id,)).fetchone()
    finally:
        conn.close()
    if post is None:
        abort(404)
    return post


@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            conn = get_db_connection()
            try:
                conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?',
                             (title, content, id))
                conn.commit()
            finally:
                conn.close()
            return redirect(url_for('index'))
    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM posts WHERE id = ?', (id,))
        conn.commit()
    finally:
        conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=5008, debug=True)
