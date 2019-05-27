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

class TestSelect():
    def setup_class(self):
        testDb = os.path.join(depPath, 'test.db')
        dbCopy = os.path.join(depPath, 'copy_test.db')
        shutil.copy(testDb,dbCopy)
        self.conn = sqlite3.connect(dbCopy)
        self.crsr = self.conn.cursor()

    @pytest.fixture
    def single_field_cursor(self):
        cursor = pickle.load(open(os.path.join(depPath, 'select_single_field_cursor.pickle'), 'rb'))
        return cursor

    @pytest.fixture
    def multi_field_cursor(self):
        cursor = pickle.load(open(os.path.join(depPath, 'select_multi_field_cursor.pickle'), 'rb'))
        return cursor

    @pytest.fixture
    def inner_join_cursor(self):
        cursor = pickle.load(open(os.path.join(depPath, 'select_inner_join_cursor.pickle'), 'rb'))
        return cursor

    def test_select_statement(self, single_field_cursor, multi_field_cursor, inner_join_cursor):
        select = builder.Select('ParticipantDemographics','id')
        args = select.generate()
        self.crsr.execute(*args)
        cursor = self.crsr.fetchall()
        assert cursor == single_field_cursor, 'Output of single field select statement is incorrect'

        select = builder.Select('ParticipantDemographics',['id','dob'])
        args = select.generate()
        self.crsr.execute(*args)
        cursor = self.crsr.fetchall()
        assert cursor == multi_field_cursor, 'Output of multi field select statement is incorrect'

        demographics = builder.Select('ParticipantDemographics', ['dob', 'iq', 'gender', 'race', 'ethnicity'])
        data = builder.Select('ExperimentData', ['taskname', 'score'])
        args = demographics.inner_join(data,('id','=','id'))
        self.crsr.execute(*args)
        cursor = self.crsr.fetchall()
        assert cursor == inner_join_cursor, 'Output of inner join select statement is incorrect'

    def teardown_class(self):
        self.conn.close()
        os.remove(os.path.join(depPath, 'copy_test.db'))