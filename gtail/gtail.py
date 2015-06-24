#!/usr/bin/env python
#
# Graylog Tail, an application for tailing Graylog logs
# Brandon Vargo

from collections import namedtuple
import ConfigParser
import argparse
import datetime
import os
import requests
import sys
import time
import urllib

MAX_DELAY = 10
DEFAULT_CONFIG_PATHS = [".gtail", os.path.expanduser("~/.gtail")]

# returns a bold version of text using ansi characters
def bold(text):
   make_bold = "\033[1m"
   reset = "\033[0;0m"
   return make_bold + str(text) + reset

# fetches the URL from the server
def fetch(server_config, url):
    if server_config.username and server_config.password:
        auth = (server_config.username, server_config.password)
    else:
        auth = None

    headers = {"accept": "application/json"}
    r = requests.get(url, auth=auth, headers=headers)
    return r

# gets a list of active streams
def fetch_streams(server_config):
    r = fetch(server_config, server_config.uri + "/streams")
    streams = r.json()["streams"]
    # only active streams
    streams = filter(lambda s: s["disabled"] == False, streams)

    d = dict()
    for s in streams:
        d[s["id"]] = s

    return d

# lists streams in a pretty format
def list_streams(streams):
    streams = sorted(streams.values(), key=lambda s: s["title"].lower())
    for stream in streams:
        if stream["description"]:
            print bold(stream["title"]), "-", stream["description"]
        else:
            print bold(stream["title"])

# gets messages for the given stream (None = all streams) since the last
# message ID (None = start from some recent date)
def fetch_messages(server_config,
        query = None,
        stream_ids = None,
        last_message_id = None):
    url = []
    url.append(server_config.uri)
    url.append("/search/universal/relative?range=7200&limit=100")

    # query terms
    if query:
        url.append("&query=" + urllib.quote_plus(query))
    else:
        url.append("&query=*")

    # stream ID
    if stream_ids:
        quoted = map(urllib.quote_plus, stream_ids)
        prefixed = map(lambda s: "streams:" + s, quoted)
        s = "%20OR%20".join(prefixed)
        url.append("&filter=" + s)

    # fetch
    url = ''.join(url)
    r = fetch(server_config, url)
    if r.status_code != 200:
        raise Exception("Could not fetch messages from server. " \
                "Status code: %d" % r.status_code)

    # extact each message
    messages = map(lambda m: m["message"], r.json()["messages"])

    # convert the timestamp
    for m in messages:
        m["timestamp"] = datetime.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")

    # sort by date
    messages = sorted(messages, key=lambda m: m["timestamp"])

    # exclude any messages that we've seen before
    index = None
    for i, m in enumerate(messages):
        if m["_id"] == last_message_id:
            index = i
            break
    if index is not None:
        messages = list(messages)[index + 1:]

    return messages

# pretty prints a message
# streams, if provided, is the full list of streams; it is used for pretty
# printing of the stream name
def print_message(message, streams=None):
    s = []
    if "timestamp" in message:
        timestamp = message["timestamp"]
        s.append(timestamp)
    if streams and "streams" in message:
        stream_ids = message["streams"]
        stream_names = []
        for sid in stream_ids:
            stream_names.append(streams[sid]["title"])
        s.append("[" + ", ".join(stream_names) + "]")
    if "facility" in message:
        facility = message["facility"]
        s.append(facility)
    if "level" in message:
        level = message["level"]
        s.append(level)
    if "source" in message:
        source = message["source"]
        s.append(source)
    if "loggerName" in message:
        logger_name = message["loggerName"]
        s.append(logger_name)

    if "full_message" in message:
        text = message["full_message"]
    else:
        text = message["message"]

    print bold(" ".join(map(str, s)))
    print text

# config object and config parsing
Config = namedtuple("Config", "server_config")
ServerConfig = namedtuple("ServerConfig", "uri username password")
def parse_config(config_paths):
    config = ConfigParser.RawConfigParser()
    read_paths = config.read(config_paths)
    if not read_paths:
        raise IOError("Could not read configuration file: %s" %
                ", ".join(config_paths))

    try:
        uri = config.get("server", "uri")
    except:
        raise Exception("Could not read server uri from configuration file.")

    try:
        username = config.get("server", "username")
    except:
        username = None

    try:
        password = config.get("server", "password")
    except:
        password = None

    return Config(ServerConfig(uri, username, password))

# finds all stream IDs that should be parsed
# if a stream name cannot be found, then an Exception is raised
def find_stream_ids(stream_names, streams):
    ids = []

    for stream_name in stream_names:
        ids.append(find_stream_id(stream_name, streams))

    return ids

# returns the stream ID
# if the ID cannot be found, then an exception is raised
def find_stream_id(stream_name, streams):
    # all stream names
    streams_lowercase = set()
    for stream in streams.values():
        stream_lowercase = stream["title"].lower()
        streams_lowercase.add(stream["title"].lower())

    # try to find the stream
    stream_ids = []
    for stream in streams.values():
        s = stream["title"].lower()
        if s.startswith(stream_name):
            stream_ids.append(stream["id"])

    # if more than one id, reset, and require exact name match
    if len(stream_ids) > 1:
        stream_ids = []
        for stream in streams.values():
            s = stream["title"]
            if s == stream_name:
                stream_ids.append(stream["id"])

    # if the stream was not found, error + list streams
    if not stream_ids:
        raise Exception("Stream '%s' could not be found " \
            "or is not active" % (stream_name))

    return stream_ids[0]

def main():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="Tail logs from Graylog.",
            epilog = """
Example configuration file:

[server]
; Graylog REST API
uri: http://graylog.example.com:12900
; optional username and password
username: USERNAME
password: PASSWORD

This file should be located at any of the following paths: %s.
""" % ", ".join(DEFAULT_CONFIG_PATHS))
    parser.add_argument("--stream", dest="stream_names",
            nargs="+",
            help="The name of the streams to tail. Default: all streams.")
    parser.add_argument("--list-streams", dest="list_streams",
            action="store_true",
            help="List streams and exit.")
    parser.add_argument("--query", dest="query",
            nargs="+",
            help="Query terms to search on")
    parser.add_argument("--config", dest="config_paths",
            nargs="+",
            help="Config files. Default: " + ", ".join(DEFAULT_CONFIG_PATHS))
    args = parser.parse_args()

    #
    # config file
    #

    config_paths = DEFAULT_CONFIG_PATHS
    if args.config_paths:
        config_paths = args.config_paths

    try:
        config = parse_config(config_paths)
    except Exception as e:
        print e
        return 1
    server_config = config.server_config

    #
    # find the stream
    #

    streams = fetch_streams(server_config)

    # list streams if needed
    if args.list_streams:
        list_streams(streams)
        return 0

    # parse stream name
    stream_ids = None
    if args.stream_names:
        try:
            stream_ids = find_stream_ids(args.stream_names, streams)
        except Exception as e:
            print e
            print
            list_streams(streams)
            return 1

    #
    # print log messages
    #

    last_message_id = None
    while True:
        # time-forward messages
        query = None
        if args.query:
            query = ' '.join(args.query)
        try:
            messages = fetch_messages(
                    server_config = server_config,
                    query = query,
                    stream_ids = stream_ids,
                    last_message_id = last_message_id)
        except Exception as e:
            print e
            time.sleep(MAX_DELAY)
            continue

        # print new messages
        last_timestamp = None
        for m in messages:
            print_message(m, streams)
            last_message_id = m["_id"]
            last_timestamp = m["timestamp"]

        if last_timestamp:
            seconds_since_last_message = max(0, (datetime.datetime.utcnow() - last_timestamp).total_seconds())
            delay = min(seconds_since_last_message, MAX_DELAY)
            if delay > 2:
                time.sleep(delay)
        else:
            time.sleep(MAX_DELAY)

if __name__ == "__main__":
    rc = main()
    if rc:
        sys.exit(rc)
