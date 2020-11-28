# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Function implementation"""

import logging
from resilient_circuits import ResilientComponent, function, handler, StatusMessage, FunctionResult, FunctionError
import subprocess, os, sys, datetime, re, json

PACKAGE_NAME = "iocchecker"

def plog(ltype,lmsg):
        dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lstr=dt+"  "+ltype+": "+lmsg+"\n"
        os.write(1, bytes(lstr.encode('utf-8')))
def jprint(jobj,silent=False):
        if silent:
                print(json.dumps(jobj, sort_keys=True, indent=4))
        else:
                plog("DEBUG",json.dumps(jobj, sort_keys=True, indent=4))
def run(cmd,returnexitcode=0):
        returncmd=""
        output=""
        if returnexitcode == 1:
                returncmd="> /dev/null 2>>/tmp/lm-error.log; echo $?"
        try:
#                p = subprocess.Popen(str(cmd+returncmd).split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                p = subprocess.Popen(str(cmd+returncmd), stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE, shell=True)
                p.wait()
                (output, err) = p.communicate()
        except Exception as e:
                print("ERROR %s command execution failed with %s" % (str(cmd+returncmd).split(" "),str(e)))
        return output


class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'iocchecker''"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get(PACKAGE_NAME, {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get(PACKAGE_NAME, {})

    @function("iocchecker")
    def _iocchecker_function(self, event, *args, **kwargs):
        """Function: None"""
        try:

            # Get the wf_instance_id of the workflow this Function was called in
            wf_instance_id = event.message["workflow_instance"]["workflow_instance_id"]

            yield StatusMessage("Starting 'iocchecker' running in workflow '{0}'".format(wf_instance_id))

            # Get the function parameters:
            attachment_name = kwargs.get("attachment_name")  # string
            attachment_id = kwargs.get("attachment_id")  # number
            incident_id = kwargs.get("incident_id")  # number
            inc_id = incident_id

            log = logging.getLogger(__name__)
            log.info("attachment_id: %s", attachment_id)
            log.info("attachment_name: %s", attachment_name)
            log.info("incident_id: %s", incident_id)
            attachment_id = str(attachment_id)
            with open(attachment_name, "w+b") as temp:
                attachment_name = temp.name
                data = self.rest_client().get_content("/incidents/{0}/attachments/{1}/contents".format(inc_id,attachment_id))
                temp.write(data)
            log.info("Attachment Name:  "+str(attachment_name))
            cmd="./parallel.sh "+attachment_name
            out=run("./parallel.sh "+attachment_name)
            ##############################################
            # PUT YOUR FUNCTION IMPLEMENTATION CODE HERE #
            ##############################################

            yield StatusMessage("Finished 'iocchecker' that was running in workflow '{0}'".format(wf_instance_id))

            results = {
                "content": "Action Summary:\n--\n Command: '"+cmd+"' processed successfully.\nLogs:\n--\n "+out
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()
