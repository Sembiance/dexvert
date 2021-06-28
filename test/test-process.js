"use strict";
/* eslint-disable node/global-require, prefer-named-capture-group */
const XU = require("@sembiance/xu"),
	path = require("path"),
	testUtil = require("./testUtil.js"),
	fileUtil = require("@sembiance/xutil").file,
	moment = require("moment"),
	printUtil = require("@sembiance/xutil").print,
	hashUtil = require("@sembiance/xutil").hash,
	diffUtil = require("@sembiance/xutil").diff,
	runUtil = require("@sembiance/xutil").run,
	{validate} = require("./validate.js"),
	dexUtil = require("../src/dexUtil.js"),
	{Command} = require("commander"),
	fs = require("fs"),
	os = require("os"),
	tiptoe = require("tiptoe");

const argv = new Command().description("Will test all sample files to ensure dexvert.process() works correctly.").
	option("--format [format]", "Can pass a specific format to limit testing to that format, example: archive/zip").
	option("--extension [ext]", "Only test files that belong to formats that have the given extension").
	option("--file [subFilePath]", "Only identify the given sample subFilePath").
	option("--verbose [level]", "Show additional info when processing. Levels 1 to 6 where 6 is most verbose").
	option("--full", "Run ALL tests, even long running ones").
	option("--keep", "Keep temporary directories around after converting").
	option("--record", "Take the results of the identifications and save them as the future expected results").
	parse(process.argv);

// Can specificy family : { formatid : ["subPath/file.png", /.txt$/]} to ignore the file subpath when doing SHA1 checking
// Filenames are the OUTPUT filenames and are all converted to LOWERCASE first
const SHA1_IGNORE_FILES =
{
	archive :
	{
		// Not sure why, but the director extraction program produces different PNG files each time
		director : [/.png$/],

		// unADF always makes this a little different each time, not sure why. Once I add GoADF amiga support, I can remove this line
		adfOFS : [/iff saxophone.instr$/]
	},
	document :
	{
		// PDF's have unique ID's within them and also creation dates, etc which cause them to never SHA1 match the same
		"*" : [/.pdf$/]
	},
	font :
	{
		// Generated .otf files from fontforge and differ. Probably meta info or something. Didn't investigate further
		"adobeType1" : [/.otf$/],
		"sfd"        : [/.otf$/],
		"woff"       : [/.otf$/]
	},
	image :
	{
		// Inkscape/uniconvertor doesn't always produce the same exact SVG file, even with the same args and inputs.
		"cgm" : [/.svg$/],
		"cvg" : [/.svg$/],
		"eps" : [/.svg$/],
		"fig" : [/.svg$/],
		 "ps" : [/.svg$/],
		"wmf" : [/.svg$/],

		// lottie2gif doesn't produce identical GIF files for these files:
		"lottie" : [/cooking.json.gif$/, /tile_grid_loading_animation.json.gif$/, /fingerprint_success.json.gif$/, /starts_transparent.json.gif$/, /tractor.json.gif$/],

		// Abydos doesn't always produce the same files, not sure why
		"amosSprites" : [/.webp$/],
		"p64"         : [/m019.png$/],

		// Abydos doesn't work with this image yet, produces different data each time
		"sgx" : [/nuke.png$/],

		// Deark produces slightly different GIF files each time, not sure why
		"ani" : [/.gif$/]
	}
};

// Filenames are the OUTPUT filenames and are all converted to LOWERCASE first
const SIZE_IGNORE_FILES =
{
	document :
	{
		// PDF's have unique ID's within them and also creation dates, etc which cause them to never SHA1 match the same
		"*" : [/.pdf$/]
	},
	image :
	{
		// Abydos sometimes fails to produce the proper webp output
		"amosSprites" : [/.webp$/],

		// soffice can produce wildly different SVG output, not sure why
		"cgm" : [/.svg$/]
	}
};

// Several output files will vary every so slightly due to screenshot artifacts or FFMPEG changing slightly how it encodes a video on version upgrades
const DEFAULT_SIZE_FLEX_VIDEO = 7;	// Video often changes, but usually not more than this
const SIZE_FLEX_PERCENTAGE =
{
	audio :
	{
		// The produced mp3 files from timidity are different each time
		"soundFont2" : 10
	},
	image :
	{
		// Program has a flashing cursor that is different each time
		"3dCK" : 1,

		// pfstools will produce an ever so slightly different PNG
		"radiance" : 0.1,

		// Darktable results produces just ever so slightly different PNG files each time
		"crw"          : 0.1,
		"cr2"          : 0.1,
		"arw"          : 0.1,
		"dng"          : 0.1,
		"erf"          : 0.1,
		"kodakDCR"     : 0.1,
		"kodakKDC"     : 0.1,
		"mrw"          : 0.1,
		"nikon"        : 0.1,
		"orf"          : 0.1,
		"panasonicRaw" : 0.1,
		"pentaxRaw"    : 0.1,
		"raf"          : 0.1
	},
	font :
	{
		// PNG preview (generated from an SVG file) is slightly different when inkscape updates
		"otf" : 1,
		"ttf" : 1
	},
	music :
	{
		// Not entirely sure why, but _¡tsa!_juanidance.med is always different
		med : 2,
		
		// The files generated from the WAVs from sidplay2 are different each time. Probably due to the analog nature of the SID chip
		sid : 10
	},
	video :
	{
		// These are screen recordings from DOSBox and get converted to MP4 with ffmpeg, thus they can differ each time
		"disneyCFAST" : DEFAULT_SIZE_FLEX_VIDEO,
		"fantavision" : DEFAULT_SIZE_FLEX_VIDEO,
		"grasp"       : 25,
	
		// These are linux virtualX screen recordings and can differ each time
		"movieSetter" : DEFAULT_SIZE_FLEX_VIDEO,

		// ffmpeg version upgrades produce slightly different output and ffmpeg on different architectures too, odd.
		"avi"                : DEFAULT_SIZE_FLEX_VIDEO,
		"cdxl"               : DEFAULT_SIZE_FLEX_VIDEO,
		"cyberPaintSeq"      : DEFAULT_SIZE_FLEX_VIDEO,
		"dl"                 : DEFAULT_SIZE_FLEX_VIDEO,
		"flc"                : DEFAULT_SIZE_FLEX_VIDEO,
		"fli"                : DEFAULT_SIZE_FLEX_VIDEO,
		"flm"                : DEFAULT_SIZE_FLEX_VIDEO,
		"iffANIM"            : DEFAULT_SIZE_FLEX_VIDEO,
		"mov"                : DEFAULT_SIZE_FLEX_VIDEO,
		"mpeg1"              : DEFAULT_SIZE_FLEX_VIDEO,
		"mpeg2"              : DEFAULT_SIZE_FLEX_VIDEO,
		"neochromeAnimation" : DEFAULT_SIZE_FLEX_VIDEO,
		"smacker"            : DEFAULT_SIZE_FLEX_VIDEO
	}
};

// Usually the formatid of the directory should match what is detected by dexid
// Sadly, some formats are only identified by an extension that is shared by multiple formats (such as image/pfsFirstPublisher and image/gfaArtist and image/asciiArtEditor)
// So add them here to exempt from failing the test due to this
const FORMATID_MATCH_IGNORE_FILES =
{
	image :
	{
		// ext conflicts
		"apStar"         : [/atarigraphics\/inny2\.mic$/],
		"xlPaint"        : [/trs80star\/girl1\.max$/],
		"asciiArtEditor" : [/(gfaartist|artistbyeaton)\/.+\.art$/],
		"artDirector"    : [/pfsfirstpublisher\/.+\.art$/]
	},
	text :
	{
		// .cue files have to live alongside ISO/CDI files
		"cue" : [/archive\/(iso|cdi)\/.+\.cue$/],
		"toc" : [/archive\/(iso|cdi)\/.+\.toc$/],

		// allprims.cgm isn't supported yet, so it fallsback to text/txt
		"txt" : [/image\/cgm\/allprims\.cgm$/]
	}
};

const IGNORE_EXTRA_FILES = {};

const IGNORE_META_DIFFERENCES =
{
	executable :
	{
		"windowsSCR" : [/kaleid95.scr$/]
	}
};

const PROGRAM_FLAGS_FILES =
{
	"archive/iso/launch.bin" : ["bchunk:bchunkSwapByteOrder:true"]
};

// We will front load these files at the start so they don't slow down the whole process by being one of the last files randomly chosen to be processed
const SLOW_FILES = ["image/kodakDCR/RAW_KODAK_DCSPRO.DCR", "image/radiance/forest_path.hdr", "image/tundra/tcf-shocktronics.tnd", "image/heic/sample1.heif", "image/cgm/corvette.cgm", ".GL", ".gl"];

const SLOW_DURATION = XU.MINUTE*3;

const fileDurations = {};
const cpuCount = os.cpus().length;
const testDataFilePath = path.join(testUtil.DATA_DIR_PATH, "process.json");
let testData = null;
let startTime = null;

tiptoe(
	function performValidation()
	{
		testUtil.initSamples(this.parallel());
		validate(this.parallel());
	},
	function findSampleFiles()
	{
		startTime = Date.now();

		printUtil.majorHeader("Process Test", {prefix : "\n"});
		XU.log`Loading test data and finding sample files...`;

		fs.readFile(testDataFilePath, XU.UTF8, this.parallel());
		testUtil.findSupportedSampleFilePaths(this.parallel());
	},
	function testSampleFiles(_testData, sampleFilePaths)
	{
		testData = JSON.parse(_testData);

		// First ensure we have a format.js for this format, otherwise it's not supported and we shouldn't bother
		sampleFilePaths.filterInPlace(sampleFilePath => fileUtil.existsSync(path.join(__dirname, "..", "src", "format", path.basename(path.resolve(sampleFilePath, "..", "..")), `${path.basename(path.dirname(sampleFilePath))}.js`)));

		// Filter out any unsupported formats as we have a lot of sample files for formats we don't yet support
		sampleFilePaths.filterInPlace(sampleFilePath => !require(path.join(__dirname, "..", "src", "format", path.basename(path.resolve(sampleFilePath, "..", "..")), `${path.basename(path.dirname(sampleFilePath))}.js`)).meta.unsupported);	// eslint-disable-line sembiance/prefer-relative-require

		// We shuffle just to better test whether some formats might not reliably work with other formats being converted in parallel
		this.data.sampleFilePaths = sampleFilePaths.shuffle().filter(sampleFilePath => !argv.file || sampleFilePath.endsWith(argv.file)).multiSort([v => SLOW_FILES.some(SLOW_FILE => v.endsWith(SLOW_FILE))], true);

		if(argv.format)
			this.data.sampleFilePaths.filterInPlace(sfp => path.relative(testUtil.SAMPLE_DIR_PATH, sfp).startsWith(path.join(argv.format, "/")));
		if(argv.extension)
			this.data.sampleFilePaths.filterInPlace(sfp => (require(path.join(__dirname, "..", "src", "format", path.basename(path.resolve(sfp, "..", "..")), `${path.basename(path.dirname(sfp))}.js`)).meta.ext || []).includes(argv.extension));	// eslint-disable-line sembiance/prefer-relative-require

		XU.log`\nTesting ${this.data.sampleFilePaths.length} sample files...`;

		Object.keys(testData).subtractAll(this.data.sampleFilePaths.map(sampleFilePath => path.relative(testUtil.SAMPLE_DIR_PATH, sampleFilePath))).forEach(extraFilePath =>
		{
			if((argv.format && !extraFilePath.startsWith(path.join(argv.format, "/"))) || argv.file)
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

		if(Object.keys(fileDurations).length>0)
		{
			XU.log`\nSlowest files: ${Object.entries(fileDurations).multiSort([([, d]) => d], true).slice(0, 15).map(([p, d]) =>
			{
				if(SLOW_FILES.some(SLOW_FILE => p.endsWith(SLOW_FILE)))
					return null;

				return `\t${XU.cf.fg.white(p)}: ${XU.cf.fg.cyan((d/XU.SECOND).secondsAsHumanReadable({short : true, maxParts : 2}))}`;
			}).filterEmpty().join("\n")}`;
		}

		XU.log`\nTotal elapsed duration: ${((Date.now()-startTime)/XU.SECOND).secondsAsHumanReadable()}`;
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
	const outDirPath = fileUtil.generateTempFilePath(undefined, "test-process");
	const resultsJSONFilePath = fileUtil.generateTempFilePath(undefined, ".json");

	tiptoe(
		function createOutDir()
		{
			fs.mkdir(outDirPath, {recursive : true}, this);
		},
		function performProcess()
		{
			const dexvertArgs = [];

			Object.forEach(PROGRAM_FLAGS_FILES, (targetPath, programFlags) =>
			{
				if(sampleSubFilePath.toLowerCase().endsWith(targetPath))
					dexvertArgs.push(...programFlags.flatMap(programFlag => (["--programFlag", programFlag])));
			});

			runUtil.run("dexvert", [...dexvertArgs, "--outputStateToFile", resultsJSONFilePath, sampleFilePath, outDirPath], runUtil.SILENT, this);
		},
		function loadResultsFile(dexvertOutputRaw)
		{
			if(!fileUtil.existsSync(resultsJSONFilePath))
			{
				fs.writeFileSync(path.join(outDirPath, "dexvertOutput.txt"), dexvertOutputRaw, XU.UTF8);
				return this.jump(2, undefined, "FAIL", `Failed to find dexvert JSON output file for: ${sampleFilePath} see dexvertOutput.txt in: `);
			}
				
			fs.readFile(resultsJSONFilePath, XU.UTF8, this);
		},
		function validateResults(resultsRaw)
		{
			const results = XU.parseJSON(resultsRaw);

			if(results.elapsedMS>SLOW_DURATION)
				fileDurations[sampleSubFilePath] = results.elapsedMS;

			const newTestData = {processed : !!results.processed};
			if(results.unsupported)
				newTestData.unsupported = true;
			if(results.input.meta)
				newTestData.inputMeta = results.input.meta;
			if(results.converter?.program)
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
				return this(undefined, "FAIL", `No test data for this file: ${sampleSubFilePath}`, `${results.id ? `${results.id.family}/${results.id.formatid}` : ""}`, newTestData);

			const sampleTestData = testData[sampleSubFilePath];

			this.data.results = results;
			if(!!results.processed!=sampleTestData.processed)	// eslint-disable-line eqeqeq
				return this(undefined, "FAIL", `Expected processed to be ${XU.c.fg.white + sampleTestData.processed + XU.c.fg.orange} but got ${XU.c.fg.white + results.processed + XU.c.fg.orange} instead`);

			const {family, formatid} = results.id || results.identify.find(id => id.from==="dexvert") || {};

			const allowMetaDifferences = IGNORE_META_DIFFERENCES[family] &&
			   (IGNORE_META_DIFFERENCES[family][formatid] || IGNORE_META_DIFFERENCES[family]["*"]) &&
			   (IGNORE_META_DIFFERENCES[family][formatid] || IGNORE_META_DIFFERENCES[family]["*"]).some(m => dexUtil.flexMatch(sampleSubFilePath.toLowerCase(), m));

			if(!allowMetaDifferences && !Object.equals(sampleTestData.inputMeta, results.input.meta))
				return this(undefined, "FAIL", `input.meta does not match expected result: ${diffUtil.diff(sampleTestData.inputMeta, results.input.meta)}`);

			if(sampleTestData.files && !results.output.files)
				return this(undefined, "FAIL", `Expected to have ${XU.c.fg.white + Object.keys(sampleTestData.files).length + XU.c.fg.orange} files but didn't find any`);

			if(!sampleTestData.files && results.output.files)
				return this(undefined, "FAIL", `Expected to have no files but found ${XU.c.fg.white + results.output.files.length + XU.c.fg.orange} instead`);

			const allowExtraFiles = IGNORE_EXTRA_FILES[family] &&
			   (IGNORE_EXTRA_FILES[family][formatid] || IGNORE_EXTRA_FILES[family]["*"]) &&
			   (IGNORE_EXTRA_FILES[family][formatid] || IGNORE_EXTRA_FILES[family]["*"]).some(m => dexUtil.flexMatch(sampleSubFilePath.toLowerCase(), m));

			const expectedFiles = sampleTestData.files ? Object.keys(sampleTestData.files) : [];
			if(results.output.files && expectedFiles.length!==results.output.files.length && !allowExtraFiles)
				return this(undefined, "FAIL", `Expected ${XU.c.fg.white + expectedFiles.length + XU.c.fg.orange} files, but got ${XU.c.fg.white + results.output.files.length} ${diffUtil.diff(expectedFiles, results.output.files)}`);

			if(!(FORMATID_MATCH_IGNORE_FILES[family] &&
				(FORMATID_MATCH_IGNORE_FILES[family][formatid] || FORMATID_MATCH_IGNORE_FILES[family]["*"]) &&
				(FORMATID_MATCH_IGNORE_FILES[family][formatid] || FORMATID_MATCH_IGNORE_FILES[family]["*"]).some(m => dexUtil.flexMatch(sampleSubFilePath.toLowerCase(), m))))
			{
				if(results.processed && diskFamily!==family)
					return this(undefined, "FAIL", `Disk FAMILY ${diskFamily}/${diskFormatid} does not match processed FAMILY ${family}/${formatid}`);
				if(results.processed && diskFormatid!==formatid)
					return this(undefined, "FAIL", `Disk FORMATID ${diskFamily}/${diskFormatid} does not match processed FORMATID ${family}/${formatid}`);
			}

			(results.output.files || []).forEach(outSubFilePath =>
			{
				if(!sampleTestData.files.hasOwnProperty(outSubFilePath))
				{
					if(allowExtraFiles)
						return;
						
					return this(undefined, "FAIL", `Unexpected file result: ${XU.c.fg.white + outSubFilePath} (Expected: ${expectedFiles.join(", ")})`);
				}

				const newOutStat = fs.statSync(path.join(outDirPath, outSubFilePath));
				let ignoreSHA1 = SHA1_IGNORE_FILES[family] && (SHA1_IGNORE_FILES[family][formatid] || SHA1_IGNORE_FILES[family]["*"]) && (SHA1_IGNORE_FILES[family][formatid] || SHA1_IGNORE_FILES[family]["*"]).some(m => dexUtil.flexMatch(outSubFilePath.toLowerCase(), m));

				if(!(SIZE_IGNORE_FILES[family] &&
				     (SIZE_IGNORE_FILES[family][formatid] || SIZE_IGNORE_FILES[family]["*"]) &&
				     (SIZE_IGNORE_FILES[family][formatid] || SIZE_IGNORE_FILES[family]["*"]).some(m => dexUtil.flexMatch(outSubFilePath.toLowerCase(), m))))
				{
					const sizeDiffPercent = 100*(1-((sampleTestData.files[outSubFilePath].size-Math.abs(newOutStat.size-sampleTestData.files[outSubFilePath].size))/sampleTestData.files[outSubFilePath].size));
					const allowedSizeDiffPercent = SIZE_FLEX_PERCENTAGE[family]?.[formatid] || 0;
					if(allowedSizeDiffPercent>0)
						ignoreSHA1 = true;
					if(sizeDiffPercent>allowedSizeDiffPercent)
						return this(undefined, "FAIL", `size mistmatch ${newOutStat.size} vs expected ${sampleTestData.files[outSubFilePath].size} a ${sizeDiffPercent.toFixed(5)}% vs allowed ${allowedSizeDiffPercent}%`, outSubFilePath);
				}

				if(newOutStat.mtime.getFullYear()<2020 && !sampleTestData.files[outSubFilePath].ts)
					return this(undefined, "FAIL", `Output file timestamp is an old date of ${moment(newOutStat.mtime).format("YYYY-MM-DD")} but this was unexpected`, outSubFilePath);

				if(newOutStat.mtime.getFullYear()>=2020 && sampleTestData.files[outSubFilePath].ts)
					return this(undefined, "FAIL", `Output file timestamp is not an old date, but we expected one: ${sampleTestData.files[outSubFilePath].ts}`, outSubFilePath);
				
				if(newOutStat.mtime.getFullYear()<2020 && sampleTestData.files[outSubFilePath].ts && moment(newOutStat.mtime).format("YYYY-MM-DD")!==sampleTestData.files[outSubFilePath].ts)
					return this(undefined, "FAIL", `Output file timestamp does not match. Got ${moment(newOutStat.mtime).format("YYYY-MM-DD")} but expected ${sampleTestData.files[outSubFilePath].ts}`, outSubFilePath);

				if(ignoreSHA1)
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
					extraArgs.push(os.hostname()==="chatsubo" ? outDirPath.replaceAll("/mnt/", "/mnt/chatsubo/") : outDirPath);

					if(this.data.results)
						fs.writeFileSync(path.join(outDirPath, "___dexvert_results.txt"), JSON.stringify(this.data.results), XU.UTF8);
				}
				testUtil.logResult(status, sampleSubFilePath, msg, ...extraArgs);
			}

			this.parallel()(undefined, status==="PASS");
			if(status!=="FAIL" && !argv.keep)
				fileUtil.unlink(outDirPath, this.parallel());
			
			fileUtil.unlink(resultsJSONFilePath, this.parallel());
		},
		cb
	);
}
