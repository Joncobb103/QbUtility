'''
Created on Aug 28, 2017

@author: Jonathan.Cobb
'''
from flask import Flask
from flask.templating import render_template
app = Flask(__name__)

class RegexConverter:
    regexDict = {
            'beginning of line': '^',
            'end of line': '$',
            'anything': '.',
            'money': '[0-9]+[.][0-9]{2}',
            'letter(any case) or number': '[0-9A-z]',
            'specific': '[(REPLACE LETTER)]',
            'letter lowercase': '[a-z]',
            'not lowercase Letter': '[^a-z]',
            'letter uppercase': '[A-Z]',
            'not uppercase Letter': '[^A-Z]',
            'Letter any case': '[A-Za-z]',
            'not any letter': '[^A-Za-z]',
            'number': '[0-9]',
            'not number': '[^0-9]',
            'space or symbol': '[^A-Za-z0-9]',
            'date (year)':'20[0-9]{2}',
            'date(mm-dd-yyyy)': '[0-1][0-9][-][0-3][0-9][-]20[0-9][0-9]',
            'date(mm-dd-yy)': '[0-1][0-9][-][0-3][0-9][-][0-9][0-9]',
            'date(m-d-yyyy)': '[1]?[0-9][-][1-3]?[0-9][-]20[0-9][0-9]',
            'date(m-d-yy)': '[1]?[0-9][-][1-3]?[0-9][-][0-9][0-9]',
            'date(mm/dd/yyyy)': '[0-1][0-9][/][0-3][0-9][/]20[0-9][0-9]',
            'date(mm/dd/yy)': '[0-1][0-9][/][0-3][0-9][/][0-9][0-9]',
            'date(m/d/yyyy)': '[1]?[0-9][/][1-3]?[0-9][/]20[0-9][0-9]',
            'date(m/d/yy)': '[1]?[0-9][/][1-3]?[0-9][/][0-9][0-9]',
            'date(mon-dd-yyyy)': '((Jan)|(Feb)|(Mar)|(Apr)|(May)|(Jun)|(Jul)|(Aug)|(Sep)|(Oct)|(Nov)|(Dec))[-][0-3][0-9][-]20[0-9][0-9]',
            'date(month-dd-yyyy)': '((January)|(February)|(March)|(April)|(May)|(June)|(July)|(August)|(September)|(October)|(November)|(December))[-][0-3][0-9][-]20[0-9][0-9]',
            'date(month-dd-yyyy)': '((January)|(February)|(March)|(April)|(May)|(June)|(July)|(August)|(September)|(October)|(November)|(December))[-][0-3][0-9][-]20[0-9][0-9]',
            'date(month dd, yyyy)': '((January)|(February)|(March)|(April)|(May)|(June)|(July)|(August)|(September)|(October)|(November)|(December))[^A-Za-z0-9]+[0-3][0-9][,][^A-Za-z0-9]+20[0-9][0-9]',
        }
    
    quantityDict = {
            'just one instance': '',
            '1 or more instances':'+',
            '0 or more instances':'*',
            '1 or no instance':'?',
            'specific number of instances': '{(REPLACE VALUE)}',
            'specific number or more instances': '{(REPLACE NUMBER),}',
            'range of numbers': '{(REPLACE MIN),(REPLACE MAX)}',
        }
@app.route("/")
def index():
    quant = RegexConverter.quantityDict
    regex = RegexConverter.regexDict
    return render_template('ccCreator.html', quant=quant, regex=regex)


if __name__ == "__main__":
    app.run( port=5400)