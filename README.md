# dexvert - Decompress EXtract conVERT

Convert 626 old file formats into modern ones. Powered by NodeJS, Gentoo and a ton of helper programs.

See [SUPPORTED.md](SUPPORTED.md) and [UNSUPPORTED.md](UNSUPPORTED.md) for file formats that are supported or unsupported.

THANK YOU to these AMAZING projects: [abydos](http://snisurset.net/code/abydos/), [deark](https://entropymine.com/deark/), [recoil](http://recoil.sourceforge.net/), [xmp](http://xmp.sourceforge.net/) and so many more.

## Install
See [INSTALL.md](INSTALL.md)

## Usage
```
Usage: dexvert [options] <inputFilePath> <outputDirPath>

Processes <inputFilePath> converting or extracting files into <outputDirPath>

Options:
  --verbose [level]                              Show additional info when processing. Levels 1 to 6 where 6 is most verbose
  --brute [family...]                            If unable to identify <inputFilePath>, try converting anyways
  		Pass a comma delimited list of families to brute force try
  		Valid families: archive document audio music video image 3d font text executable rom other or all
  		Successes will be stored in <outputDirPath>/<family>/<format>/ sub dirs
  		WARNING: Multiple successes could use a lot of disk space
  --keepGoing                                    When brute forcing, don't stop at the first success. Try them all.
  --alwaysBrute                                  When brute forcing, always brute force, even if we have an exact id match.
  --outputState                                  If set, will output the state as JSON
  --outputStateToFile [filePath]                 If set, will output the state as JSON to the given filePath
  --brutePrograms                                If unable to identify <inputFilePath> just run every available program on it
  --dontTransform                                If a file can't be converted, dexvert will try different transforms to convert it.
  --useTmpOutputDir                              If set, dexvert won't clobber the output dir
  --programFlag [program:flagName:flagValue...]  If set, the given flagName and flagValue will be used for program. Possible flags include:
      bchunk:bchunkSwapByteOrder                 If set to true, will swap the byte ordering for WAVs extracted from audio tracks with bchunk
      uniso:offset                               Extract ISO starting at this particular byte offset. Default: 0
      uniso:hfs                                  Set this to true to process the iso as a MacOS HFS disc. Default: false
      unlzx:unlzxListOnly                        If set to true, only list out the the files in the archive and set meta info, don't actually extract. Default: false
      unoconv:unoconvType                        Which format to transform into ("svg", "csv", "pdf", "png", etc). Default is "png" for images or "pdf" for everything else.
      file:allMatches                            Set this to true to return ALL matches from the file command, instead of just 1. Default: false
      ansilove:ansiloveType                      Which ansilove format to use. Default: Let ansilove decide
      convert:convertExt                         Which extension to convert to (".png", ".webp", ".svg"). Default: .png
      convert:flip                               Set this to true to flip the image vertically. Default: false
      convert:removeAlpha                        Set this to true to remove the alpha channel and produce a flat, opaque image. Default: false
      deark:dearkModule                          Which deark module to forcibly set. Default: Let deark decide
      deark:dearkOpts                            An array of additional -opt <option> arguments to pass to deark
      deark:dearkCharOutput                      Which type of output to use when converting character based files. Can be "image" or "html" Default: Let deark decide.
      deark:dearkRemoveDups                      Remove any duplicate output files, based on sum. Default: false
      deark:dearkJoinFrames                      Treat output files as individual images frames of an animation and join them together as an MP4
      deark:dearkGIFDelay                        Duration of delay between animation frames. Default: 12
      deark:keepAsGIF                            If dearkJoinFrames is set, leave the animation as a GIF, don't convert to MP4
      fig2dev:fig2devType                        Which image format to convert to ("png" for example). Default: svg
      sidplay2:sidSubTune                        Specify which sub tune to convert, zero based. Default: 1
      sidplay2:sidSongLength                     Duration of time to play the SID song. Default: Let sidplay2 decide
      timidity:midiFont                          Which midifont to use to convert (eaw, fluid, roland, creative, freepats, windows) Default: eaw
      uade123:uadeType                           Which 'player' file to use for conversion. Default: Let uade123 decide
      ffmpeg:ffmpegExt                           Which extension to convert into (".png", ".mp3", ".mp4", ".flac", etc). Default for image is .png, audio is .mp3 otherwise .mp4
      ffmpeg:ffmpegFormat                        Specify which format to treat the input file as. Default: Let ffmpeg decide
      ffmpeg:ffmpegFPS                           What frame rate to specify for conversion. Default: Let ffmpeg decide
  -h, --help                                     display help for command

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

A server needs to be run in the background before doing any transformations.
This server will start a background unoconv daemon and also run several emulator instances of win2k, amiga, etc.
It also runs a tensorServer python web server that loads the tensorflow models used by dexvert to determine if image conversion was successful.
Start this by kicking off: 'bin/runServers.sh'

Use dexvert as a nodejs module:

```javascript
const dexvert = require("dexvert");

dexvert.process(inputFilePath, outputDirPath, options, cb);
dexvert.identify(inputFilePath, options, cb);
```

## Test Suite
The sample files used for tests are available here: https://telparia.com/fileFormatSamples/
		