"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	testUtil = require(path.join(__dirname, "testUtil.js")),
	fileUtil = require("@sembiance/xutil").file,
	printUtil = require("@sembiance/xutil").print,
	hashUtil = require("@sembiance/xutil").hash,
	diffUtil = require("@sembiance/xutil").diff,
	C = require(path.join(__dirname, "..", "lib", "C.js")),
	dexvert = require(path.join(__dirname, "..", "lib", "dexvert.js")),
	argv = require("minimist")(process.argv.slice(2), {boolean : true}),
	fs = require("fs"),
	os = require("os"),
	tiptoe = require("tiptoe");

if(argv.help)
{
	XU.log`Usage: node test-process.js [options]

Will test all sample files to ensure dexvert.process() works correctly.

Options:
  --help                Display help/usage
  --format=<format>     Can pass a specific format to limit testing to that format, example: archive/zip
  --full                Run ALL tests, even long running ones
  --record              Take the results of the identifications and save them as the future expected results`;
	process.exit(0);
}

// Can specificy family : { formatid : ["subPath/file.png", /.txt$/]} to ignore the file subpath when doing SHA1 checking
const SHA1_IGNORE_FILES =
{
	archive :
	{
		director : [/.png$/]
	}
};

const cpuCount = os.cpus().length;
const testDataFilePath = path.join(testUtil.DATA_DIR_PATH, "process.json");
let testData = null;

tiptoe(
	function findSampleFiles()
	{
		printUtil.majorHeader("Process Test", {prefix : "\n"});
		XU.log`Loading test data and finding sample files...`;

		fs.readFile(testDataFilePath, XU.UTF8, this.parallel());
		testUtil.findSupportedSampleFilePaths(this.parallel());
	},
	function testSampleFiles(_testData, sampleFilePaths)
	{
		testData = JSON.parse(_testData);

		this.data.sampleFilePaths = sampleFilePaths;

		if(argv.format)
			sampleFilePaths.filterInPlace(sampleFilePath => path.relative(testUtil.SAMPLE_DIR_PATH, sampleFilePath).startsWith(argv.format));

		XU.log`\nTesting ${sampleFilePaths.length} sample files...`;

		sampleFilePaths.parallelForEach((sampleFilePath, subcb) => testSampleFile(sampleFilePath, false, subcb), this, cpuCount);
	},
	function saveTestDataIfNeeded()
	{
		if(argv.record)
			fs.writeFile(testDataFilePath, JSON.stringify(testData), XU.UTF8, this);
		else
			this();
	},
	function runParallelTests()
	{
		if(!argv.full)
			return this();

		XU.log`\nTesting parallel friendlyness with ${cpuCount} at once for each sample file...`;
		this.data.sampleFilePaths.serialForEach(testParallel, this);
	},
	XU.FINISH
);

function testParallel(sampleFilePath, cb)
{
	tiptoe(
		function runManyInParallel()
		{
			[].pushMany(1, cpuCount).parallelForEach((ignoreMe, parCB) => testSampleFile(sampleFilePath, true, parCB), this, cpuCount);
		},
		function checkResults(results)
		{
			if(results.length!==cpuCount || results.some(result => result!==true))
				testUtil.logResult("FAIL", path.relative(testUtil.SAMPLE_DIR_PATH, sampleFilePath), `Parallelzation test failed: ${XU.c.fg.white + results.join(", ")}`);
			else
				testUtil.logResult("PASS", path.relative(testUtil.SAMPLE_DIR_PATH, sampleFilePath));

			this();
		},
		cb
	);
}

function testSampleFile(sampleFilePath, silent, cb)
{
	const sampleSubFilePath = path.relative(testUtil.SAMPLE_DIR_PATH, sampleFilePath);
	const tmpDirPath = fileUtil.existsSync("/mnt/ram/tmp") ? "/mnt/ram/tmp" : os.tmpdir();
	const outDirPath = fileUtil.generateTempFilePath(tmpDirPath, "test-process");

	tiptoe(
		function createOutDir()
		{
			fs.mkdir(outDirPath, {recursive : true}, this);
		},
		function performProcess()
		{
			this.capture();

			dexvert.process(sampleFilePath, outDirPath, {tmpDirPath, verbose : false}, this);
		},
		function validateResults(err, results)
		{
			if(err)
				return this(undefined, "FAIL", err.toString(), err);

			const newTestData = {processed : !!results.processed};
			if(results.unsupported)
				newTestData.unsupported = true;
			if(results.input.meta)
				newTestData.inputMeta = results.input.meta;
			if(results.processed && results.output.files)
			{
				newTestData.files = {};
				results.output.files.forEach(outSubFilePath => { newTestData.files[outSubFilePath] = hashUtil.hash("sha1", fs.readFileSync(path.join(outDirPath, outSubFilePath))); });
			}

			if(argv.record)
			{
				testData[sampleSubFilePath] = newTestData;
				return this(undefined, "SKIP", "Skipped because we are recording");
			}

			if(!testData.hasOwnProperty(sampleSubFilePath))
				return this(undefined, "FAIL", "No test data for this file", newTestData);

			const sampleTestData = testData[sampleSubFilePath];
			if(!!results.processed!=sampleTestData.processed)	// eslint-disable-line eqeqeq
				return this(undefined, "FAIL", `Expected processed to be ${XU.c.fg.white + sampleTestData.processed + XU.c.fg.orange} but got ${XU.c.fg.white + results.processed + XU.c.fg.orange} instead`);

			if(!Object.equals(sampleTestData.inputMeta, results.input.meta))
				return this(undefined, "FAIL", "input.meta does not match expected result: " + diffUtil.diff(sampleTestData.inputMeta, results.input.meta));

			if(sampleTestData.files && !results.output.files)
				return this(undefined, "FAIL", `Expected to have ${XU.c.fg.white + Object.keys(sampleTestData.files).length + XU.c.fg.orange} files but didn't find any`);

			if(!sampleTestData.files && results.output.files)
				return this(undefined, "FAIL", `Expected to have no files but found ${XU.c.fg.white + results.output.files.length + XU.c.fg.orange} instead`);
			
			const expectedFiles = sampleTestData.files ? Object.keys(sampleTestData.files) : [];
			if(results.output.files && expectedFiles.length!==results.output.files.length)
				return this(undefined, "FAIL", `Expected ${XU.c.fg.white + expectedFiles.length + XU.c.fg.orange} files, but only got ${XU.c.fg.white + results.output.files.length}`);

			const {family, formatid} = results.id;
			(results.output.files || []).forEach(outSubFilePath =>
			{
				if(SHA1_IGNORE_FILES[family] && SHA1_IGNORE_FILES[family][formatid] && SHA1_IGNORE_FILES[family][formatid].some(m => C.flexMatch(outSubFilePath.toLowerCase(), m)))
				{
					expectedFiles.removeOnce(outSubFilePath);
					return;
				}

				if(!sampleTestData.files.hasOwnProperty(outSubFilePath))
					return this(undefined, "FAIL", `Unexpected file result: ${XU.c.fg.white + outSubFilePath}`);
				
				if(hashUtil.hash("sha1", fs.readFileSync(path.join(outDirPath, outSubFilePath)))!==sampleTestData.files[outSubFilePath])
					return this(undefined, "FAIL", "SHA1 sum mistmatch", outSubFilePath);

				expectedFiles.removeOnce(outSubFilePath);
			});

			if(sampleTestData.files && expectedFiles.length>0)
				return this(undefined, "FAIL", `The following expected files were not found: ${XU.c.fg.white + expectedFiles.join(", ")}`);

			this(undefined, "PASS");
		},
		function cleanup(status, msg="", ...args)
		{
			if(!silent)
				testUtil.logResult(status, sampleSubFilePath, msg, ...args);

			this.parallel()(undefined, status==="PASS");
			fileUtil.unlink(outDirPath, this.parallel());
		},
		cb
	);
}
