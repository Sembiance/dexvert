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

Some background servers need to be running in order for dexvert to operate correctly. You can run them in 'bin/runServers.sh'
bin/dexserv runs unoconv and handles generating unique numbers for cd daemon mounting (which sadly, is a littly buggy)
The tensorServer runs a python web server that loads the tensorflow models used by dexvert to determine if image conversion was successful.

Use as a nodejs module:

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
