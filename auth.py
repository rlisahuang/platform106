import os, re
import MySQLdb

def file_contents(filename):
    with open(filename,'r') as f:
        return f.read()

def getpass(filename='~/mysql-passwd'):
    '''returns the contents of the given file as a string.
    
You can store your MySQL password in there, separate from your source code'''
    return file_contents(os.path.expanduser(filename))
    
# ==========================================================================================
# Reading a file formatted like ~/.my.cnf

def read_cnf_core(cnf_file=None):
    '''Read a file formatted like ~/.my.cnf file; defaulting to that
    file. Return a dictionary with the necessary information to connect to
    a database. This function is an internal function. Consider using read_cnf(),
    which caches the results.'''
    if cnf_file is None:
        cnf_file = os.path.expanduser('~/.my.cnf')
    else:
        cnf_file = os.path.expanduser(cnf_file)
    cnf = file_contents(cnf_file)
    credentials = {}
    # the key is the name used in the CNF file;
    # the value is the name used in the MySQLdb.connect() function
    mapping = {'host':'host',
               'user':'user',
               'password':'passwd',
               'database':'db'}
    for key in ('host', 'user', 'password', 'database' ):
        cred_key = mapping[key]
        # using \w* permits empty passwords and such
        # this regex is not perfect. It doesn't allow embedded spaces, for example.
        regex = r"\b{k}\s*=\s*[\'\"]?(\w*)[\'\"]?".format(k=key)
        # print 'regex',regex
        p = re.compile(regex)
        m = p.search(cnf)
        if m:
            credentials[ cred_key ] = m.group(1)
        elif key == 'host' or key == 'database':
            credentials[ cred_key ] = 'not specified in ' + cnf_file
        else:
            raise Exception('Could not find key {k} in {f}'
                            .format(k=key,f=cnf_file))
    checkDSN(credentials)
    return credentials

def checkDSN(dsn):
    '''Raises a comprehensible error message if the DSN is missing some necessary info'''
    for key in ('host', 'user', 'passwd', 'db' ):
        if not key in dsn:
            raise KeyError('''DSN lacks necessary '{k}' key'''.format(k=key))
    return True
    
CNF = None

def read_cnf(cnf_file="~/.my.cnf"):
    global CNF
    if CNF is not None:
        return CNF
    CNF = read_cnf_core(cnf_file)
    return CNF
    
# ==========================================================================================
def mysqlConnectCNF(db=None,filename="~/.my.cnf"):
    CNF = read_cnf(filename)
    if db is not None:
        CNF['db'] = db
    conn = MySQLdb.connect(**CNF)
    conn.autocommit(True)
    return conn


