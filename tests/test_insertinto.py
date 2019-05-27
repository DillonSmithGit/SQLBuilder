import os
import pathlib
import pickle
import pytest
import shutil
import sqlite3
import sys

testPath = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
genPath = pathlib.Path(os.path.join(testPath,'..','gen','mods'))
sys.path.insert(0,genPath)
import sqlbuilder.builders as builder
depPath = os.path.join(testPath,'dep')

class TestInsertInto():
    def setup_class(self):
        testDb = os.path.join(depPath, 'test.db')
        dbCopy = os.path.join(depPath, 'copy_test.db')
        shutil.copy(testDb,dbCopy)
        self.conn = sqlite3.connect(dbCopy)
        self.crsr = self.conn.cursor()

    def get_demographics_data(self):
        select = builder.Select('ParticipantDemographics', ['dob', 'iq', 'gender', 'race', 'ethnicity'])
        args = select.generate()
        self.crsr.execute(*args)
        output = self.crsr.fetchall()
        return output

    @pytest.fixture
    def insert_into_cursor(self):
        output = pickle.load(open(os.path.join(depPath, 'insert_into_cursor.pickle'), 'rb'))
        return output

    def test_insert_into_statement(self,insert_into_cursor):
        insertinto = builder.InsertInto('ParticipantDemographics',['dob','iq','gender','race','ethnicity'],
                                        ['2000-01-01','95','Male','Asian','Not Hispanic'])
        args = insertinto.generate()
        self.crsr.execute(*args)
        assert self.get_demographics_data() == insert_into_cursor, 'Insert into statement failed to correctly insert records.'

    def teardown_class(self):
        self.conn.close()
        os.remove(os.path.join(depPath, 'copy_test.db'))