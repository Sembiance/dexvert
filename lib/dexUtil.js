"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	httpUtil = require("@sembiance/xutil").http,
	path = require("path"),
	ioctl = require("ioctl"),
	fs = require("fs"),
	assert = require("assert"),
	C = require("./C.js"),
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

	const loopDev = fs.openSync(`/dev/loop${loopNum}`);
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
	const loopDev = fs.openSync(`/dev/loop${loopNum}`);
	assert.strictEqual(ioctl(loopDev, LOOP.CLR_FD), 0, `Failed to clear loop ${loopNum}`);
	fs.closeSync(loopDev);
};

exports.waitForLock = function waitForLock(lockid, cb)
{
	tiptoe(
		function getLock()
		{
			httpUtil.get(`http://127.0.0.1:${C.DEXSERV_PORT}/lock?lockid=${lockid}`, this);
		},
		function rescheduleIfNeeded(err, resultRaw)
		{
			if(err)
				XU.log`dexUtil.waitForLock error: ${err}`;

			if(JSON.parse(resultRaw).status==="busy")
				setTimeout(() => exports.waitForLock(lockid, cb), C.LOCK_CHECK_INTERVAL);
			else
				setImmediate(cb);
		}
	);
};

exports.releaseLock = function releaseLock(lockid, cb)
{
	httpUtil.get(`http://127.0.0.1:${C.DEXSERV_PORT}/unlock?lockid=${lockid}`, cb);
};
