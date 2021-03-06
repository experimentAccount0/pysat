"""
tests the pysat utils area
"""
import pysat
import pandas as pds
from nose.tools import assert_raises, raises
import nose.tools
import pysat.instruments.pysat_testing
import numpy as np
import os
import tempfile

import sys
if sys.version_info[0] >= 3:
    if sys.version_info[1] < 4:
        import imp
        re_load = imp.reload
    else:
        import importlib
        re_load = importlib.reload
else:
    re_load = reload



#########
## basic yrdoy tests
def test_getyrdoy_1():
    '''Test the date to year, day of year code functionality'''
    date = pds.datetime(2009,1,1)
    yr, doy = pysat.utils.getyrdoy(date)
    assert ((yr == 2009) & (doy == 1))

def test_getyrdoy_leap_year():
    '''Test the date to year, day of year code functionality (leap_year)'''
    date = pds.datetime(2008,12,31)
    yr, doy = pysat.utils.getyrdoy(date)
    assert ((yr == 2008) & (doy == 366)) 

####################3
# test netCDF fexport ile support

def prep_dir(inst=None):
    import os
    import shutil

    if inst is None:
        inst = pysat.Instrument(platform='pysat', name='testing')
    # create data directories
    try:
        os.makedirs(inst.files.data_path)
        #print ('Made Directory')
    except OSError:
        pass

def remove_files(inst):
    # remove any files
    dir = inst.files.data_path
    for the_file in os.listdir(dir):
        if (the_file[0:13] == 'pysat_testing') & (the_file[-19:] == '.pysat_testing_file'):
            file_path = os.path.join(dir, the_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)

class TestBasics:
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        # store current pysat directory
        self.data_path = pysat.data_dir
        
        # create temporary directory  
        dir_name = tempfile.gettempdir()
        pysat.utils.set_data_dir(dir_name, store=False)

        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing, 
                                        clean_level='clean')
        # create testing directory
        prep_dir(self.testInst)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        remove_files(self.testInst)
        try:
            pysat.utils.set_data_dir(self.data_path, store=False)
        except:
            pass
        del self.testInst
    
    def test_basic_writing_and_reading_netcdf4_default_format(self):
        # create a bunch of files by year and doy
        from unittest.case import SkipTest
        try:
            import netCDF4
        except ImportError:
            raise SkipTest
  
        prep_dir(self.testInst)            
        outfile = os.path.join(self.testInst.files.data_path, 'test_ncdf.nc')
        self.testInst.load(2009,1)
        self.testInst.to_netcdf4(outfile)

        loaded_inst, meta = pysat.utils.load_netcdf4(outfile)
        self.testInst.data = self.testInst.data.reindex_axis(sorted(self.testInst.data.columns), axis=1)
        loaded_inst = loaded_inst.reindex_axis(sorted(loaded_inst.columns), axis=1)
        assert(np.all(self.testInst.data == loaded_inst))

    def test_basic_writing_and_reading_netcdf4_default_format_higher_order(self):
        # create a bunch of files by year and doy
        from unittest.case import SkipTest
        try:
            import netCDF4
        except ImportError:
            raise SkipTest
        test_inst = pysat.Instrument('pysat', 'testing2d')    
        prep_dir(test_inst)
        outfile = os.path.join(test_inst.files.data_path, 'test_ncdf.nc')
        test_inst.load(2009,1)
        test_inst.to_netcdf4(outfile)
        loaded_inst, meta = pysat.utils.load_netcdf4(outfile)
        test_inst.data = test_inst.data.reindex_axis(sorted(test_inst.data.columns), axis=1)
        loaded_inst = loaded_inst.reindex_axis(sorted(loaded_inst.columns), axis=1)
        prep_dir(test_inst)
        
        # test Series of DataFrames
        test_list = []
        #print (loaded_inst.columns)
        for frame1, frame2 in zip(test_inst.data['profiles'], loaded_inst['profiles']):
            test_list.append((frame1 == frame2).all())
        loaded_inst.drop('profiles', inplace=True, axis=1) 
        test_inst.data.drop('profiles', inplace=True, axis=1)    
        assert(np.all((test_inst.data == loaded_inst).all()))


    def test_basic_writing_and_reading_netcdf4_multiple_formats(self):
        # create a bunch of files by year and doy
        from unittest.case import SkipTest
        try:
            import netCDF4
        except ImportError:
            raise SkipTest
            
        outfile = os.path.join(self.testInst.files.data_path, 'test_ncdf.nc')
        self.testInst.load(2009,1)
        check = []
        for format in ['NETCDF3_CLASSIC','NETCDF3_64BIT', 'NETCDF4_CLASSIC', 'NETCDF4']:
            self.testInst.to_netcdf4(outfile, format=format)
            loaded_inst, meta = pysat.utils.load_netcdf4(outfile, format=format)
            self.testInst.data = self.testInst.data.reindex_axis(sorted(self.testInst.data.columns), axis=1)
            loaded_inst = loaded_inst.reindex_axis(sorted(loaded_inst.columns), axis=1)
            check.append(np.all(self.testInst.data == loaded_inst))
        assert(np.all(check))

#######################
### test pysat data dir options
    def test_set_data_dir(self):
        saved_dir = self.data_path
        # update data_dir
        pysat.utils.set_data_dir('.')
        check1 = (pysat.data_dir == '.')
        if saved_dir is not '':
            pysat.utils.set_data_dir(saved_dir)
            check2 = (pysat.data_dir == saved_dir)
        else:
            check2 = True
        assert check1 & check2

    def test_set_data_dir_no_store(self):
        import sys
        if sys.version_info[0] >= 3:
            if sys.version_info[1] < 4:
                import imp
                re_load = imp.reload
            else:
                import importlib
                re_load = importlib.reload
        else:
            re_load = reload

        saved_dir = self.data_path #pysat.data_dir
        # update data_dir
        pysat.utils.set_data_dir('.', store=False)
        check1 = (pysat.data_dir == '.')
        pysat._files = re_load(pysat._files)
        pysat._instrument = re_load(pysat._instrument)
        re_load(pysat)

        check2 = (pysat.data_dir == saved_dir)
        if saved_dir is not '':
            pysat.utils.set_data_dir(saved_dir, store=False)
            check3 = (pysat.data_dir == saved_dir)
        else:
            check3 = True

        assert check1 & check2 & check3        
                        
    def test_initial_pysat_load(self):
        import shutil
        saved = False
        try:
            root = os.path.join(os.getenv('HOME'), '.pysat')
            new_root = os.path.join(os.getenv('HOME'), '.saved_pysat')
            shutil.move(root, new_root)
            saved = True
        except:
            pass
            
        re_load(pysat)
        
        try:
            if saved:
                # remove directory, trying to be careful
                os.remove(os.path.join(root, 'data_path.txt'))
                os.rmdir(root)
                shutil.move(new_root, root)
        except:
            pass

        assert True