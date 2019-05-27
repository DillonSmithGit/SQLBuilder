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

class TestCondition():
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
    def condition_cursor(self):
        cursor = pickle.load(open(os.path.join(depPath, 'condition_cursor.pickle'), 'rb'))
        return cursor
    
    def test_condition(self, condition_cursor):
        conditionSeed = \
            [
                {'id': ('=', '1')}
            ]
        condition = builder.Condition(conditionSeed)
        select = builder.Select('ParticipantDemographics',['dob', 'iq', 'gender', 'race', 'ethnicity'],condition)
        args = select.generate()
        self.crsr.execute(*args)
        output = self.crsr.fetchall()
        assert output == condition_cursor, 'Output of conditional select statement is incorrect'

    def teardown_class(self):
        self.conn.close()
        os.remove(os.path.join(depPath, 'copy_test.db'))