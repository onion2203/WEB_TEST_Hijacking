from flask import Blueprint, render_template, request, session

home_router = Blueprint('home', __name__)

@home_router.route('/home')
def home():
    if session.get('logged_in'):
        return render_template('home.html')
    else:
        return render_template('login.html')

# Note search feature
@home_router.route('/search')
def search():
    if session.get('logged_in'):
        sanitized_q = request.args.get('q', '').replace('<script>', '').replace('</script>', '')
        html = f'Your search - <b>{sanitized_q}</b> - did not match any notes.<br><br>'
        return html
    else:
        return render_template('login.html')
