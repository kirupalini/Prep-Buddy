from flask import Flask,redirect,url_for,request,make_response,render_template,session,flash,g
import upload
import syllabus_summ
import chatbot1
import highlight
import os
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
from werkzeug.utils import secure_filename
from flask import send_file,send_from_directory
import search
import syllabus_summ1
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
app = Flask(__name__)
tmp_FOLDER = './tmp'
app.config['tmp'] = tmp_FOLDER
UPLOAD_FOLDER = './Upload Folder'
app.config['upload'] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'notesviewer'
mysql = MySQL(app)
bcrypt = Bcrypt()
import test1
@app.before_request
def before_request():
    g.username = None
    if 'username' in session:
        g.username = session['username']

@app.route('/authentication',methods=['POST','GET'])
def authenticate():
    if request.method == 'POST':
        uname = request.form['username']
        passwrd = request.form['password']
        print(passwrd)
        cur = mysql.connection.cursor()
        cur.execute("SELECT username,password FROM faculty WHERE username=%s",[uname])
        user = cur.fetchone()
        temp = user[1]
        hashPwd = bcrypt.generate_password_hash(temp)
        print(hashPwd)
        if len(user) > 0:
            session.pop('username',None)
            if (bcrypt.check_password_hash(hashPwd,passwrd)) == True:
                session['username'] = request.form['username']
                return redirect(url_for('login_verify',userID = uname))
            else:
                flash('Invalid Username or Password !!')
                return render_template('login.html')
    else:
        return render_template('login.html')
@app.route('/upload_file',methods = ['GET','POST'])
def upload_file():
    if request.method =='POST':
        id = request.form['ID']
        file1 = request.files['file1']
        if file1:
            ext = file1.filename.split('.')[-1]
            if ext == 'pdf' or ext == 'pptx':
                filename = secure_filename(file1.filename)
                path = os.path.join(app.config['upload'],id.split('_')[-1],id,filename)
                path1 = os.path.join(app.config['upload'],id.split('_')[-1],'admin_' + id.split('_')[-1])
                file1.save(path)
                upload.upload(id, path1, path)
            else:
                filename = secure_filename(file1.filename)
                path = os.path.join(app.config['upload'],id.split('_')[-1],id,filename)
                file1.save(path)
                upload.genkeywords(path,'./Upload Folder/' + id.split('_')[-1] + '/',id)
            return redirect(url_for('success',name = id))
        else:
            return "File found not saved"
    else:
        return "Unsuccessful"
@app.route('/download/<string:id>/<string:filename>')
def download(id,filename = None):
    print(id)
    uploads = os.path.join(app.config['upload'],id.split('_')[-1],id)
    #print(uploads)
    print(filename)
    return send_from_directory(uploads, filename)
@app.route('/success/<string:name>')
def success(name):
    return render_template('admin_home.html',docs = upload.retrieve(name))

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')  
    #return str(chatbot1.get_bot_response(userText)) 
    return str(test1.getreply(userText))

@app.route("/chatbot")
def chatbot_init():
    return render_template('chatbot.html')
@app.route('/login_verify/<string:userID>',methods = ['POST','GET'])
def login_verify(userID):
    name = userID
    return redirect(url_for('success',name = name))

@app.route("/notes")
def notes():
    return render_template('viewer_home.html')

@app.route("/full_notes")
def full_notes():
    files = os.listdir(app.config['upload'])
    return render_template('full_notes.html',files = files)
@app.route("/full_notes1/<path:folder>")
def full_notes1(folder = None):
    if folder == None:
        folder = './Upload Folder'
    else:
        print(folder)
        if folder in os.listdir('Upload Folder'):
            #print('Subject Folder')
            folder1 = './Upload Folder/' + folder
            files = os.listdir(folder1)
            files = [f for f in files if (str)('_' + folder) in f and 'admin' not in f and 'Event Based' not in f]
            cur = mysql.connection.cursor()
            f1 = []
            for f in files:
                cur.execute("Select name from faculty where username = %s",[f])
                f1.append(cur.fetchone()[0])
            return render_template('full_notes.html',files = f1)
            #print(files)
        else:
            extension = folder.split('/')
            print(extension)
            if len(extension) == 4:
                id = extension[2]
                name = extension[3]
                return redirect(url_for('download',id = id,filename = name))
            else:
                if len(folder.split('//')) < 2:
                    cur = mysql.connection.cursor()
                    cur.execute('Select username from faculty where name = %s',[folder])
                    name1 = cur.fetchone()[0]
                    folder = './Upload Folder/' + name1.split('_')[-1] + '/' + name1
                files = [(folder + '/' + f) for f in os.listdir(folder)]
    return render_template('full_notes.html',files = files)

@app.route("/smart_notes")
def smart_notes():
    docs = os.listdir(app.config['upload'])
    return render_template('smart_notes.html',docs = docs)

@app.route("/smart_notes1/<string:subject>/<string:search>/<string:res>")
def smart_notes1(subject,search,res):
    path = os.path.join(app.config['upload'],subject,'Event Based_' + subject)
    pl = [os.path.join(path,f) for f in os.listdir(path) if '_PLACEMENT' in f]
    endsem = [os.path.join(path,f) for f in os.listdir(path) if '_ENDSEM' in f]
    path1 = os.path.join(app.config['upload'],subject)
    names = os.listdir(path1)
    names = [f for f in names if '_' + subject in f and 'Event Based_' not in f and 'admin' not in f]
    n1 = {}
    for f in names:
        cur = mysql.connection.cursor()
        cur.execute("SELECT name from faculty where username =%s",[f])
        user = cur.fetchone()
        temp = user[0]
        n1[f] = temp
    return render_template('smart_notes1.html',pl = pl,end = endsem,sub = subject,staffs = n1,res = res,search = search)

@app.route('/getres',methods = ['GET','POST'])
def getres():
    if request.method == 'POST':
        subject = request.form['subject']
        staffs = request.form.getlist('staff')
        search_term = request.form['term']
        res = search.keyword_search(subject,staffs,search_term)
        #res = "<p><a href = 'localhost:5000'>Home</p>"
        path = os.path.join(app.config['upload'],subject,'Event Based_' + subject)
        pl = [os.path.join(path,f) for f in os.listdir(path) if '_PLACEMENT' in f]
        endsem = [os.path.join(path,f) for f in os.listdir(path) if '_ENDSEM' in f]
        path1 = os.path.join(app.config['upload'],subject)
        names = os.listdir(path1)
        names = [f for f in names if '_' + subject in f and 'Event Based_' not in f and 'admin' not in f]
        n1 = {}
        for f in names:
            cur = mysql.connection.cursor()
            cur.execute("SELECT name from faculty where username =%s",[f])
            user = cur.fetchone()
            temp = user[0]
            n1[f] = temp
        return render_template('smart_notes1.html',pl = pl,end = endsem,sub = subject,staffs = n1,res = res,search = search)
@app.route('/syllabus')
def syllabus():
    return render_template('syllabus.html')
@app.route('/syllabus_summarizer',methods = ['POST','GET'])
def syllabus_summarizer():
    if request.method == 'POST':
        val = request.form['search_term']
        val1 = val
        if len(val) == 0:
            return render_template('result.html',res = 'Enter a search term',val = val)
        if 'choice' in request.form:
            choice = request.form['choice']
            if choice == 'topic':
                res = syllabus_summ.summarize(val)
                if  res == None:
                    res = "Not Found"
            else:
                val = val.lower()
                terms = val.split('unit')
                if len(terms) > 1:
                    terms[1] = 'UNIT' + terms[1]
                    res = syllabus_summ1.get_info(terms[0].strip().upper(), terms[1].upper())
                else:
                    res = syllabus_summ1.get_info(terms[0].upper(), "")
            return render_template('result.html',res = res,val = val1)
        else:
            return render_template('result.html',res = 'Select a radio button',val = val)
@app.route('/jumpthequeue')
def jumpthequeue():
    return render_template('login.html')

@app.route('/authentication1',methods=['POST','GET'])
def authenticate1():
    if request.method == 'POST':
        uname = request.form['username']
        passwrd = request.form['password']
        print(passwrd)
        cur = mysql.connection.cursor()
        cur.execute("SELECT username,password FROM admin WHERE username=%s",[uname])
        user = cur.fetchone()
        temp = user[1]
        hashPwd = bcrypt.generate_password_hash(temp)
        print(hashPwd)
        if len(user) > 0:
            session.pop('username',None)
            if (bcrypt.check_password_hash(hashPwd,passwrd)) == True:
                session['username'] = request.form['username']
                return redirect(url_for('buddyprep',status = 'Success'))
            else:
                flash('Invalid Username or Password !!')
                return render_template('login1.html')
    else:
        return render_template('login1.html')
@app.route('/buddyprep/<string:status>')
def buddyprep(status):
    if status == 'Success':
        folders = os.listdir(app.config['upload'])
        return render_template('admin_homepage.html',subs = folders)
    else:
        return render_template('login1.html')
@app.route('/buddypreplogin')
def buddypreplogin():
    return render_template('login1.html')
@app.route('/admin_subject/<string:subject>')
def admin_subject(subject):
    path = os.path.join(app.config['upload'],subject,('admin_' + subject))
    print(path)
    if os.path.exists(path):
        files_to_download = [os.path.join(path,f) for f in os.listdir(path)]
    else:
        files_to_download = []
    path1 = os.path.join(app.config['upload'],subject,('Event Based_' + subject))
    if os.path.exists(path1):
        highlighted_files = [os.path.join(path1,f) for f in os.listdir(path1)]
    else:
        highlighted_files = []
    #print(files_to_download)
    #print(highlighted_files)
    return render_template('admin_main.html',f1 = files_to_download,f2 = highlighted_files)
@app.route('/admin_upload',methods = ['GET','POST'])
def admin_upload():
    if request.method =='POST':
        id = request.form['ID1']
        print(id)
        if 'files' not in request.files:
            print('Not there')
            return redirect(url_for('admin_subject',subject = id))
        files = request.files.getlist('files')
        if len(files) == 0:
            print('Not there')
            return redirect(url_for('admin_subject',subject = id))
        for file1 in files:
            filename = secure_filename(file1.filename)
            path = os.path.join(app.config['upload'],id,'temp',filename)
            file1.save(path)
        if 'name' not in request.form:
            print('Not there')
            return redirect(url_for('admin_subject',subject = id))
        print('There')
        name = request.form['name']
        path1 = os.path.join('Upload Folder',id,'temp')
        files = [os.path.join('Upload Folder',id,'temp',f) for f in os.listdir(path1)]
        print(files)
        print(name)
        highlight.highlighted(files, id, name)
        for f in files:
            os.remove(f)
        return redirect(url_for('admin_subject',subject = id))
if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)
    #test1.tempfn()