#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# -
# Copyright (c) 2019 Alex Richardson
# All rights reserved.
#
# This software was developed by SRI International and the University of
# Cambridge Computer Laboratory under DARPA/AFRL contract FA8750-10-C-0237
# ("CTSRD"), as part of the DARPA CRASH research programme.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
import sys
import subprocess
from pathlib import Path
from run_tests_common import boot_cheribsd


def convert_kyua_db_to_junit_xml(db_file: Path, output_file: Path):
    assert output_file.resolve() != db_file.resolve()
    with output_file.open("w") as output_stream:
        command = ["kyua", "report-junit", "--results-file=" + str(db_file)]
        boot_cheribsd.run_host_command(command, stdout=output_stream)
        # TODO: xml escape the file?
        if not boot_cheribsd.PRETEND:
            fixup_kyua_generated_junit_xml(output_file)

def fixup_kyua_generated_junit_xml(xml_file: Path):
    boot_cheribsd.info("Updating statistics in JUnit file ", xml_file)
    # Process junit xml file with junitparser to update the number of tests, failures, total time, etc.
    import junitparser
    xml = junitparser.JUnitXml.fromfile(str(xml_file))
    xml.update_statistics()
    xml.write()
    boot_cheribsd.run_host_command(["grep", "<testsuite", str(xml_file)])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("db", help="The database to convert")
    parser.add_argument("xml", nargs=argparse.OPTIONAL, help="The output file (or - for stdout). Defaults to the db file with suffix .xml")
    args = parser.parse_args()
    if not args.xml:
        output = Path(args.db).with_suffix(".xml")
    elif args.xml == "-":
        output = Path("/dev/stdout")
    else:
        output = Path(args.xml)
    convert_kyua_db_to_junit_xml(Path(args.db), output)