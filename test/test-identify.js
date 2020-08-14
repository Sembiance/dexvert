"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	path = require("path"),
	testUtil = require(path.join(__dirname, "testUtil.js")),
	printUtil = require("@sembiance/xutil").print,
	dexvert = require(path.join(__dirname, "..", "lib", "dexvert.js")),
	argv = require("minimist")(process.argv.slice(2), {boolean : true}),
	fs = require("fs"),
	os = require("os"),
	tiptoe = require("tiptoe");

if(argv.help)
{
	XU.log`Usage: node test-identify.js [options]

Will test all sample files to ensure dexvert.identify() works correctly.

Options:
  --help                Display help/usage
  --format=<format>     Can pass a specific format to limit testing to that format, example: archive/zip
  --file=<subFilePath>	Only identify the given sample subFilePath
  --verbose=<level>		Verbosity level, 1 to 5 where 5 is the most verbose
  --record              Take the results of the identifications and save them as the future expected results`;
	process.exit(0);
}

const testDataFilePath = path.join(testUtil.DATA_DIR_PATH, "identify.json");
let testData = null;
const startTime = Date.now();

tiptoe(
	function findSampleFiles()
	{
		printUtil.majorHeader("Identification Test", {prefix : "\n"});
		XU.log`Loading test data and finding sample files...`;

		fs.readFile(testDataFilePath, XU.UTF8, this.parallel());
		testUtil.findSupportedSampleFilePaths(this.parallel());
	},
	function testSampleFiles(_testData, sampleFilePaths)
	{
		testData = JSON.parse(_testData);

		const allTypes = sampleFilePaths.map(sampleFilePath => path.dirname(sampleFilePath)).unique().map(sampleFilePath => path.basename(sampleFilePath));
		const nonUniqueFormatids = allTypes.subtractOnce(allTypes.slice().unique());
		if(nonUniqueFormatids.length>0)
		{
			XU.log`Non unique formatids: ${nonUniqueFormatids}`;
			process.exit(1);
		}

		if(argv.format)
			sampleFilePaths.filterInPlace(sampleFilePath => path.relative(testUtil.SAMPLE_DIR_PATH, sampleFilePath).startsWith(`${argv.format}/`));
		
		// Filter out any unsupported formats as we have a lot of sample files for formats we don't yet support
		sampleFilePaths.filterInPlace(sampleFilePath => !require(path.join(__dirname, "..", "lib", "format", path.basename(path.resolve(sampleFilePath, "..", "..")), `${path.basename(path.dirname(sampleFilePath))}.js`)).meta.unsupported);

		XU.log`\nTesting ${sampleFilePaths.length} sample files...`;

		Object.keys(testData).subtractAll(sampleFilePaths.map(sampleFilePath => path.relative(testUtil.SAMPLE_DIR_PATH, sampleFilePath))).forEach(extraFilePath =>
		{
			if(!extraFilePath.startsWith(`${argv.format}/`))
				return;

			XU.log`${XU.cf.fg.cyan("[") + XU.c.blink + XU.cf.fg.red("EXTRA") + XU.cf.fg.cyan("]")} file path detected: ${extraFilePath}`;
			if(argv.record)
				delete testData[extraFilePath];
		});

		sampleFilePaths.shuffle().filter(sampleFilePath => !argv.file || sampleFilePath.endsWith(argv.file)).parallelForEach(testSampleFile, this, os.cpus().length);
	},
	function saveTestDataIfNeeded()
	{
		if(argv.record)
			fs.writeFile(testDataFilePath, JSON.stringify(testData), XU.UTF8, this);
		else
			this();
	},
	function outputResults()
	{
		testUtil.logFinish();
		XU.log`\nElapsed time: ${(Date.now()-startTime).secondsAsHumanReadable()}`;
		this();
	},
	XU.FINISH
);

function testSampleFile(sampleFilePath, cb)
{
	const sampleSubFilePath = path.relative(testUtil.SAMPLE_DIR_PATH, sampleFilePath);
	
	tiptoe(
		function performIdentification()
		{
			this.capture();

			dexvert.identify(sampleFilePath, {verbose : argv.verbose || 0}, this);
		},
		function validateIdentification(err, ids)
		{
			if(err)
				return testUtil.logResult("FAIL", sampleSubFilePath, err.toString(), err), this();
			
			if(!ids)
				return testUtil.logResult("FAIL", sampleSubFilePath, "No id results returned"), this();
			
			ids.filterInPlace(id =>
			{
				if(id.from!=="dexvert")
					return false;

				delete id.extensions;
				delete id.from;

				return true;
			});

			if(argv.record)
			{
				testData[sampleSubFilePath] = ids;
				testUtil.logResult("SKIP", sampleSubFilePath, "Skipped because we are recording");
				return this();
			}

			if(!testData.hasOwnProperty(sampleSubFilePath))
				return testUtil.logResult("FAIL", sampleSubFilePath, "No test data for this file", ids), this();

			let finished = false;
			ids.forEach(id =>
			{
				if(finished)
					return;

				const previd = testData[sampleSubFilePath].find(v => v.formatid===id.formatid);
				if(!previd)
					finished = testUtil.logResult("FAIL", sampleSubFilePath, "New identification detected", id);
				else if(previd.confidence!==id.confidence)
					finished = testUtil.logResult("FAIL", sampleSubFilePath, `Confidence level changed for ${XU.c.fg.white + id.formatid + XU.c.fg.orange} was ${XU.c.fg.white + previd.confidence + XU.c.fg.orange} and now ${XU.c.fg.white + id.confidence}`);
			});

			if(finished)
				return this();
			
			testData[sampleSubFilePath].forEach(previd =>
			{
				if(finished)
					return;

				const id = ids.find(v => v.formatid===previd.formatid);
				if(!id)
					finished = testUtil.logResult("FAIL", sampleSubFilePath, "Previous identification not detected", previd);
			});

			if(finished)
				return this();

			testUtil.logResult("PASS", sampleSubFilePath);

			this();
		},
		cb
	);
}
