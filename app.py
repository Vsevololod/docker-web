from flask import *
from flask_bootstrap import Bootstrap
from flask_ldap import LDAP
from flask_ldap import login_required
import requests
import docker

app = Flask(__name__)
Bootstrap(app)
app.debug = True

app.config['LDAP_HOST'] = '195.19.252.68'
app.config['LDAP_DOMAIN'] = 'cc.spbu.ru'
app.config['LDAP_SEARCH_BASE'] = 'CN=Users,DC=cc,DC=spbu,DC=ru'
app.config['LDAP_REQUIRED_GROUP'] = 'CN=docker,CN=Users,DC=cc,DC=spbu,DC=ru'

ldap = LDAP(app)
app.secret_key = "welfhwdlhwdlfhwelfhwlehfwlehfelwehflwefwlehflwefhlwefhlewjfhwelfjhweflhweflhwel"
app.add_url_rule('/login', 'login', ldap.login, methods=['GET', 'POST'])


@app.route('/')
@login_required
def index():
    if 'username' in session:
        if 'volume' in session:
            return redirect("/run_containers".format(escape(session['username'])))

        else:
            return redirect("/virtual_drive_setup")
    return 'You are not logged in'


@app.route('/run_containers', methods=['GET'])
@login_required
def run_get():
    if 'username' in session:
        r = requests.get('https://docker-hub.cc.spbu.ru/v2/_catalog')

        cont = r.json()['repositories']
        return render_template("settings.html", name=session["username"], volume=session["volume"], containers=cont)
    return 'error'


@app.route('/run_containers', methods=['POST'])
@login_required
def run_post():
    if 'username' in session:
        cli = docker.APIClient(base_url='unix://var/run/docker.sock')
        container_name = request.form.get("container")
        full_container_name = "docker-hub.cc.spbu.ru:443/" + container_name
        pull_res = cli.pull(full_container_name)
        command = request.form.get("command")
        create_instance = cli.create_container(full_container_name, command,
                                               volumes=["/test"],
                                               name=session['username'] +"_"+ container_name,
                                               host_config=cli.create_host_config(binds={
                                                   session["volume"]: {
                                                       'bind': '/test',
                                                       'mode': 'rw',
                                                   }}),
                                               )
        cli.start(create_instance["Id"])

        return str(create_instance)
    return 'error'


@app.route('/virtual_drive_setup', methods=['POST'])
@login_required
def virtual_drive_setup_post():
    if 'username' in session:

        url2 = request.form.get("url")
        name2 = request.form.get("name")
        pass2 = request.form.get("pass")
        path2 = request.form.get("path")
        r2 = requests.request('PROPFIND', url2, auth=(name2, pass2))
        if 199 < r2.status_code < 300:
            cli = docker.APIClient(base_url='unix://var/run/docker.sock')
            volume = cli.create_volume(name=name2 + "_user_cont", driver='fentas/davfs',
                                       driver_opts={
                                           'url': "https://{}:{}@{}/{}".format(name2, pass2, url2[8:], path2),
                                           'uid': '1000',
                                           'gid': '1000',
                                       },
                                       labels={"key": "value"})
            session["volume"] = volume["Name"]
            return redirect('/run_containers')
        return redirect("/virtual_drive_setup")
    return 'error'


@app.route('/virtual_drive_setup', methods=['GET'])
@login_required
def virtual_drive_setup_get():
    if 'username' in session:
        return render_template("virtual_drive_setup.html", user=session["mail"])
    return 'error'



if __name__ == '__main__':
    app.run()
