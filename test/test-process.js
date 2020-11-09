"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	path = require("path"),
	testUtil = require("./testUtil.js"),
	fileUtil = require("@sembiance/xutil").file,
	moment = require("moment"),
	printUtil = require("@sembiance/xutil").print,
	hashUtil = require("@sembiance/xutil").hash,
	diffUtil = require("@sembiance/xutil").diff,
	{validate} = require("./validate.js"),
	dexUtil = require("../lib/dexUtil.js"),
	dexvert = require("../lib/dexvert.js"),
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
  --ext=<ext>			Only test files that belong to formats that have the given extension
  --file=<subFilePath>	Only process the given sample subFilePath
  --full                Run ALL tests, even long running ones
  --verbose=<level>		Verbosity level, 1 to 5 where 5 is the most verbose
  --record              Take the results of the identifications and save them as the future expected results`;
	process.exit(0);
}

// Can specificy family : { formatid : ["subPath/file.png", /.txt$/]} to ignore the file subpath when doing SHA1 checking
// Filenames are the OUTPUT filenames and are all converted to LOWERCASE first
const SHA1_IGNORE_FILES =
{
	archive :
	{
		// Not sure why, but the director extraction program produces different PNG files each time
		director : [/.png$/]
	},
	document :
	{
		// PDF's have unique ID's within them and also creation dates, etc which cause them to never SHA1 match the same
		"*" : [/.pdf$/]
	},
	font :
	{
		// Generated .otf files from fontforge and differ. Probably meta info or something. Didn't investigate further
		"adobeType1" : [/.otf$/]
	},
	image :
	{
		// These are screengrabs from DOSBox and due to this the images are not guaranteed to be bit perfect identical
		"3dCK" : [/.png$/],
		 "pds" : [/.png$/],

		// Inkscape/uniconvertor doesn't always produce the same exact SVG file, even with the same args and inputs.
		"cvg" : [/.svg$/],
		"eps" : [/.svg$/],
		"fig" : [/.svg$/],
		 "ps" : [/.svg$/],
		"wmf" : [/.svg$/]
	},
	music :
	{
		// These files are slightly different each time
		"med" : [/juanidance.flac$/],
		"sid" : [/.flac$/]	// The FLAC files generated from the WAVs from sidplay2 are different each time. Probably due to the analog nature of the SID chip
	},
	video :
	{
		// These are screen recordings and the videos are not guaranteed to be identical. I could in theory though check for duration, but meh.
		"disneyCFAST" : [/.mp4$/],
		"fantavision" : [/.mp4$/],
		"movieSetter" : [/.mp4$/]
	}
};

// Filenames are the OUTPUT filenames and are all converted to LOWERCASE first
const SIZE_IGNORE_FILES =
{
	image :
	{
		// These are screengrabs from DOSBox and due to this the images are not guaranteed to be the same size
		"3dCK" : [/.png$/]
	},
	document :
	{
		// The size varies by a few bytes each time, not sure why. Probably some the pdf unique id that gets generated
		"wordMac" : [/business_letter.pdf$/]
	},
	music :
	{
		// These files are slightly different each time
		"med" : [/juanidance.flac$/],
		"sid" : [/.flac$/]	// The FLAC files generated from the WAVs from sidplay2 are different each time. Probably due to the analog nature of the SID chip
	},
	video :
	{
		// These are screen recordings and the videos are not guaranteed to be identical. I could in theory though check for duration, but meh.
		"disneyCFAST" : [/.mp4$/],
		"fantavision" : [/.mp4$/],
		"movieSetter" : [/.mp4$/]
	}
};

// Usually the formatid of the directory should match what is detected by dexid
// Sadly, some formats are only identified by an extension that is shared by multiple formats (such as image/pfsFirstPublisher and image/gfaArtist and image/asciiArtEditor)
// So add them here to exempt from failing the test due to this
const FORMATID_MATCH_EXEMPT =
[
	"gfaArtist", "pfsFirstPublisher", "artistByEaton",	// .art (conflict with asciiArtEditor)
	"trs80Star",			// .pix (conflict with xlPaint)
	"imgScan",				// .raw	(conflict with xlPaint)
	"atariGraphics",		// .mic (conflict with apStar)
	"snx",					// barw22.snx fails to convert with snx but converts to static with recoil, which is wrong, but we just ignore it here for now
	"blazingPaddlesFont"
];

const cpuCount = os.cpus().length;
const testDataFilePath = path.join(testUtil.DATA_DIR_PATH, "process.json");
let testData = null;
const startTime = Date.now();

tiptoe(
	function performValidation()
	{
		validate(this);
	},
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

		// Filter out any unsupported formats as we have a lot of sample files for formats we don't yet support
		sampleFilePaths.filterInPlace(sampleFilePath => !require(path.join(__dirname, "..", "lib", "format", path.basename(path.resolve(sampleFilePath, "..", "..")), `${path.basename(path.dirname(sampleFilePath))}.js`)).meta.unsupported);	// eslint-disable-line sembiance/prefer-relative-require, max-len

		// We shuffle just to better test whether some formats might not reliably work with other formats being converted in parallel
		this.data.sampleFilePaths = sampleFilePaths.shuffle().filter(sampleFilePath => !argv.file || sampleFilePath.endsWith(argv.file));

		if(argv.format)
			this.data.sampleFilePaths.filterInPlace(sfp => path.relative(testUtil.SAMPLE_DIR_PATH, sfp).startsWith(argv.format));
		if(argv.extension)
			this.data.sampleFilePaths.filterInPlace(sfp => (require(path.join(__dirname, "..", "lib", "format", path.basename(path.resolve(sfp, "..", "..")), `${path.basename(path.dirname(sfp))}.js`)).meta.ext || []).includes(argv.extension));	// eslint-disable-line sembiance/prefer-relative-require, max-len

		XU.log`\nTesting ${this.data.sampleFilePaths.length} sample files...`;

		Object.keys(testData).subtractAll(this.data.sampleFilePaths.map(sampleFilePath => path.relative(testUtil.SAMPLE_DIR_PATH, sampleFilePath))).forEach(extraFilePath =>
		{
			if(!extraFilePath.startsWith(argv.format))
				return;
			XU.log`${XU.cf.fg.cyan("[") + XU.c.blink + XU.cf.fg.red("EXTRA") + XU.cf.fg.cyan("]")} file path detected: ${extraFilePath}`;
			if(argv.record)
				delete testData[extraFilePath];
		});

		this.data.sampleFilePaths.parallelForEach((sampleFilePath, subcb) => testSampleFile(sampleFilePath, false, subcb), this, cpuCount);
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
	function outputResults()
	{
		testUtil.logFinish();
		XU.log`\nElapsed time: ${((Date.now()-startTime)/XU.SECOND).secondsAsHumanReadable()}`;
		this();
	},
	XU.FINISH
);

function testParallel(sampleFilePath, cb)
{
	if(argv.verbose)
		XU.log`Testing in parallel: ${sampleFilePath}`;

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
	const diskFamily = path.basename(path.dirname(path.dirname(sampleSubFilePath)));
	const diskFormatid = path.basename(path.dirname(sampleSubFilePath));
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

			dexvert.process(sampleFilePath, outDirPath, {tmpDirPath, verbose : argv.verbose}, this);
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
			if(results.converter && results.converter.program)
				newTestData.converter = results.converter.program;
			if(results.processed && results.output.files)
			{
				newTestData.files = {};
				results.output.files.forEach(outSubFilePath =>
				{
					const outSubFileStats = fs.statSync(path.join(outDirPath, outSubFilePath));
					const outSubFileRecord =
					{
						sum  : hashUtil.hash("sha1", fs.readFileSync(path.join(outDirPath, outSubFilePath))),
						size : outSubFileStats.size
					};
					if(outSubFileStats.mtime.getFullYear()<2020)
						outSubFileRecord.ts = moment(outSubFileStats.mtime).format("YYYY-MM-DD");
					
					newTestData.files[outSubFilePath] = outSubFileRecord;
				});
			}

			if(argv.record)
			{
				testData[sampleSubFilePath] = newTestData;
				return this(undefined, "SKIP", `Skipped because we are recording${!results.processed ? XU.cf.fg.red(" WARNING! processed is FALSE!") : ""}${!results.output.files ? XU.cf.fg.red(" WARNING! No output files detected!") : ""}`);
			}

			if(!testData.hasOwnProperty(sampleSubFilePath))
				return this(undefined, "FAIL", "No test data for this file", `${results.id.family}/${results.id.formatid}`, newTestData);

			const sampleTestData = testData[sampleSubFilePath];

			this.data.results = results;
			if(!!results.processed!=sampleTestData.processed)	// eslint-disable-line eqeqeq
				return this(undefined, "FAIL", `Expected processed to be ${XU.c.fg.white + sampleTestData.processed + XU.c.fg.orange} but got ${XU.c.fg.white + results.processed + XU.c.fg.orange} instead`);

			if(!Object.equals(sampleTestData.inputMeta, results.input.meta))
				return this(undefined, "FAIL", `input.meta does not match expected result: ${diffUtil.diff(sampleTestData.inputMeta, results.input.meta)}`);

			if(sampleTestData.files && !results.output.files)
				return this(undefined, "FAIL", `Expected to have ${XU.c.fg.white + Object.keys(sampleTestData.files).length + XU.c.fg.orange} files but didn't find any`);

			if(!sampleTestData.files && results.output.files)
				return this(undefined, "FAIL", `Expected to have no files but found ${XU.c.fg.white + results.output.files.length + XU.c.fg.orange} instead`);
			
		
			const expectedFiles = sampleTestData.files ? Object.keys(sampleTestData.files) : [];
			if(results.output.files && expectedFiles.length!==results.output.files.length)
				return this(undefined, "FAIL", `Expected ${XU.c.fg.white + expectedFiles.length + XU.c.fg.orange} files, but got ${XU.c.fg.white + results.output.files.length} ${diffUtil.diff(expectedFiles, results.output.files)}`);

			const {family, formatid} = results.id;
			if(results.processed && diskFamily!==family && !FORMATID_MATCH_EXEMPT.includes(diskFormatid))
				return this(undefined, "FAIL", `Disk family ${diskFamily} does not match processed family ${family}`);
			if(results.processed && diskFormatid!==formatid && !FORMATID_MATCH_EXEMPT.includes(diskFormatid))
				return this(undefined, "FAIL", `Disk formatid ${diskFormatid} does not match processed formatid ${formatid}`);

			(results.output.files || []).forEach(outSubFilePath =>
			{
				if(!sampleTestData.files.hasOwnProperty(outSubFilePath))
					return this(undefined, "FAIL", `Unexpected file result: ${XU.c.fg.white + outSubFilePath} (Expected: ${expectedFiles.join(", ")})`);

				const newOutStat = fs.statSync(path.join(outDirPath, outSubFilePath));

				if(!(SIZE_IGNORE_FILES[family] &&
				     (SIZE_IGNORE_FILES[family][formatid] || SIZE_IGNORE_FILES[family]["*"]) &&
				     (SIZE_IGNORE_FILES[family][formatid] || SIZE_IGNORE_FILES[family]["*"]).some(m => dexUtil.flexMatch(outSubFilePath.toLowerCase(), m))))
				{
					if(newOutStat.size!==sampleTestData.files[outSubFilePath].size)
						return this(undefined, "FAIL", `size mistmatch ${newOutStat.size} vs expected ${sampleTestData.files[outSubFilePath].size}`, outSubFilePath);
				}
				
				if(newOutStat.mtime.getFullYear()<2020 && !sampleTestData.files[outSubFilePath].ts)
					return this(undefined, "FAIL", `Output file timestamp is an old date of ${moment(newOutStat.mtime).format("YYYY-MM-DD")} but this was unexpected`, outSubFilePath);

				if(newOutStat.mtime.getFullYear()>=2020 && sampleTestData.files[outSubFilePath].ts)
					return this(undefined, "FAIL", `Output file timestamp is not an old date, but we expected one: ${sampleTestData.files[outSubFilePath].ts}`, outSubFilePath);
				
				if(newOutStat.mtime.getFullYear()<2020 && sampleTestData.files[outSubFilePath].ts && moment(newOutStat.mtime).format("YYYY-MM-DD")!==sampleTestData.files[outSubFilePath].ts)
					return this(undefined, "FAIL", `Output file timestamp does not match. Got ${moment(newOutStat.mtime).format("YYYY-MM-DD")} but expected ${sampleTestData.files[outSubFilePath].ts}`, outSubFilePath);

				if(SHA1_IGNORE_FILES[family] &&
				   (SHA1_IGNORE_FILES[family][formatid] || SHA1_IGNORE_FILES[family]["*"]) &&
				   (SHA1_IGNORE_FILES[family][formatid] || SHA1_IGNORE_FILES[family]["*"]).some(m => dexUtil.flexMatch(outSubFilePath.toLowerCase(), m)))
				{
					expectedFiles.removeOnce(outSubFilePath);
					return;
				}

				if(hashUtil.hash("sha1", fs.readFileSync(path.join(outDirPath, outSubFilePath)))!==sampleTestData.files[outSubFilePath].sum)
					return this(undefined, "FAIL", "SHA1 sum mistmatch", outSubFilePath);

				expectedFiles.removeOnce(outSubFilePath);
			});

			if(sampleTestData.files && expectedFiles.length>0)
				return this(undefined, "FAIL", `The following expected files were not found: ${XU.c.fg.white + expectedFiles.join(", ")}`);

			if(sampleTestData.converter && !newTestData.converter)
				return this(undefined, "FAIL", `Expected converter ${sampleTestData.converter} but did not find one in results.`);

			if(!sampleTestData.converter && newTestData.converter)
				return this(undefined, "FAIL", `Expected no converter but found in results ${newTestData.converter}`);

			if(sampleTestData.converter && newTestData.converter && sampleTestData.converter!==newTestData.converter)
				return this(undefined, "FAIL", `converter ${newTestData.converter} does not match expected ${sampleTestData.converter}`);

			this(undefined, "PASS");
		},
		function cleanup(status, msg="", ...args)
		{
			if(!silent || status!=="PASS")
			{
				const extraArgs = Array.from(args);
				if(status!=="PASS")
				{
					extraArgs.push(outDirPath);

					if(this.data.results)
						fs.writeFileSync(path.join(outDirPath, "dexvert_results.txt"), JSON.stringify(this.data.results), XU.UTF8);
				}
				testUtil.logResult(status, sampleSubFilePath, msg, ...extraArgs);
			}

			this.parallel()(undefined, status==="PASS");
			if(status!=="FAIL" && !argv.keep)
				fileUtil.unlink(outDirPath, this.parallel());
		},
		cb
	);
}
