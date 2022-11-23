# -*- coding: utf-8 -*-
"""
#####################################################
:mod:`automarking.utils` -- Handy Utilities
#####################################################

.. moduleauthor:: Dan Campbell <danielcampbell2097@hotmail.com>
"""

import os
import glob
import shutil
from zipfile import ZipFile


class GradeBookFix():

    def __init__(self, task_id, module_code, task_file_extensions, gradebook_path, cwd):
        self.task_id = task_id
        self.module_code = module_code
        self.task_file_extensions = task_file_extensions
        self.gradebook_path = gradebook_path
        self.current_working_directory = cwd
        self.OUT_DIR = '{}fixed_gradebook/'.format(self.current_working_directory)
        self.GB_DIR_ORIGINAL = '{}gradebook_old'.format(self.current_working_directory)
        self.TEMP_DIR = '{}temp/'.format(self.current_working_directory)
        self.DIR_LIST = [self.TEMP_DIR, self.GB_DIR_ORIGINAL, self.OUT_DIR]

    def __cleanup(self):
        for dir in self.DIR_LIST:
            if os.path.exists(dir):
                shutil.rmtree(dir)

    def __create_temp_directories(self):
        if not os.path.exists(self.OUT_DIR):
            os.mkdir(self.OUT_DIR)

    def __extract_gradebook(self):
        zip = ZipFile(self.gradebook_path)
        for archive in zip.namelist():
            if '__MACOSX' not in archive:
                zip.extract(archive, path=self.GB_DIR_ORIGINAL)

    def __create_fixed_zip(self, original_filename):
        print('processing ' + original_filename)
        for path, subdirs, files in os.walk(self.TEMP_DIR):
            if '__MACOSX' not in path:
                for name in files:
                    if any(ex in name for ex in self.task_file_extensions):

                        print(str(path))
                        try:
                            shutil.move(os.path.join(path, name), self.TEMP_DIR)
                        except:
                            # file already exists
                            pass
            else:
                if os.path.exists(path):
                    shutil.rmtree(path)
        # Removes subdirectories
        for element in os.scandir(self.TEMP_DIR):
            if element.is_dir():
                shutil.rmtree(element)

        archive_name = os.path.basename(original_filename)
        destination = self.OUT_DIR + archive_name.strip('.zip')
        source = self.TEMP_DIR
        shutil.make_archive(base_name=destination, format='zip',
                            base_dir=source, root_dir=os.getcwd())

        if os.path.exists(self.TEMP_DIR):
            shutil.rmtree(self.TEMP_DIR)

    def __process_submission(self):
        DL_ZIP_FILES = []

        for path in glob.glob(self.GB_DIR_ORIGINAL + '/**/*zip', recursive=True):
            DL_ZIP_FILES.append(path)

        for archive in DL_ZIP_FILES:
            name = "/" + archive.split('/')[-1]
            archive_name = archive
            try:
                archive = ZipFile(archive)

                count = sum(map(lambda x: self.task_id not in x, archive.namelist()))
                nested = sum(map(lambda x: self.task_id in x, archive.namelist()))
                # Fixes ZIP
                if count > 1 or nested > 1:
                    a = archive.namelist()
                    archive.extractall(path=self.TEMP_DIR)
                    self.__create_fixed_zip(archive.filename)
                # Moves Zip
                else:
                    os.rename(src=archive_name, dst=self.OUT_DIR + name)
            except:
                print('The following file cannot be unzipped: {}'.format(name))
                os.rename(src=archive_name, dst=self.OUT_DIR + name)
    def __compress_modified_gradebook(self):
        print('[Ultra Gradebook] Compressing modified Gradebook')
        archive_name = os.path.expanduser(os.path.join(self.current_working_directory,
                                                       'gradebook_{}_{}_fixed'.format(self.module_code, self.task_id)))
        root_dir = os.path.expanduser(os.path.join(self.current_working_directory, self.OUT_DIR))
        shutil.make_archive(archive_name, 'zip', root_dir)

    def __remove_old_attempts(self):
        print('[Ultra Gradebook] Removing old attempts...')
        last_sub_dic = {}
        dup_subs = {}
        for path, subdirs, files in os.walk(self.GB_DIR_ORIGINAL):
            for name in files:
                parts = name.split("_")
                student = parts[1]
                last_sub_dic[student] = name
        for name in last_sub_dic.values():
            os.rename(src="{}/{}".format(self.GB_DIR_ORIGINAL, name), dst=self.OUT_DIR + name)

        # Proof
        # if student in dup_subs.keys():
        #     dup_subs[student] = dup_subs.get(student) + 1
        # else:
        #     dup_subs[student] = 1

        # print(parts)

        # dup = {k:v for (k,v) in dup_subs.items() if v > 1}
        # for student in dup.keys():
        #     print(last_sub_dic.get(student))

    def fix_zips(self):
        print('[Fixing Zips] Starting....')
        self.__cleanup()
        self.__create_temp_directories()
        self.__extract_gradebook()
        self.__process_submission()
        self.__compress_modified_gradebook()
        self.__cleanup()
        print('[Fixing Zips] Completed....')

    def ultra_gradebook_submission_download_fix(self):
        print(
        '[Ultra Gradebook] Beginning to fix Gradebook Submissions...')
        self.__cleanup()
        self.__create_temp_directories()
        self.__extract_gradebook()
        self.__remove_old_attempts()
        self.__compress_modified_gradebook()
        self.__cleanup()
        print('[Ultra Gradebook] Fixed Gradebook Submissions.')


# current_working_directory = os.path.dirname(os.path.realpath(__file__)) + '/'
# GB = current_working_directory + 'gradebook.zip'
# x = GradeBookFix(task_id='task_01', module_code='CIS1110', gradebook_path=GB, task_file_extensions=['.html'], cwd=current_working_directory)
# x..ultra_gradebook_submission_download_fix()
# x.fix_zips()
