#!/usr/bin/env python3

import testUtils

import argparse
import subprocess

Print=testUtils.Utils.Print

def errorExit(msg="", errorCode=1):
    Print("ERROR:", msg)
    exit(errorCode)

parser = argparse.ArgumentParser()
parser.add_argument("-v", help="verbose", action='store_true')
parser.add_argument("--not-noon", help="This is not the Noon branch.", action='store_true')
parser.add_argument("--dump-error-details",
                    help="Upon error print etc/eosio/node_*/config.ini and var/lib/node_*/stderr.log to stdout",
                    action='store_true')

args = parser.parse_args()
debug=args.v
amINoon=not args.not_noon
dumpErrorDetails=args.dump_error_details

testUtils.Utils.Debug=debug

killEosInstances=True
topo="mesh"
delay=1
pnodes=1
total_nodes=pnodes
actualTest="tests/nodeos_run_test.py"
if not amINoon:
    actualTest="tests/eosd_run_test.py"
    testUtils.Utils.iAmNotNoon()

cluster=testUtils.Cluster()
testSuccessful = False
try:
    Print("BEGIN")
    cluster.killall()
    cluster.cleanup()

    Print(
        "producing nodes: %s, non-producing nodes: %d, topology: %s, delay between nodes launch(seconds): %d"
        % (total_nodes, 0, topo, delay)
    )
    Print("Stand up cluster")
    if cluster.launch(total_nodes, total_nodes, topo, delay) is False:
        errorExit("Failed to stand up eos cluster.")

    Print ("Wait for Cluster stabilization")
    # wait for cluster to start producing blocks
    if not cluster.waitOnClusterBlockNumSync(3):
        errorExit("Cluster never stabilized")

    cmd = f'{actualTest} --dont-launch {"-v" if debug else ""} {"" if amINoon else "--not-noon"}'
    Print(f'Starting up {"nodeos" if amINoon else "eosd"} test: {actualTest}')
    Print("cmd: %s\n" % (cmd))
    if subprocess.call(cmd, shell=True) != 0:
        errorExit("failed to run cmd.")

    testSuccessful=True
    Print("\nEND")
finally:
    if not testSuccessful and dumpErrorDetails:
        cluster.dumpErrorDetails()
        Print("== Errors see above ==")

    if killEosInstances:
        Print("Shut down the cluster and cleanup.")
        cluster.killall()
        cluster.cleanup()

exit(0)
