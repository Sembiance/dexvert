# dexvert - Decompress EXtract conVERT

Convert 610 old file formats into modern ones. Powered by NodeJS, Gentoo and a ton of helper programs.

See [SUPPORTED.md](SUPPORTED.md) and [UNSUPPORTED.md](UNSUPPORTED.md) for file formats that are supported or unsupported.

THANK YOU to these AMAZING projects: [abydos](http://snisurset.net/code/abydos/), [deark](https://entropymine.com/deark/), [recoil](http://recoil.sourceforge.net/), [xmp](http://xmp.sourceforge.net/) and so many more.

## Install
See [INSTALL.md](INSTALL.md)

## Usage
```
Usage: dexvert [options] <inputFilePath> <outputDirPath>

Processes <inputFilePath> converting or extracting files into <outputDirPath>

Options:
  --verbose [level]               Show additional info when processing. Levels
                                  1 to 6 where 6 is most verbose
  --brute [family...]             If unable to identify <inputFilePath>, try converting anyways
  		Pass a comma delimited list of families to brute force try
  		Valid families: archive document audio music video image 3d font text executable rom other or all
  		Successes will be stored in <outputDirPath>/<family>/<format>/ sub dirs
  		WARNING: Multiple successes could use a lot of disk space
  --keepGoing                     When brute forcing, don't stop at the first
                                  success. Try them all.
  --alwaysBrute                   When brute forcing, always brute force, even
                                  if we have an exact id match.
  --outputState                   If set, will output the state as JSON
  --outputStateToFile [filePath]  If set, will output the state as JSON to the
                                  given filePath
  --brutePrograms                 If unable to identify <inputFilePath> just
                                  run every available program on it
  --dontTransform                 If a file can't be converted, dexvert will
                                  try different transforms to convert it.
  --useTmpOutputDir               If set, dexvert won't clobber the output dir
  --midiFont [midiFont]           Convert MIDI files with a specific midi font. Default: eaw
  		Other available fonts: fluid, roland, creative, freepats, windows
  -h, --help                      display help for command

```

You can also just 'identify' what a file is, without processing it by running 'dexid':
```
Usage: dexid [options] <inputFilePath...>

Identifies <inputFilePath>. Like an advanced 'file' command

Options:
  --verbose [level]      Show additional info when identifying. Levels 1 to 5
                         where 5 is most verbose
  --json                 Output JSON
  --jsonFile [filePath]  If set, will output the result JSON to the given
                         filePath
  -h, --help             display help for command

```

Some background servers need to be running in order for dexvert to operate correctly. You can run them in 'bin/runServers.sh'
bin/dexserv runs unoconv and handles generating unique numbers for cd daemon mounting (which sadly, is a littly buggy)
The tensorServer runs a python web server that loads the tensorflow models used by dexvert to determine if image conversion was successful.

Use as a nodejs module:

```javascript
const dexvert = require("dexvert");

dexvert.process(inputFilePath, outputDirPath, options, cb);
dexvert.identify(inputFilePath, options, cb);
```

## Test Suite
The sample files used for tests are available here: https://telparia.com/fileFormatSamples/
		