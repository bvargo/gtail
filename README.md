# gtail - Graylog Tail

A tool to tail Graylog logs in "real-time" using the Graylog REST API.

**Note: This project is no longer actively developed.**

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

## Configuration

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

# License

Copyright (C) 2014 Brandon Vargo

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
