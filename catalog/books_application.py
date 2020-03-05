#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
from flask import make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool
from database_setup import *
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import requests
import os
import sys

app = Flask(__name__)

# connect to client_id

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'item-catalog'

# Connect to Database and create database session

engine = create_engine('sqlite:///Books.db?check_same_thread=False',
                       poolclass=SingletonThreadPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token

@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits)for x in xrange(32))
    login_session['state'] = state

    # return "The current session state is %s" % login_session['state']

    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token

    if request.args.get('state') != login_session['state']:
        response = make_response(
            json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code

    request.get_data()
    code = request.data.decode('utf-8')

    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets(
            'client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;"\
    "border-radius: 150px;-webkit-border-radius: 150px;"\
    "-moz-border-radius: 150px;"> '
    flash('you are now logged in as %s' % login_session['username'])
    print 'done!'
    return output


# User Helper Functions
# create new user
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session['email']).one()
    return user.id

# get user information


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# get user id


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():

        # Only disconnect a connected user.

    access_token = login_session.get('access_token')
    if access_token is None:
        response = \
            make_response(json.dumps('Current user not connected.'),
                          401)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCategories'))
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':

        # Reset the user's sesson.

        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCategories'))
    else:

        # For whatever reason, the given token was invalid.

        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCategories'))


# Show all categories

@app.route('/')
@app.route('/categories/')
def showCategories():
    # query to get categories from database
    categories = session.query(Category).order_by(asc(Category.name))
    # protect the database from unwanted modifications
    if 'username' not in login_session:
        return render_template('publiccategories.html',
                               categories=categories)
    else:
        return render_template('categories.html', categories=categories)


# Create a new category

@app.route('/categories/new/', methods=['GET', 'POST'])
def newCategory():
    # add new category only if the user in login_session
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        # query to add category to the database
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        flash('Category %s Successfully added' % newCategory.name)
        session.commit()
        # after adding back to the main page
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


# Edit a category

@app.route('/categories/<int:category_id>/edit/', methods=['GET',
           'POST'])
def editCategory(category_id):
    # edit existing category only if the user in login_session
    if 'username' not in login_session:
        return redirect('/login')
    # query to get category from the database
    editedCategory = \
        session.query(Category).filter_by(id=category_id).one()
    # Authorize editing, only menu creator can edit thhe categories
    user = getUserInfo(login_session['user_id'])
    creator = getUserInfo(editedCategory.user_id)
    if creator.id != user.id:
        flash('You cannot edit this category')
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s'
                  % editedCategory.name)
            # after editing back to the main page
            return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html',
                               category=editedCategory)


# Delete a category

@app.route('/categories/<int:category_id>/delete/', methods=['GET',
           'POST'])
def deleteCategory(category_id):
    # delete existing category only if the user in login_session
    if 'username' not in login_session:
        return redirect('/login')
    # query to get category from the database
    categoryToDelete = \
        session.query(Category).filter_by(id=category_id).one()
    # Authorize deleting, only menu creator can delete thhe categories
    user = getUserInfo(login_session['user_id'])
    creator = getUserInfo(categoryToDelete.user_id)
    if creator.id != user.id:
        flash('You cannot delete this category')
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        # after deleting back to the main page
        return redirect(url_for('showCategories',
                        category_id=category_id))
    else:
        return render_template('deleteCategory.html',
                               category=categoryToDelete)


# Show a category menu

@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/menu/')
def showMenu(category_id):
    # query to get category from the database
    category = session.query(Category).filter_by(id=category_id).one()
    # find the menu creator
    creator = getUserInfo(category.user_id)
    # query to get all items in the above category from the database
    items = session.query(Book).filter_by(category_id=category_id).all()
    # protect the database from unwanted modifications
    if 'username' not in login_session or \
    creator.id != login_session['user_id']:
        return render_template('publicmenu.html', items=items,
                               category=category, creator=creator)
    return render_template('menu.html', items=items, category=category,
                           creator=creator)


# Create a new menu item(book)

@app.route('/categories/<int:category_id>/menu/new/', methods=['GET',
           'POST'])
def newMenuItem(category_id):
    # add new book only if the user in login_session
    if 'username' not in login_session:
        return redirect('/login')
    # query to get category from the database
    category = session.query(Category).filter_by(id=category_id).one()
    # get book information from the user
    if request.method == 'POST':
        newItem = Book(
            name=request.form['name'],
            file_link=request.form['file_link'],
            picture=request.form['picture'],
            author=request.form['author'],
            yearOfEmission=request.form['yearOfEmission'],
            numOfPage=request.form['numOfPage'],
            category_id=category.id,
            user_id=category.user_id,
            )
        session.add(newItem)
        session.commit()
        flash('New Book %s Successfully Created' % newItem.name)
        # after deleting back to the menu
        return redirect(url_for('showMenu', category_id=category_id))
    else:
        return render_template('newmenuitem.html',
                               category_id=category_id)


# Edit a menu item(book)

@app.route('/categories/<int:category_id>/menu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(category_id, menu_id):
    # edit book only if the user in login_session
    if 'username' not in login_session:
        return redirect('/login')
    # query to get item from the dtabase
    editedItem = session.query(Book).filter_by(id=menu_id).one()
    # query to get category from the database
    category = session.query(Category).filter_by(id=category_id).one()
    # Authorize editing, only menu creator can edit the book
    user = getUserInfo(login_session['user_id'])
    creator = getUserInfo(editedItem.user_id)
    if creator.id != user.id:
        flash('You cannot edit this book')
        return redirect(url_for('showCategories'))
    # get book information from the user
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['file_link']:
            editedItem.file_link = request.form['file_link']
        if request.form['picture']:
            editedItem.picture = request.form['picture']
        if request.form['author']:
            editedItem.author = request.form['author']
        if request.form['yearOfEmission']:
            editedItem.yearOfEmission = request.form['yearOfEmission']
        if request.form['numOfPage']:
            editedItem.numOfPage = request.form['numOfPage']
        session.add(editedItem)
        session.commit()
        flash('Book Successfully Edited')
        # after deleting back to the menu
        return redirect(url_for('showMenu', category_id=category_id))
    else:
        return render_template('editmenuitem.html',
                               category_id=category_id,
                               menu_id=menu_id, item=editedItem)


# Delete a menu item(book)

@app.route('/categories/<int:category_id>/menu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteMenuItem(category_id, menu_id):
    # delete book only if the user in login_session
    if 'username' not in login_session:
        return redirect('/login')
    # query to get category from the database
    category = session.query(Category).filter_by(id=category_id).one()
    # query to get item from the dtabase
    itemToDelete = session.query(Book).filter_by(id=menu_id).one()
    # Authorize editing, only menu creator can edit the book
    user = getUserInfo(login_session['user_id'])
    creator = getUserInfo(itemToDelete.user_id)
    if creator.id != user.id:
        flash('You cannot delete this book')
        return redirect(url_for('showCategories'))

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Book Successfully Deleted')
        # after deleting back to the menu
        return redirect(url_for('showMenu', category_id=category_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)


# JSON APIs to view Categories Information

@app.route('/categories/<int:category_id>/menu/JSON')
def category_menuJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Book).filter_by(category_id=category_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/categories/JSON')
def categorieJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


@app.route('/categories/<int:category_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(category_id, menu_id):
    Menu_Item = session.query(Book).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
