"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	path = require("path"),
	testUtil = require("./testUtil.js"),
	printUtil = require("@sembiance/xutil").print,
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	{validate} = require("./validate.js"),
	{Command} = require("commander"),
	fs = require("fs"),
	os = require("os"),
	tiptoe = require("tiptoe");

const argv = new Command().description("Will test all sample files to ensure dexvert.identify() works correctly.").
	option("--format [format]", " Can pass a specific format to limit testing to that format, example: archive/zip").
	option("--extension [ext]", "Only test files that belong to formats that have the given extension").
	option("--file [subFilePath]", "Only identify the given sample subFilePath").
	option("--verbose [level]", "Show additional info when processing. Levels 1 to 6 where 6 is most verbose").
	option("--record", "Take the results of the identifications and save them as the future expected results").
	parse(process.argv);

const testDataFilePath = path.join(testUtil.DATA_DIR_PATH, "identify.json");
let testData = null;
const startTime = Date.now();

tiptoe(
	function init()
	{
		testUtil.initSamples(this.parallel());
		validate(this.parallel());
	},
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
			sampleFilePaths.filterInPlace(sfp => path.relative(testUtil.SAMPLE_DIR_PATH, sfp).startsWith(path.join(argv.format, "/")));
		if(argv.extension)
		{
			sampleFilePaths.filterInPlace(sfp =>
			{
				const formatJSPath = path.join(__dirname, "..", "src", "format", path.basename(path.resolve(sfp, "..", "..")), `${path.basename(path.dirname(sfp))}.js`);
				if(!fileUtil.existsSync(formatJSPath))
					return false;
				return (require(formatJSPath).meta.ext || []).includes(argv.extension);
			});
		}

		XU.log`\nTesting ${sampleFilePaths.length} sample files...`;

		Object.keys(testData).subtractAll(sampleFilePaths.map(sampleFilePath => path.relative(testUtil.SAMPLE_DIR_PATH, sampleFilePath))).forEach(extraFilePath =>
		{
			if(!argv.format || !extraFilePath.startsWith(path.join(argv.format, "/")))
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
		XU.log`\nElapsed time: ${((Date.now()-startTime)/XU.SECOND).secondsAsHumanReadable()}`;
		this();
	},
	XU.FINISH
);

function testSampleFile(sampleFilePath, cb)
{
	const sampleSubFilePath = path.relative(testUtil.SAMPLE_DIR_PATH, sampleFilePath);
	const idJSONFilePath = fileUtil.generateTempFilePath(undefined, ".json");
	
	tiptoe(
		function performIdentification()
		{
			runUtil.run("dexid", ["--jsonFile", idJSONFilePath, sampleFilePath], runUtil.SILENT, this);
		},
		function loadIdentification()
		{
			fs.readFile(idJSONFilePath, XU.UTF8, this);
		},
		function validateIdentification(idsRaw)
		{
			const ids = XU.parseJSON(idsRaw);
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
		function cleanup()
		{
			fileUtil.unlink(idJSONFilePath, this);
		},
		function handleError(err)
		{
			if(err)
				testUtil.logResult("FAIL", sampleSubFilePath, "Failed due to unexpected error: ", err);

			cb();
		}
	);
}
