from flask import render_template, request, Response, flash, redirect, url_for
from fyyurapp.models import Venue, Artist, Show
from fyyurapp.forms import *
from fyyurapp import app, db
import logging
from logging import Formatter, FileHandler
import sys


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    venues = Venue.query.order_by(db.desc(Venue.created_at)).limit(10).all()
    artists = Artist.query.order_by(db.desc(Artist.created_at)).limit(10).all()
    return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    all_venues = Venue.query.all()

    data = []
    for venue in all_venues:
        venue_area = {
            "city": venue.city,
            "state": venue.state
        }

        venues = Venue.query.filter_by(
            city=venue.city, state=venue.state).all()

        # getting individual venue by city and state
        specific_venues = []
        now = datetime.now
        for venue in venues:
            venue_shows = Show.query.filter_by(venue_id=venue.id).all()
            num_of_upcoming_show = 0
            for show in venue_shows:
                if show.start_time > now():
                    num_of_upcoming_show += 1
            specific_venues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": num_of_upcoming_show
            }
            )
            venue_area['venues'] = specific_venues
        data.append(venue_area)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "")

    response = {}

    name_search = Venue.name.ilike(f"%{search_term}%")
    state_search = Venue.state.ilike(f"%{search_term}%")
    city_search = Venue.city.ilike(f"%{search_term}%")
    venues = list(Venue.query.filter(
        name_search | state_search | city_search).all())
    response['count'] = len(venues)
    response["data"] = []
    now = datetime.now
    for venue in venues:
        venue_shows = Show.query.filter_by(venue_id=venue.id).all()
        num_of_upcoming_show = 0
        for show in venue_shows:
            if show.start_time > now():
                num_of_upcoming_show += 1
        specific_venue = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_of_upcoming_show
        }
        response["data"].append(specific_venue)

        return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    # converting genre string back to array
    setattr(venue, "genres", venue.genres.split(","))

    # getting the past shows
    past_shows = []
    for show in venue.shows:
        if show.start_time < datetime.now():
            past_shows.append(show)

    shows_detail = []
    for show in past_shows:
        show_info = {}
        show_info["artist_name"] = show.artists.name
        show_info["artist_id"] = show.artists.id
        show_info["artist_image_link"] = show.artists.image_link
        show_info["start_time"] = show.start_time.strftime(
            "%m/%d/%Y, %H:%M:%S")
        shows_detail.append(show_info)

    setattr(venue, "past_shows", shows_detail)
    setattr(venue, "past_shows_count", len(past_shows))

    # getting future shows

    upcoming_shows = []
    for show in venue.shows:
        if show.start_time > datetime.now():
            upcoming_shows.append(show)

    artist_shows = []
    for show in upcoming_shows:
        artist_info = {}
        artist_info["artist_name"] = show.artists.name
        artist_info["artist_id"] = show.artists.id
        artist_info["artist_image_link"] = show.artists.image_link
        artist_info["start_time"] = show.start_time.strftime(
            "%m/%d/%Y, %H:%M:%S")
        artist_shows.append(artist_info)

    setattr(venue, "upcoming_shows", artist_shows)
    setattr(venue, "upcoming_shows_count", len(upcoming_shows))

    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    try:
        newVenue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            # convert array to string separated by commas
            genres=",".join(request.form['genres']),
            facebook_link=request.form['facebook_link'],
            image_link=request.form['image_link'],
            seeking_talent=request.form['seeking_talent'],
            seeking_description=request.form['seeking_description'],
            website_link=request.form['website_link']
        )

        db.session.add(newVenue)
        db.session.commit()
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')

    except Exception as e:
        print(e)
        db.session.rollback()

        flash('An error occurred. Venue' + ' could not be listed.')

    finally:
        db.session.close()

    return redirect(url_for("index"))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    # return None

    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash("Venue " + venue.name + " was deleted successfully!")
    except:
        db.session.rollback()

        flash("Venue was not deleted successfully.")
    finally:
        db.session.close()

    return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # solutions
    artists = db.session.query(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')

    name_search = Artist.name.ilike(f"%{search_term}%")
    city_search = Artist.city.ilike(f"%{search_term}%")
    state_search = Artist.state.ilike(f"%{search_term}%")

    artists = Artist.query.filter(
        name_search | city_search | state_search).all()
    response = {
        "count": len(artists),
        "data": []
    }

    for artist in artists:
        artist_info = {}
        artist_info["name"] = artist.name
        artist_info["id"] = artist.id

        upcoming_shows = 0
        for show in artist.shows:
            if show.start_time > datetime.now():
                upcoming_shows = upcoming_shows + 1
        artist_info["upcoming_shows"] = upcoming_shows

        response["data"].append(artist_info)

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.get(artist_id)

    # converting  genre string back to array
    setattr(artist, "genres", artist.genres.split(","))

    # get past shows
    past_shows = list(filter(lambda show: show.start_time <
                      datetime.now(), artist.shows))

    shows_venue = []
    for show in past_shows:
        venue_info = {}
        venue_info["venue_name"] = show.venues.name
        venue_info["venue_id"] = show.venues.id
        venue_info["venue_image_link"] = show.venues.image_link
        venue_info["start_time"] = show.start_time.strftime(
            "%m/%d/%Y, %H:%M:%S")

        shows_venue.append(venue_info)

    setattr(artist, "past_shows", shows_venue)
    setattr(artist, "past_shows_count", len(past_shows))

    # get upcoming shows
    upcoming_shows = list(
        filter(lambda show: show.start_time > datetime.now(), artist.shows))
    shows_venue = []
    for show in upcoming_shows:
        venue_info = {}
        venue_info["venue_name"] = show.venues.name
        venue_info["venue_id"] = show.venues.id
        venue_info["venue_image_link"] = show.venues.image_link
        venue_info["start_time"] = show.start_time.strftime(
            "%m/%d/%Y, %H:%M:%S")

        shows_venue.append(venue_info)

    setattr(artist, "upcoming_shows", shows_venue)
    setattr(artist, "upcoming_shows_count", len(upcoming_shows))

    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>

    artist = Artist.query.get(artist_id)
    # convert genre string back to array
    request.form['genres'] = artist.genres.split(",")

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        artist = Artist.query.get(artist_id)

        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        # convert array to string separated by commas
        artist.genres = ",".join(request.form['genres'])
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        artist.seeking_venue = request.form['seeking_venue']
        artist.seeking_description = request.form['seeking_description']
        artist.website_link = request.form['website_link']

        db.session.add(artist)
        db.session.commit()
        flash("Artist " + artist.name + " was successfully edited!")
    except:
        db.session.rollback()
        flash("Artist was not edited successfully.")
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    # converting genre string back to array
    form.genres.data = venue.genres.split(",")

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)

    try:
        venue = Venue.query.get(venue_id)

        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        # convert array to string separated by commas
        venue.genres = ",".join(request.form['genres'])
        venue.facebook_link = request.form['facebook_link']
        venue.image_link = request.form['image_link']
        venue.seeking_talent = request.form['seeking_talent']
        venue.seeking_description = request.form['seeking_description']
        venue.website_link = request.form['website_link']

        db.session.add(venue)
        db.session.commit()

        flash("Venue " + form.name.data + " edited successfully")

    except Exception:
        db.session.rollback()
        flash("Venue was not edited successfully.")
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    try:
        newArtist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            # convert array to string separated by commas
            genres=",".join(request.form['genres']),
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            website_link=request.form['website_link'],
            seeking_venue=request.form['seeking_venue'],
            seeking_description=request.form['seeking_description'],
        )
        db.session.add(newArtist)
        db.session.commit()
        flash("Artist " + request.form["name"] +
              " was successfully listed!")
    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Artist was not successfully listed.")
    finally:
        db.session.close()
    return redirect(url_for("index"))

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows
    # TODO: replace with real venues data.
    data = []

    shows = Show.query.all()
    for show in shows:
        show_info = {}
        show_info["venue_id"] = show.venues.id
        show_info["venue_name"] = show.venues.name
        show_info["artist_id"] = show.artists.id
        show_info["artist_name"] = show.artists.name
        show_info["artist_image_link"] = show.artists.image_link
        show_info["start_time"] = show.start_time.strftime(
            "%m/%d/%Y, %H:%M:%S")

        data.append(show_info)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    try:
        new_show = Show(
            artist_id=request.form['artist_id'],
            venue_id=request.form['venue_id'],
            start_time=request.form['start_time']
        )
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except Exception:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')
