import os
import pathlib
import shutil
import sqlite3
import sys

testPath = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
genPath = pathlib.Path(os.path.join(testPath,'..','gen','mods'))
sys.path.insert(0,genPath)
import sqlbuilder.builders as builder
depPath = os.path.join(testPath,'dep')

class TestDelete():
    def setup_class(self):
        testDb = os.path.join(depPath, 'test.db')
        dbCopy = os.path.join(depPath, 'copy_test.db')
        shutil.copy(testDb,dbCopy)
        self.conn = sqlite3.connect(dbCopy)
        self.crsr = self.conn.cursor()
        builder.Delete.no_condition_warning = lambda _: ()

    def get_demographics_data(self):
        select = builder.Select('ParticipantDemographics', ['dob', 'iq', 'gender', 'race', 'ethnicity'])
        args = select.generate()
        self.crsr.execute(*args)
        output = self.crsr.fetchall()
        return output

    def test_delete_statement(self):
        delete = builder.Delete('ParticipantDemographics')
        args = delete.generate()
        self.crsr.execute(*args)
        output = self.get_demographics_data()
        assert output == [], 'Delete statement failed to clear records'

    def teardown_class(self):
        self.conn.close()
        os.remove(os.path.join(depPath, 'copy_test.db'))