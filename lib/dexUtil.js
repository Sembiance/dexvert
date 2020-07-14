"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	ioctl = require("ioctl"),
	fs = require("fs"),
	assert = require("assert"),
	C = require(path.join(__dirname, "C.js")),
	tiptoe = require("tiptoe");

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
					const formatid = path.basename(familyFormatPath, ".js");
					const format = require(familyFormatPath);

					// Validate that the handler meta is correctly formed
					const meta = format.meta;
					meta.formatid = formatid;
					meta.family = FAMILY;

					if((meta.ext || []).some(ext => ext.match(/[A-Z]/)))
						process.exit(XU.log`Handler ${FAMILY}/${formatid} has an ext that is not lowercase!`);

					if(!meta.hasOwnProperty("name"))
						process.exit(XU.log`Handler ${FAMILY}/${formatid} does not have a name!`);
					
					
					formats[FAMILY][formatid] = format;
				});
			});

			Object.forEach(require(path.join(C.FORMAT_DIR_PATH, "unsupported.js")).formats, (family, unsupportedFormats) =>
			{
				Object.forEach(unsupportedFormats, (formatid, format) =>
				{
					formats[family][formatid] = {meta : {...format, unsupported : true}};
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

/* eslint-disable unicorn/no-unused-properties */
const LOOP =
{
	CTL_ADD      : 0x4C80,
	CTL_REMOVE   : 0x4C81,
	CTL_GET_FREE : 0x4C82,
	SET_FD       : 0x4C00,
	CLR_FD       : 0x4C01
};
/* eslint-enable unicorn/no-unused-properties */

// Will find an open loop device num and filePath to it
exports.allocateLoopDev = function allocateLoopDev(filePath, tries=1024)
{
	const loopControl = fs.openSync("/dev/loop-control", "r+");
	const loopNum = ioctl(loopControl, LOOP.CTL_GET_FREE);
	fs.closeSync(loopControl);

	const loopDev = fs.openSync("/dev/loop" + loopNum);
	const fd = fs.openSync(filePath, "r");

	try
	{
		assert.strictEqual(ioctl(loopDev, LOOP.SET_FD, fd), 0, `Assigning fs to loop ${loopNum} failed for ${filePath}`);
		fs.closeSync(loopDev);
		fs.closeSync(fd);
	}
	catch(err)
	{
		fs.closeSync(loopDev);
		fs.closeSync(fd);
		
		if((tries-1)===0)
			throw err;

		return allocateLoopDev(filePath, tries-1);
	}

	return loopNum;
};

// Will free the passed in loopNum
exports.freeLoopDev = function freeLoopDev(loopNum)
{
	const loopDev = fs.openSync("/dev/loop" + loopNum);
	assert.strictEqual(ioctl(loopDev, LOOP.CLR_FD), 0, `Failed to clear loop ${loopNum}`);
	fs.closeSync(loopDev);
};
