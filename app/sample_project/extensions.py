from flask_sqlalchemy import SQLAlchemy

def nothing():
    # The nothing function, used as such:
    # (var:=payload['value']) if 'value' in payload else nothing()
    # This allows you to combine the setter and conditional check in one line
    # Only problem is when using inline if, python expects an else and wrapping 
    # The set operation makes it a function? So we need another function to create_all
    # In the failure case, hence the nothing function. Only works on variables, you 
    # can't set model.value for example.
    pass

db = SQLAlchemy()