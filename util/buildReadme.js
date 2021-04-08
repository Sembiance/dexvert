"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

tiptoe(
	function findPrograms()
	{
		runUtil.run(path.join(__dirname, "..", "bin", "dexid"), ["--help"], runUtil.SILENT, this.parallel());
		runUtil.run(path.join(__dirname, "..", "bin", "dexvert"), ["--help"], runUtil.SILENT, this.parallel());
		fileUtil.glob(path.join(__dirname, "..", "lib", "format"), "**/*.js", {nodir : true}, this.parallel());
	},
	function generateReadme(dexidUsage, dexvertUsage, formatFilePaths)
	{
		fs.writeFile(path.join(__dirname, "..", "README.md"), `# dexvert - Decompress EXtract conVERT

Convert ${formatFilePaths.map(formatFilePath => require(formatFilePath).meta).filter(f => f?.name && !f.unsupported).length.toLocaleString()} old file formats into modern ones. Powered by NodeJS, Gentoo and a ton of helper programs.

See [SUPPORTED.md](SUPPORTED.md) and [UNSUPPORTED.md](UNSUPPORTED.md) for file formats that are supported or unsupported.

THANK YOU to these AMAZING projects: [abydos](http://snisurset.net/code/abydos/), [deark](https://entropymine.com/deark/), [recoil](http://recoil.sourceforge.net/), [xmp](http://xmp.sourceforge.net/) and so many more.

## Install
See [INSTALL.md](INSTALL.md)

## Usage
\`\`\`
${dexvertUsage}
\`\`\`

You can also just 'identify' what a file is, without processing it by running 'dexid':
\`\`\`
${dexidUsage}
\`\`\`

A server needs to be run in the background before doing any transformations.
This server will start a background unoconv daemon and also run several emulator instances of win2k, amiga, etc.
It also runs a tensorServer python web server that loads the tensorflow models used by dexvert to determine if image conversion was successful.
Start this by kicking off: 'bin/runServers.sh'

Use dexvert as a nodejs module:

\`\`\`javascript
const dexvert = require("dexvert");

dexvert.process(inputFilePath, outputDirPath, options, cb);
dexvert.identify(inputFilePath, options, cb);
\`\`\`

## Test Suite
The sample files used for tests are available here: https://telparia.com/fileFormatSamples/
		`, XU.UTF8, this);
	},
	XU.FINISH
);
