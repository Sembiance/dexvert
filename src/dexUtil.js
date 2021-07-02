"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	path = require("path"),
	C = require("./C.js"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

// Matches the given value against the matcher. If 'matcher' is a string, then value just needs to start with matcher, unless fullStringMatch is set then the entire string must be a case insensitive match. If 'matcher' is a regexp, it must regex match value.
exports.flexMatch = function flexMatch(value, matcher, fullStringMatch)
{
	return ((typeof matcher==="string" && (fullStringMatch ? (value.toLowerCase()===matcher.toLowerCase()) : value.toLowerCase().startsWith(matcher.toLowerCase()))) || (matcher instanceof RegExp && value.match(matcher)));
};

// Will find every format for every family and return them
exports.findFormats = function findFormats(cb)
{
	tiptoe(
		function findFormatFiles()
		{
			C.FAMILIES.parallelForEach((FAMILY, subcb) => fileUtil.glob(path.join(C.FORMAT_DIR_PATH, FAMILY), "*.js", {nodir : true}, subcb), this);
		},
		function loadFormats(familyFormatPaths)
		{
			const formats = C.FAMILIES.reduce((r, FAMILY) => { r[FAMILY] = {}; return r; }, {});

			C.FAMILIES.forEach((FAMILY, i) =>
			{
				familyFormatPaths[i].forEach(familyFormatPath =>
				{
					const format = require(familyFormatPath);
					format.meta.formatid = path.basename(familyFormatPath, ".js");
					format.meta.family = FAMILY;

					formats[FAMILY][format.meta.formatid] = format;
				});
			});

			Object.forEach(require(path.join(C.FORMAT_DIR_PATH, "unsupported.js")).formats, (family, unsupportedFormats) =>
			{
				Object.forEach(unsupportedFormats, (formatid, format) =>
				{
					formats[family][formatid] = {meta : {...format, unsupported : true}};
					if(format.idCheck)
					{
						formats[family][formatid].idCheck = format.idCheck;
						delete formats[family][formatid].meta.idCheck;
					}
				});
			});

			return formats;
		},
		cb
	);
};

// Sets the state.output object according to the passed in outputDirPath
exports.setStateInput = function setStateInput(state, inputFilePath)
{
	state.input = { absolute : path.resolve(inputFilePath), meta : {}, filePath : path.resolve(inputFilePath), ...path.parse(inputFilePath)};
};

// Sets the state.output object according to the passed in outputDirPath
exports.setStateOutput = function setStateOutput(state, outputDirPath)
{
	state.output = { absolute : path.resolve(outputDirPath), dirPath : path.resolve(outputDirPath), ...path.parse(outputDirPath)};
};

// Will run an external dexvert process against inFilePath, treating it asFormat
exports.dexvertAs = function dexvertAs(state, inFilePath, outDirPath, asFormat, cb)
{
	const outputJSONFilePath = fileUtil.generateTempFilePath(undefined, ".json");
	tiptoe(
		function runDexvert()
		{
			const dexArgs = ["--verbose", state.verbose.toString(), "--outputStateToFile", outputJSONFilePath];
			if(asFormat)
				dexArgs.push("--asFormat", asFormat);
			dexArgs.push(inFilePath, outDirPath);

			runUtil.run(path.join(__dirname, "..", "bin", "dexvert"), dexArgs, {silent : true, liveOutput : true}, this);
		},
		function loadResults()
		{
			fs.readFile(outputJSONFilePath, XU.UTF8, this);
		},
		function parseJSON(resultRaw)
		{
			this.parallel()(undefined, XU.parseJSON(resultRaw, null));
			fileUtil.unlink(outputJSONFilePath, this.parallel());
		},
		cb
	);
};
