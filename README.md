# gtail - Graylog Tail

A tool to tail Graylog logs in "real-time" using the Graylog REST API.

## Usage

### Watch all logs

`gtail`

### List streams

`gtail --list-streams`

### Watch a stream

`gtail --stream mississippi`

### Watch more than one stream

`gtail --stream nile amazon`

### Watch for query keywords

`gtail --query some query here`

This uses Graylog's search mechanism, so you can use `field: value` syntax.

### Watch a single stream for query keywords

`gtail --stream nile --query crocodile`

### Full usage instructions

`gtail --help`

## Installation

(Optional) virtualenv setup:

```
virtualenv env
. env/bin/activate
```

Install:

```
pip install git+git://github.com/bvargo/gtail.git
```

### Configuration File

Put the following configuration file in `~/.gtail`, modifying the settings as
appropriate.

```
[server]
; Graylog REST API
uri: http://graylog.example.com:12900
; optional username and password
username: USERNAME
password: PASSWORD
```
