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

class TestUpdate():
    def setup_class(self):
        testDb = os.path.join(depPath, 'test.db')
        dbCopy = os.path.join(depPath, 'copy_test.db')
        shutil.copy(testDb,dbCopy)
        self.conn = sqlite3.connect(dbCopy)
        self.crsr = self.conn.cursor()
        builder.Update.no_condition_warning = lambda _: ()

    @pytest.fixture
    def update_cursor(self):
        output = pickle.load(open(os.path.join(depPath, 'update_cursor.pickle'), 'rb'))
        return output

    def get_demographics_data(self):
        select = builder.Select('ParticipantDemographics', ['dob', 'iq', 'gender', 'race', 'ethnicity'])
        args = select.generate()
        self.crsr.execute(*args)
        output = self.crsr.fetchall()
        return output

    def test_update_statement(self, update_cursor):
        update = builder.Update('ParticipantDemographics', ['dob', 'iq', 'gender', 'race', 'ethnicity'],
                                ['1990-01-02', '110', 'Female', 'Asian', 'Hispanic'])
        args = update.generate()
        self.crsr.execute(*args)
        self.crsr.execute('commit;')
        output = self.get_demographics_data()
        assert output == update_cursor, 'Update statement failed to correctly update record'

    def teardown_class(self):
        self.conn.close()
        os.remove(os.path.join(depPath, 'copy_test.db'))