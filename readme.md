<div class="document">

<div class="documentwrapper">

<div class="body" role="main">

<div class="section" id="welcome-to-the-documentation-for-the-sqlbuilder-package">

# Welcome to the documentation for the SQLBuilder Package!

<span class="target" id="module-sqlbuilder.builders"></span>

This module procedurally generates parameterized SQL statements from structured Python data. It is intended for use with Python DB API compatible libraries. It currently supports SELECT, UPDATE, INSERT INTO, and DELETE statements. See below for usage details and examples.

To install, open SQLBuilder directory in your terminal and run setup.py install. The module is written in pure Python with no outside dependencies for version 3.7.3.

General example of syntactic structure for this module

<div class="highlight-default notranslate">

<div class="highlight">

<pre><span></span><span class="kn">import</span> <span class="nn">sqlbuilder.builders</span> <span class="k">as</span> <span class="nn">builders</span>

<span class="n">condition</span> <span class="o">=</span> <span class="n">builders</span><span class="o">.</span><span class="n">Condition</span><span class="p">(</span><span class="n">args</span><span class="p">,</span><span class="n">kwargs</span><span class="p">)</span>
<span class="n">select</span> <span class="o">=</span> <span class="n">builders</span><span class="o">.</span><span class="n">Select</span><span class="p">(</span><span class="n">args</span><span class="p">,</span><span class="n">kwargs</span><span class="p">)</span>
<span class="n">update</span> <span class="o">=</span> <span class="n">builders</span><span class="o">.</span><span class="n">Update</span><span class="p">(</span><span class="n">args</span><span class="p">,</span><span class="n">kwargs</span><span class="p">)</span>
<span class="n">insertInto</span> <span class="o">=</span> <span class="n">builders</span><span class="o">.</span><span class="n">InsertInto</span><span class="p">(</span><span class="n">args</span><span class="p">,</span><span class="n">kwargs</span><span class="p">)</span>
<span class="n">delete</span> <span class="o">=</span> <span class="n">builders</span><span class="o">.</span><span class="n">Delete</span><span class="p">(</span><span class="n">args</span><span class="p">,</span><span class="n">kwargs</span><span class="p">)</span>
</pre>

</div>

</div>

<dl class="class">

<dt id="sqlbuilder.builders.Statement">class sqlbuilder.builders.Statement<span class="sig-paren">(</span>type, table, condition=None<span class="sig-paren">)</span>

<dd>

Bases: <span class="pre">object</span>

This is the superclass used as a basis for our statement classes. Users should not instantiate this class directly. Rather, one of the more specific subclasses should be used.

<dl class="method">

<dt id="sqlbuilder.builders.Statement.add_condition">add_condition<span class="sig-paren">(</span>condition<span class="sig-paren">)</span></dt>

<dd>

Attaches a Condition object to a previously instantiated Statement.

<dl class="field-list simple">

<dt class="field-odd">Parameters</dt>

<dd class="field-odd">

**condition** – (Condition) object that contains specifications for fields that should be operated on by the Statements they are associated with.

</dd>

</dl>

</dd>

</dl>

</dd>

</dl>

<dl class="class">

<dt id="sqlbuilder.builders.Select">class sqlbuilder.builders.Select<span class="sig-paren">(</span>table, fields, condition=None_<span class="sig-paren">)</span></dt>

<dd>

Bases: <span class="pre">sqlbuilder.builders.Statement</span>

This is the class used to construct SELECT statements.

Each instance contains a table name and list/tuple of fields to select data from. Optionally, they may also include a Condition object specifying which data should be selected. The class also has an inner join method which allows users to select data from two separate tables with one command.

E.g. to select the fields ‘id’, ‘age’, and ‘gender’ from table ‘demographics’ where the participant’s age is higher than 20:

<div class="highlight-default notranslate">

<div class="highlight">

<pre><span></span><span class="n">select</span> <span class="o">=</span> <span class="n">Select</span><span class="p">(</span><span class="s1">'demographics'</span><span class="p">,</span> <span class="p">[</span><span class="s1">'id'</span><span class="p">,</span><span class="s1">'age'</span><span class="p">,</span><span class="s1">'gender'</span><span class="p">],</span>
                <span class="n">condition</span> <span class="o">=</span> <span class="n">Condition</span><span class="p">([{</span><span class="s1">'age'</span><span class="p">:(</span><span class="s1">'>'</span><span class="p">,</span><span class="mi">20</span><span class="p">)}]))</span>
<span class="nb">input</span> <span class="o">=</span> <span class="n">select</span><span class="o">.</span><span class="n">generate</span><span class="p">()</span>
<span class="n">crsr</span><span class="o">.</span><span class="n">execute</span><span class="p">(</span><span class="o">*</span><span class="nb">input</span><span class="p">)</span>
<span class="n">output</span> <span class="o">=</span> <span class="n">crsr</span><span class="o">.</span><span class="n">fetchall</span><span class="p">()</span>
</pre>

</div>

</div>

<dl class="simple">

<dt>TODO:</dt>

<dd>

1.  Expand inner_join functionality to support selecting data from an arbitrary number of tables.

2.  Include support for other types of joins.

</dd>

</dl>

<dl class="method">

<dt id="sqlbuilder.builders.Select.generate">generate<span class="sig-paren">(</span><span class="sig-paren">)</span></dt>

<dd>

Generates parameterized sql statement and list of params for use with a Python DB API compatible library.

<dl class="field-list simple">

<dt class="field-odd">Returns</dt>

</dl>

(str) SQL statement used to select specified data.

(list) containing parameters to be supplied with the accompanying statement.

</dd>

</dl>

<dl class="method">

<dt id="sqlbuilder.builders.Select.inner_join">inner_join<span class="sig-paren">(</span>statementToJoin, joinKey<span class="sig-paren">)</span></dt>

<dd>

Takes as input a second select statement and creates an inner join by combining them.

<dl class="field-list simple">

<dt class="field-odd">Parameters</dt>

<dd class="field-odd">

*   **statementToJoin** – (Select) a second Select object to construct an Inner Join with.

*   **joinKey** – (list/tuple) a 3-element list used to specify how records from the two tables should be unified.

</dd>

</dl>

The argument (‘id’,’=’,’id’), for example, would correspond to FROM Table1 INNER JOIN Table2 ON Table1.id = Table2.id

<dl class="field-list simple">

<dt class="field-odd">Returns</dt>

<dd class="field-odd">

(str) SQL statement that selects all specified fields from both tables, conjoined via the joinKey, which satisfy all

</dd>

</dl>

conditions of both statements.

</dd>

</dl>

</dd>

</dl>

<dl class="class">

<dt id="sqlbuilder.builders.Update">class sqlbuilder.builders.Update<span class="sig-paren">(</span>table, fields, values, condition=None <span class="sig-paren">)</dt>

<dd>

Bases: <span class="pre">sqlbuilder.builders.Statement</span>

This is the class used to construct UPDATE statements.

Each instance contains a table, set of fields, set of values, and optionally, a condition.

E.g. to loop through an array of tuples containing ids, ages, and genders of participants and update your database, you could do the following

<div class="highlight-default notranslate">

<div class="highlight">

<pre><span></span><span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="n">demoData</span><span class="p">:</span>
    <span class="n">update</span> <span class="o">=</span> <span class="n">Update</span><span class="p">(</span><span class="s1">'demographics'</span><span class="p">,[</span><span class="s1">'age'</span><span class="p">,</span><span class="s1">'gender'</span><span class="p">],</span> <span class="p">[</span><span class="n">i</span><span class="p">[</span><span class="mi">1</span><span class="p">],</span><span class="n">i</span><span class="p">[</span><span class="mi">2</span><span class="p">]],</span> <span class="n">condition</span> <span class="o">=</span> <span class="n">Condition</span><span class="p">([{</span><span class="s1">'id'</span><span class="p">:(</span><span class="s1">'='</span><span class="p">,</span><span class="n">i</span><span class="p">[</span><span class="mi">0</span><span class="p">])}]))</span>
    <span class="nb">input</span> <span class="o">=</span> <span class="n">update</span><span class="o">.</span><span class="n">generate</span><span class="p">()</span>
    <span class="n">crsr</span><span class="o">.</span><span class="n">execute</span><span class="p">(</span><span class="o">*</span><span class="nb">input</span><span class="p">)</span>
<span class="n">crsr</span><span class="o">.</span><span class="n">execute</span><span class="p">(</span><span class="s1">'commit;'</span><span class="p">)</span>
</pre>

</div>

</div>

<dl class="method">

<dt id="sqlbuilder.builders.Update.no_condition_warning">no_condition_warning<span class="sig-paren">(</span><span class="sig-paren">)</span></dt>

<dd>

If an Update object is instantiated without a condition this warning is given. This is a safe guard to prevent users from accidentally updating every record in their table if they did not mean to do so.

</dd>

</dl>

<dl class="method">

<dt id="sqlbuilder.builders.Update.generate">generate<span class="sig-paren">(</span><span class="sig-paren">)</span></dt>

<dd>

<dl class="field-list simple">

<dt class="field-odd">Returns</dt>

</dl>

(str) SQL statement used to update specified data. (list) containing parameters to be supplied with accompanying statement.

</dd>

</dl>

</dd>

</dl>

<dl class="class">

<dt id="sqlbuilder.builders.InsertInto">class sqlbuilder.builders.InsertInto<span class="sig-paren">(</span>table, fields, values<span class="sig-paren">)</span></dt>

<dd>

Bases: <span class="pre">sqlbuilder.builders.Statement</span>

This is the class used to construct INSERT INTO statements.

Each instance contains a table name, array with fields to populate when creating records, and respective values to populate fields with.

E.g. to loop through an array of tuples containing ids, ages, and genders of participants and insert records into your database, you could do the following

<div class="highlight-default notranslate">

<div class="highlight">

<pre><span></span><span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="n">demoData</span><span class="p">:</span>
    <span class="n">insert</span> <span class="o">=</span> <span class="n">InsertInto</span><span class="p">(</span><span class="s1">'demographics'</span><span class="p">,[</span><span class="s1">'id'</span><span class="p">,</span><span class="s1">'age'</span><span class="p">,</span><span class="s1">'gender'</span><span class="p">],[</span><span class="n">i</span><span class="p">[</span><span class="mi">0</span><span class="p">],</span><span class="n">i</span><span class="p">[</span><span class="mi">1</span><span class="p">],</span><span class="n">i</span><span class="p">[</span><span class="mi">2</span><span class="p">])</span>
    <span class="nb">input</span> <span class="o">=</span> <span class="n">insert</span><span class="o">.</span><span class="n">generate</span><span class="p">()</span>
    <span class="n">crsr</span><span class="o">.</span><span class="n">execute</span><span class="p">(</span><span class="o">*</span><span class="nb">input</span><span class="p">)</span>
<span class="n">crsr</span><span class="o">.</span><span class="n">execute</span><span class="p">(</span><span class="s1">'commit;'</span><span class="p">)</span>
</pre>

</div>

</div>

<dl class="method">

<dt id="sqlbuilder.builders.InsertInto.generate">generate<span class="sig-paren">(</span><span class="sig-paren">)</span></dt>

<dd>

<dl class="field-list simple">

<dt class="field-odd">Returns</dt>

</dl>

(str) SQL statement used to update specified data. (list) containing parameters to be supplied with accompanying statement.

</dd>

</dl>

</dd>

</dl>

<dl class="class">

<dt id="sqlbuilder.builders.Delete">class sqlbuilder.builders.Delete<span class="sig-paren">(</span>table, condition=None_<span class="sig-paren">)</span></dt>

<dd>

Bases: [<span class="pre">sqlbuilder.builders.Statement</span>]("sqlbuilder.builders.Statement")

This is the class used to construct DELETE statements.

Each instance contains a table name and, optionally, a condition

E.g. to delete all records from the table “demographics” with IDs below 20, you could do

<div class="highlight-default notranslate">

<div class="highlight">

<pre><span></span><span class="n">delete</span> <span class="o">=</span> <span class="n">Delete</span><span class="p">(</span><span class="s1">'demographics'</span><span class="p">,</span><span class="n">condition</span> <span class="o">=</span> <span class="n">Condition</span><span class="p">([{</span><span class="s1">'id'</span><span class="p">:(</span><span class="s1">'<'</span><span class="p">,</span><span class="mi">20</span><span class="p">)}]))</span>
<span class="nb">input</span> <span class="o">=</span> <span class="n">delete</span><span class="o">.</span><span class="n">generate</span><span class="p">()</span>
<span class="n">crsr</span><span class="o">.</span><span class="n">execute</span><span class="p">(</span><span class="o">*</span><span class="nb">input</span><span class="p">)</span>
<span class="n">crsr</span><span class="o">.</span><span class="n">execute</span><span class="p">(</span><span class="s1">'commit;'</span><span class="p">)</span>
</pre>

</div>

</div>

<dl class="method">

<dt id="sqlbuilder.builders.Delete.no_condition_warning">no_condition_warning<span class="sig-paren">(</span><span class="sig-paren">)</span></dt>

<dd>

If a Delete object is instantiated without a condition this warning is given. This is a safe guard to prevent users from accidentally deleting every record in their table if they did not mean to do so.

</dd>

</dl>

<dl class="method">

<dt id="sqlbuilder.builders.Delete.generate">generate<span class="sig-paren">(</span><span class="sig-paren">)</span></dt>

<dd>

<dl class="field-list simple">

<dt class="field-odd">Returns</dt>

</dl>

(str) SQL statement used to delete specified data. (list) containing parameters to be supplied with accompanying statement.

</dd>

</dl>

</dd>

</dl>

<dl class="class">

<dt id="sqlbuilder.builders.Condition">class sqlbuilder.builders.Condition<span class="sig-paren">(</span>conditionSeed<span class="sig-paren">)</span></dt>

<dd>

Bases: <span class="pre">object</span>

This class is used to construct the WHERE clauses for our statements. These are created through condition seeds. Currently, the seeds are in the form of lists of dicts. The key:value format for these dicts is FieldName: (Logical Operator, Value). This corresponds to one logical condition. A dict represents a set of logical tests which all must be true together to return a True value, i.e. they are “AND”-separated tests. Only one of the dicts within a list need to be evaluted as true for a given condition to be met, i.e. the list items themselves are “OR”-separated logical tests. Therefore, if I were to declare an instance with the following parameters:

<div class="highlight-default notranslate">

<div class="highlight">

<pre><span></span><span class="n">myCondition</span> <span class="o">=</span> <span class="n">builder</span><span class="o">.</span><span class="n">Condition</span><span class="p">([</span>
                                <span class="p">{</span><span class="s1">'Age'</span><span class="p">:</span> <span class="p">(</span><span class="s1">'>'</span><span class="p">,</span> <span class="mi">10</span><span class="p">),</span>
                                <span class="s1">'Id'</span><span class="p">:</span> <span class="p">(</span><span class="s1">'<'</span><span class="p">,</span> <span class="mi">50</span><span class="p">)}</span>
                                <span class="p">,</span>
                                <span class="p">{</span><span class="s1">'Race'</span><span class="p">:(</span><span class="s1">'='</span><span class="p">,</span><span class="s1">'Caucasian'</span><span class="p">)}</span>
                                <span class="p">])</span>
</pre>

</div>

</div>

The string representation would be ‘(Age > 10 AND Id < 50) OR (Race = ‘Caucasian’)’

NOTE: If you actually run this code, the output you will get from the Condition’s generate method will be ‘(Age > ? AND Id < ?) OR (Race = ?)’. This is because the module generates parameterized statements. If you used the condition in conjunction with a Statement object to form a statement, you would be given the values (10, 50, and ‘Caucasian’) in a list to use as parameters.

<dl class="method">

<dt id="sqlbuilder.builders.Condition.initialize_params">initialize_params<span class="sig-paren">(</span><span class="sig-paren">)</span></dt>

<dd>

Method used by Statement objects to retrieve params from their Conditions.

<dl class="field-list simple">

<dt class="field-odd">Returns</dt>

<dd class="field-odd">

(List) containing parameters to be piped into DB.

</dd>

</dl>

</dd>

</dl>

<dl class="method">

<dt id="sqlbuilder.builders.Condition.generate">generate<span class="sig-paren">(</span><span class="sig-paren">)</span></dt>

<dd>

Method used to generate string representation of clause :return: (str) WHERE clause generated from condition seed

</dd>

</dl>

<dl class="method">

<dt id="sqlbuilder.builders.Condition.merge">merge<span class="sig-paren">(</span>conditionToMerge<span class="sig-paren">)</span></dt>

<dd>

Method used for inner joins when both statements have conditions. Appends table names to condition fields to avoid ambiguity and merges both sets of conditions so that both must be true for data to be selected from resultant statement.

<dl class="field-list simple">

<dt class="field-odd">Parameters</dt>

<dd class="field-odd">

**conditionToMerge** – (Condition) object to merge with.

</dd>

<dt class="field-even">Returns</dt>

<dd class="field-even">

(str) Where clause to be used with joined statements

</dd>

</dl>

</dd>

</dl>

</dd>

</dl>

</div>

</div>

</div>

</div>

<div class="footer">©2019, Dillon Smith.
