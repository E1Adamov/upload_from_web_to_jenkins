import os
import time
import shlex
import shutil
import threading
import subprocess
from typing import *
from zipfile import ZipFile

import config
from python import helper, global_objects


class AltDDataHandler:
    def __init__(self):
        self.server_path = helper.get_server_location()
        self.temp_dir = None
        self.temp_alt_d_dir = None
        self.temp_support_files_dir = None
        self.temp_support_files_zip_dir = None

    def start_jenkins_upload_thread(self):
        submit_to_jenkins_thread = threading.Thread(target=self.handle_alt_d,
                                                    args=(global_objects.q,),
                                                    daemon=True)
        submit_to_jenkins_thread.start()

    def handle_alt_d(self, q):
        while True:
            fields = q.get()
            self.make_temp_dirs()
            self.save_alt_d_zip(fields['alt_d_file'])
            self.save_support_files(fields['support_files'])
            self.archive_support_files()
            self.post_to_jenkins(fields)
            self.clear_temp_dir()
            time.sleep(10)
            q.task_done()

    def clear_temp_dir(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def make_temp_dirs(self, ):
        timestamp = helper.get_file_timestamp()

        self.temp_dir = os.path.join(self.server_path, config.TEMP, timestamp)
        os.mkdir(self.temp_dir)

        self.temp_alt_d_dir = os.path.join(self.temp_dir, config.TPATH_REPORT)
        os.mkdir(self.temp_alt_d_dir)

        self.temp_support_files_dir = os.path.join(self.temp_dir, config.TPATH_SF)
        os.mkdir(self.temp_support_files_dir)

        self.temp_support_files_zip_dir = os.path.join(self.temp_dir, config.TPATH_SF_ZIP)
        os.mkdir(self.temp_support_files_zip_dir)

    def save_alt_d_zip(self, alt_d: Dict):
        alt_d_dump_file_path = os.path.join(self.temp_alt_d_dir, alt_d['name'])
        helper.save_bin_to_file(alt_d['data'], alt_d_dump_file_path)

    def save_support_files(self, support_files: List):
        for sf in support_files:
            file_path = os.path.join(self.temp_support_files_dir, sf['name'])
            helper.save_bin_to_file(sf['data'], file_path)

    def get_jenkins_curl_dict(self, fields: Dict):
        jenkins_curl_dict = dict()
        jenkins_curl_dict['jira_issue'] = fields['jiraIssueNumber']
        jenkins_curl_dict['comments'] = fields['comments']
        jenkins_curl_dict['alt_d_zip'] = os.path.join(self.temp_alt_d_dir, fields['alt_d_file']['name'])
        jenkins_curl_dict['support_files_zip'] = os.path.join(self.temp_support_files_zip_dir, config.SF_ZIP_NAME)
        return jenkins_curl_dict

    def archive_support_files(self, ):
        support_files_folder = os.path.join(self.temp_support_files_dir)
        sf_temp_folder = os.path.join(self.temp_support_files_zip_dir)
        support_files_zip_file_name = os.path.join(sf_temp_folder, config.SF_ZIP_NAME)

        with ZipFile(support_files_zip_file_name, 'w') as zipf:
            for folder, sub_folders, file_names in os.walk(support_files_folder):
                for file_name in file_names:
                    file_path = os.path.join(folder, file_name)
                    zipf.write(file_path, file_name)

    def post_to_jenkins(self, fields):
        jenkins_curl_dict = self.get_jenkins_curl_dict(fields)

        # valid example
        # cmd = r'''curl -X POST http://domain.com/view/All/job/_test_AltD_FromTheField/build
        # --form file0=@C:\\path\\logfile.zip
        # --form file1=@C:\\path\\support_files.zip
        # --form json="{\"parameter\": [{\"name\":\"logfile.zip\", \"file\":\"file0\"},
        #              {\"name\":\"support_files/support_files.zip\", \"file\":\"file1\"},
        #              {\"name\":\"Uploading comments\", \"value\":\"Python comments \"},
        #              {\"name\":\"Jira issue number\", \"value\":\"<Issue number>\"}]}"'''

        cmd = r'''curl -X POST $JenkinsUrl 
                  --form file0=@$AltDZip 
                  --form file1=@$SupportFilesZip 
                  --form json="{\"parameter\": [{\"name\":\"logfile_altd.zip\", \"file\":\"file0\"},
                               {\"name\":\"support_files/support_files.zip\", \"file\":\"file1\"},
                               {\"name\":\"Uploading comments\", \"value\":\"$Comments\"},
                               {\"name\":\"Jira issue number\", \"value\":\"$JiraIssue\"}]}"'''

        cmd = cmd.replace('$JenkinsUrl', config.J_POST_URL)
        cmd = cmd.replace('$AltDZip', jenkins_curl_dict['alt_d_zip'].replace('\\', r'\\'))
        cmd = cmd.replace('$SupportFilesZip', jenkins_curl_dict['support_files_zip'].replace('\\', r'\\'))
        cmd = cmd.replace('$Comments', jenkins_curl_dict['comments'])
        cmd = cmd.replace('$JiraIssue', jenkins_curl_dict['jira_issue'])

        args = shlex.split(cmd)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()

        helper.log(stdout)
        helper.log(stderr)
