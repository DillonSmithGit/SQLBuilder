'''This module procedurally generates parameterized SQL statements. It is intended for use with Python DB API compatible
libraries.
It currently supports SELECT, UPDATE, INSERT INTO, and DELETE statements. See below for usage details and examples.

To install, open SQLBuilder directory in your terminal and run setup.py install. The module is written in pure Python with
no outside dependencies for version 3.7.3.

General example of syntactic structure for this module ::

    import sqlbuilder.builders as builders

    condition = builders.Condition(args,kwargs)
    select = builders.Select(args,kwargs)
    update = builders.Update(args,kwargs)
    insertInto = builders.InsertInto(args,kwargs)
    delete = builders.Delete(args,kwargs)

'''
from sqlbuilder import errors

class Statement():
    '''This is the superclass used as a basis for our statement classes. Users should not instantiate this class directly.
    Rather, one of the more specific subclasses should be used.
    '''
    def __init__(self, type, table, condition=None):
        assert all((isinstance(type, str), type.upper() in ('SELECT', 'UPDATE', 'INSERT INTO', 'DELETE'))), errors.typeFailure
        assert isinstance(table, str), errors.tableFailure
        assert isinstance(condition, (Condition)) or condition is None, errors.conditionFailure
        self.root = type
        self.table = table
        self.add_condition(condition)

    def add_condition(self, condition):
        '''
        Attaches a Condition object to a previously instantiated Statement.

        :param condition: (Condition) object that contains specifications for fields that should be operated on by
            the Statements they are associated with.

        '''
        self.condition = condition
        if condition is not None:
            self.condition.parent = self

class Select(Statement):
    '''This is the class used to construct SELECT statements.

    Each instance contains a table name and list/tuple of fields to select data from. Optionally, they may also include
    a Condition object specifying which data should be selected. The class also has an inner join method which allows
    users to select data from two separate tables with one command.

    E.g. to select the fields 'id', 'age', and 'gender' from table 'demographics' where the participant's age is higher than 20: ::

        select = Select('demographics', ['id','age','gender'],
                        condition = Condition([{'age':('>',20)}]))
        input = select.generate()
        crsr.execute(*input)
        output = crsr.fetchall()

    TODO:
        1. Expand inner_join functionality to support selecting data from an arbitrary number of tables.
        2. Include support for other types of joins.

    '''
    def __init__(self, table, fields, condition=None):
        '''
        :param table: (str) name of table to select data from
        :param fields:  (str/list/tuple) indicating field or collection of fields to select data from
        :param condition: (Condition) specifying which conditions data must meet  to be selected
        '''
        assert isinstance(fields, (str, set, list)), errors.fieldFailure
        Statement.__init__(self, 'SELECT', table, condition)
        if isinstance(fields,str):
            self.fields = [fields]
        else:
            self.fields = fields

    def generate(self):
        '''
        Generates parameterized sql statement and list of params for use with a Python DB API compatible library.

        :return:
        (str) SQL statement used to select specified data.

        (list) containing parameters to be supplied with the accompanying statement.
        '''
        fields = [str(i) for i in self.fields]
        strSQL = f'SELECT {", ".join(fields)} FROM {self.table}'
        params = []
        if self.condition is not None:
            strSQL += f' WHERE {self.condition.generate()}'
            params.extend(self.condition.params)
        return strSQL, params

    def inner_join(self, statementToJoin, joinKey):
        '''
        Takes as input a second select statement and creates an inner join by combining them.

        :param statementToJoin: (Select) a second Select object to construct an Inner Join with.

        :param joinKey: (list/tuple) a 3-element list used to specify how records from the two tables should be unified.
        The argument ('id','=','id'), for example, would correspond to FROM Table1 INNER JOIN Table2 ON Table1.id = Table2.id

        :return: (str) SQL statement that selects all specified fields from both tables, conjoined via the joinKey, which satisfy all
        conditions of both statements.
        '''
        assert isinstance(statementToJoin, Statement)
        joinedFields = [f'{self.table}.{i}' for i in self.fields] + [f'{statementToJoin.table}.{i}' for i in statementToJoin.fields]
        selectClause = f'SELECT {", ".join(joinedFields)}'
        fromClause = f'FROM {self.table}'
        joinClause = f'INNER JOIN {statementToJoin.table} ON {self.table}.{joinKey[0]} ' \
                     f'{joinKey[1]} {statementToJoin.table}.{joinKey[2]}'
        whereClause = ''
        params = []
        if not [i for i in (self.condition,statementToJoin.condition) if i is not None] == []:
            conditionMerge, params = self.condition.merge(statementToJoin.condition)
            whereClause = f'WHERE {conditionMerge}'
        return (f'{selectClause} {fromClause} {joinClause} {whereClause}',params)

class Update(Statement):
    '''
    This is the class used to construct UPDATE statements.

    Each instance contains a table, set of fields, set of values, and optionally, a condition.

    E.g. to loop through an array of tuples containing ids, ages, and genders of participants and update your database,
    you could do the following ::

        for i in demoData:
            update = Update('demographics',['age','gender'], [i[1],i[2]], condition = Condition([{'id':('=',i[0])}]))
            input = update.generate()
            crsr.execute(*input)
        crsr.execute('commit;')
    '''
    def __init__(self, table, fields, values, condition=None):
        '''
        :param table: (str) specifying name of table to update
        :param fields:  (list,tuple) specifies which fields should be updated
        :param values:  (list,tuple) specifies values which fields should be updated to
        :param condition: (Condition) optional, Condition specifying which records should be operated upon
        '''
        assert len(fields)==len(values), errors.lenMismatchFailure
        if condition is None:
            self.no_condition_warning()
        Statement.__init__(self, 'UPDATE', table, condition)
        self.values = values
        self.fields = fields

    def no_condition_warning(self):
        '''
        If an Update object is instantiated without a condition this warning is given. This is a safe guard to prevent
        users from accidentally updating every record in their table if they did not mean to do so.
        '''
        noConditionWarning = input('Careful! You are generating an update statement without a condition. '
                                   'If you execute this statement as is you will update every record in your table. '
                                   'Continue? [y/n]')
        if not noConditionWarning.upper() == 'Y':
            raise Exception('Please construct a condition for use with your delete statement.')

    def generate(self):
        '''
        :return:
        (str) SQL statement used to update specified data.
        (list) containing parameters to be supplied with accompanying statement.
        '''
        strSQL = f'UPDATE {self.table} SET {", ".join([f"{i} = ?" for i in self.fields])}'
        params = self.values[:]
        if self.condition is not None:
            strSQL += f' WHERE {self.condition.generate()}'
            params.extend(self.condition.params[:])
        return strSQL, params

class InsertInto(Statement):
    '''
    This is the class used to construct INSERT INTO statements.

    Each instance contains a table name, array with fields to populate when creating records, and respective values to
    populate fields with.

    E.g. to loop through an array of tuples containing ids, ages, and genders of participants and insert records into your database,
    you could do the following ::

        for i in demoData:
            insert = InsertInto('demographics',['id','age','gender'],[i[0],i[1],i[2])
            input = insert.generate()
            crsr.execute(*input)
        crsr.execute('commit;')
    '''
    def __init__(self, table, fields, values):
        '''
        :param table: (str) Specifying which table to insert records into
        :param fields:  (list/tuple) Containing names of fields that should be populated when records are created
        :param values:  (list/tuple) Containing values to populate specified fields with
        '''
        Statement.__init__(self,'INSERT INTO',table)
        self.fields = fields
        self.values = values

    def generate(self):
        '''
        :return:
        (str) SQL statement used to update specified data.
        (list) containing parameters to be supplied with accompanying statement.
        '''
        strSQL = f'INSERT INTO {self.table} ({", ".join([i for i in self.fields])}) ' \
                 f'VALUES ({", ".join(["?"]*len(self.values))})'
        params = self.values[:]
        return strSQL, params

class Delete(Statement):
    '''
    This is the class used to construct DELETE statements.

    Each instance contains a table name and, optionally, a condition

    E.g. to delete all records from the table "demographics" with IDs below 20, you could do ::

        delete = Delete('demographics',condition = Condition([{'id':('<',20)}]))
        input = delete.generate()
        crsr.execute(*input)
        crsr.execute('commit;')

    '''
    def __init__(self, table, condition=None):
        '''
        :param table: (str) Specifying which table to delete records from
        :param condition: (Condition) specifying under which conditions records should be deleted
        '''
        Statement.__init__(self,'DELETE',table,condition)
        self.condition = condition
        if self.condition is None:
            self.no_condition_warning()

    def no_condition_warning(self):
        '''
        If a Delete object is instantiated without a condition this warning is given. This is a safe guard to prevent
        users from accidentally deleting every record in their table if they did not mean to do so.
        '''
        noConditionWarning = input('Careful! You are generating a delete statement without a condition. '
                                   'If you execute this statement as is you will delete every record in your table. '
                                   'Continue? [y/n]')
        if not noConditionWarning.upper() == 'Y':
            raise Exception('Please construct a condition for use with your delete statement.')

    def generate(self):
        '''
        :return:
        (str) SQL statement used to delete specified data.
        (list) containing parameters to be supplied with accompanying statement.
        '''
        strSQL = f'DELETE FROM {self.table}'
        params = []
        if self.condition is not None:
            strSQL += f' WHERE {self.condition.generate()}'
            params.extend(self.condition.params[:])
        return strSQL, params

class Condition():
    '''
    This class is used to construct the WHERE clauses for our statements. These are created through condition seeds. Currently,
    the seeds are in the form of lists of dicts. The key:value format for these dicts is FieldName: (Logical Operator, Value).
    This corresponds to one logical condition. A dict represents a set of logical tests which all must be true together to return
    a True value, i.e. they are "AND"-separated tests. Only one of the dicts within a list need to be evaluted as true for a given
    condition to be met, i.e. the list items themselves are "OR"-separated logical tests. Therefore, if I were to declare an instance
    with the following parameters: ::

        myCondition = builder.Condition([
                                        {'Age': ('>', 10),
                                        'Id': ('<', 50)}
                                        ,
                                        {'Race':('=','Caucasian')}
                                        ])

    The string representation would be '(Age > 10 AND Id < 50) OR (Race = 'Caucasian')'

    NOTE: If you actually run this code, the output you will get from the Condition's generate method will be '(Age > ? AND Id < ?) OR (Race = ?)'.
    This is because the module generates parameterized statements. If you used the condition in conjunction with a Statement object to form a statement,
    you would be given the values (10, 50, and 'Caucasian') in a list to use as parameters.
    '''
    def __init__(self,conditionSeed):
        assert(isinstance(conditionSeed,(set,list,dict))), errors.conditionSeedFailure
        if isinstance(conditionSeed,dict):
            self.conditionSeed = [conditionSeed]
        else:
            self.conditionSeed = conditionSeed
        self.params = self.initialize_params()
        self.string = self.generate()
        self.parent = None

    def initialize_params(self):
        '''
        Method used by Statement objects to retrieve params from their Conditions.

        :return: (List) containing parameters to be piped into DB.
        '''
        params = []
        for element in self.conditionSeed:
            params.extend([element[i][1] for i in element.keys()])
        return params

    def generate(self):
        '''
        Method used to generate string representation of clause
        :return: (str) WHERE clause generated from condition seed
        '''
        orSeparatedConditions = []
        for element in self.conditionSeed:
            orSeparatedConditions.append('(' + ' AND '.join([f'{i} {element[i][0]} ?' for i in element.keys()]) + ')')
        whereClause = ' OR '.join(orSeparatedConditions)
        return whereClause

    def merge(self, conditionToMerge):
        '''
        Method used for inner joins when both statements have conditions. Appends table names to condition fields to
        avoid ambiguity and merges both sets of conditions so that both must be true for data to be selected from resultant
        statement.

        :param conditionToMerge: (Condition) object to merge with.
        :return: (str) Where clause to be used with joined statements
        '''
        subordinateConditions = [i for i in (self, conditionToMerge) if i is not None]
        joinedConditionStrings = []
        params = []
        for condition in subordinateConditions:
            joinedConditionList = []
            for clause in condition.conditionSeed:
                clauseDict = {f'{condition.parent.table}.{key}': val for key, val in clause.items()}
                joinedConditionList.append(clauseDict)
            tempCondition = Condition(joinedConditionList)
            joinedConditionStrings.append(tempCondition.generate())
            params.extend(condition.params)
        return ' AND '.join(joinedConditionStrings), params

