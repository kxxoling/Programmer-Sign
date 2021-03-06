import json

from flask import Blueprint
from flask import render_template, jsonify, abort
from flask import url_for, request
from flask import g, session
from flask import current_app

from ..models import Sigh
from ..forms import SighForm, CommentForm
from ..models import Comment
from ..models import User
from ..models import Tag


front_views = Blueprint('front', __name__, url_prefix='/')


@front_views.before_request
def get_site_info():
    g.user_count = User.query.count()
    g.comment_count = Comment.query.count()
    g.sigh_count = Sigh.query.count()
    g.tag_count = Tag.query.count()
    g.friend_links  = current_app.config['FRIEND_LINKS']


@front_views.before_request
def get_current_user():
    g.user_id = session.get('user_id')

    def get_current_user():
        if g.user_id is None:
            return None
        return User.query.get(g.user_id)
    g.current_user = get_current_user()


@front_views.route('/')
@front_views.route('<int:page_num>/')
def index(page_num=1):
    sighs_pagination = Sigh.query.order_by(Sigh.create_time.desc()).paginate(page_num, per_page=20, error_out=True)
    return render_template('index.jade', page_title='Programmer sighs!', sighs_pagination=sighs_pagination)


@front_views.route('search/sigh')
def search_sigh():
    q = request.args.get('q')
    g.q = q
    page_num = request.args.get('page_num', 1)
    sighs_pagination = Sigh.query.whoosh_search(q).paginate(page_num, per_page=20, error_out=True)

    return render_template('search.jade', page_title='Programmer sighs!', sighs_pagination=sighs_pagination)


@front_views.route('sigh/<int:sigh_id>/')
def render_sigh(sigh_id):
    sigh = Sigh.query.get_or_404(sigh_id)
    comments = sigh.comments

    # users_on_page = [comment.creator.username for comment in comments]
    # if sigh.creator.username not in users_on_page:
    #     users_on_page.append(sigh.creator.username)

    return render_template('sigh.jade', page_title='Programmer sighs!',
                           sigh=sigh, comments=comments)


@front_views.route('new/', methods=['POST'])
def post_sigh():
    """TODO: Should be login required later"""

    form = SighForm(request.form)
    if form.validate():
        sigh = form.save(creator_id=g.user_id)
        return jsonify(dict(
            sigh_id=sigh.id_,
            redirect_url=url_for('front.render_sigh', sigh_id=sigh.id_),
        ))
    else:
        return jsonify(form.errors), 405


@front_views.route('sigh/<int:sigh_id>/comment/', methods=['POST'])
def post_comment(sigh_id):
    """TODO: Should be login required later"""
    form = CommentForm(request.form)
    if form.validate():
        comment = form.save(creator_id=g.user_id, sigh_id=sigh_id)
        return comment.to_json('creator_id', 'content', 'id_', 'create_time', 'sigh_id')
    else:
        return jsonify(form.errors), 405


@front_views.route('tag/')
def render_tags():
    tags = Tag.query.all()
    return render_template('tags.jade', tags=tags)


@front_views.route('tag/<int:tag_id>/', endpoint='get_sighs_by_tag')
@front_views.route('tag/<int:tag_id>/<int:page_num>/')
def get_sighs_by_tag(tag_id, page_num=1):
    tag = Tag.query.get_or_404(tag_id)
    sighs_pagination = Sigh.query.filter_by(id_=tag.id_)\
                           .order_by(Sigh.create_time.desc())\
                           .paginate(page_num, per_page=20, error_out=True)
    return render_template('tag.jade', tag=tag, sighs_pagination=sighs_pagination)


@front_views.route('u/<int:user_id>/')
@front_views.route('u/<username>/')
def render_profile(user_id=None, username=None):
    if user_id is not None:
        user = User.query.get_or_404(user_id)
    elif username is not None:
        user = User.get_or_404(username=username)
    else:
        abort(404)

    page_num, per_page = 1, 20
    sighs_pagination = Sigh.query.filter_by(creator_id=user_id)\
            .order_by(Sigh.create_time.desc())\
            .paginate(page_num, per_page=20, error_out=True)
    comments_pagination = Comment.query.filter_by(creator_id=user_id)\
            .order_by(Comment.create_time.desc())\
            .paginate(page_num, per_page=20, error_out=True)

    return render_template('profile.jade', user=user,
                           sighs_pagination=sighs_pagination,
                           comments_pagination=comments_pagination)
