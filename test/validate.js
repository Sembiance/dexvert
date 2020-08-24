"use strict";

const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "lib", "C.js")),
	{validateValue} = require("@validatem/core"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	dexUtil = require(path.join(__dirname, "..", "lib", "dexUtil.js")),
	either = require("@validatem/either"),
	anything = require("@validatem/anything"),	// eslint-disable-line no-unused-vars
	isLowercase = require("@validatem/is-lowercase"),
	isRegex = require("@validatem/is-regular-expression"),
	isPositive = require("@validatem/is-positive"),
	isNumber = require("@validatem/is-number"),
	hasLengthOf = require("@validatem/has-length-of"),
	hasLengthBetween = require("@validatem/has-length-between"),
	isFunction = require("@validatem/is-function"),
	anyProperty = require("@validatem/any-property"),
	isURL = require("@validatem/is-url"),
	isBoolean = require("@validatem/is-boolean"),
	isNonEmptyString = require("@validatem/is-non-empty-string"),
	arrayOf = require("@validatem/array-of"),
	oneOf = require("@validatem/one-of"),
	required = require("@validatem/required");

exports.validate = function validate(cb)
{
	tiptoe(
		function loadFormatsAndPrograms()
		{
			dexUtil.findFormats(this.parallel());
			fileUtil.glob(path.join(__dirname, "..", "lib", "program"), "**/*.js", {nodir : true}, this.parallel());
		},
		function testFormats(formats, programFilePaths)
		{
			Object.values(formats).flatMap(v => Object.values(v)).forEach(format => validateFormat(format));
			programFilePaths.forEach(programFilePath => validateProgram(require(programFilePath)));		// eslint-disable-line node/global-require

			this();
		},
		cb
	);
};

function validateFormat(format)
{
	const filesizeValues = [];
	if(!format.meta.ext || format.meta.ext.length===1)
		filesizeValues.push(isPositive, arrayOf([isPositive]));
	else
		filesizeValues.push(isPositive, arrayOf([isPositive]), [anyProperty({key : [required, isNonEmptyString, isLowercase], value : [required, either([[isPositive], arrayOf([isPositive])])]})]);

	const filesizeValue = filesizeValues.length===1 ? filesizeValues : [either(filesizeValues)];

	const formatMetaSchema =
	{
		name          : [required, isNonEmptyString],
		website       : [isNonEmptyString, isURL()],
		notes         : [isNonEmptyString],
		mimeType      : [isNonEmptyString],
		encoding      : [isNonEmptyString],
		family        : [isNonEmptyString],
		formatid      : [isNonEmptyString],
		browserNative : [isBoolean],

		bruteUnsafe      : [isBoolean],
		unsupported      : [isBoolean],
		keepFilename     : [isBoolean],
		symlinkUnsafe    : [isBoolean],
		priority         : [isNumber, oneOf(Object.values(C.PRIORITY))],
		confidenceAdjust : [isFunction, hasLengthBetween(0, 2)],
		filesRequired    : [isFunction, hasLengthBetween(0, 2)],
		filesOptional    : [isFunction, hasLengthBetween(0, 2)],

		ext            : [arrayOf([isNonEmptyString, isLowercase]), hasLengthBetween(1, Infinity)],
		forbidExtMatch : [either([[arrayOf([isNonEmptyString]), hasLengthBetween(1, Infinity)], [isBoolean]])],
		safeExt        : [isFunction, hasLengthBetween(0, 1)],

		magic          : [arrayOf(either([[isNonEmptyString], [isRegex]])), hasLengthBetween(1, Infinity)],
		forbiddenMagic : [arrayOf(either([[isNonEmptyString], [isRegex]])), hasLengthBetween(1, Infinity)],
		weakMagic      : [isBoolean],
		trustMagic     : [isBoolean],

		filesize            : filesizeValue,
		forbidFilesizeMatch : [isBoolean],

		filename : [arrayOf(either([[isNonEmptyString], [isRegex]])), hasLengthBetween(1, Infinity)]
	};

	const formatSchema =
	{
		meta : [required, formatMetaSchema],

		idCheck : [isFunction, hasLengthBetween(0, 1)],

		converterPriorty : [arrayOf([required, isNonEmptyString]), hasLengthBetween(1, Infinity)],
		converterExclude : [arrayOf([required, isNonEmptyString]), hasLengthBetween(1, Infinity)],

		inputMeta       : [isFunction, hasLengthOf(3)],
		preSteps        : [arrayOf([required, isFunction, hasLengthBetween(0, 2)])],
		steps           : [arrayOf([required, isFunction])],
		postSteps       : [arrayOf([required, isFunction, hasLengthBetween(0, 2)])],
		post            : [isFunction, hasLengthOf(3)],
		updateProcessed : [isFunction, hasLengthOf(3)]
	};

	try
	{
		validateValue(format, formatSchema);
	}
	catch(err)
	{
		XU.log`Failed to validate format.\n${err}`;
		process.exit(1);
	}
}

function validateProgram(program)
{
	const programMetaSchema =
	{
		website        : [required, either([[isNonEmptyString, isURL()], [arrayOf([isNonEmptyString, isURL()])]])],
		notes          : [isNonEmptyString],

		informational  : [isBoolean],
		bruteUnsafe    : [isBoolean],

		gentooOverlay  : [isNonEmptyString],
		gentooPackage  : [either([[isNonEmptyString], [arrayOf([isNonEmptyString])]])],
		gentooUseFlags : [isNonEmptyString]
	};

	if(Array.isArray(program.meta.gentooPackage))
		programMetaSchema.bin = [arrayOf([isNonEmptyString])];

	const programSchema =
	{
		meta       : [required, programMetaSchema],
		bin        : [required, isFunction, hasLengthBetween(0, 2)],
		args       : [required, isFunction, hasLengthOf(2)],	// Technically it's 4, but args with defaults don't count in .length
		cwd        : [isFunction, hasLengthBetween(0, 2)],
		pre        : [isFunction, hasLengthOf(3)],
		post       : [isFunction, hasLengthOf(3)],
		runOptions : [isFunction, hasLengthBetween(0, 2)]
	};

	// Format specific properties that are shared for easier re-use
	["STRIP_ARGS"].forEach(v => { programSchema[v] = [anything]; });

	try
	{
		validateValue(program, programSchema);
	}
	catch(err)
	{
		XU.log`Failed to validate program ${program}.\n${err}`;
		process.exit(1);
	}
}
