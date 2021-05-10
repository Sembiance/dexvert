"use strict";

const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require("../src/C.js"),
	assert = require("assert"),
	{validateValue} = require("@validatem/core"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	dexUtil = require("../src/dexUtil.js"),
	either = require("@validatem/either"),
	anything = require("@validatem/anything"),
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
	isPlainObject = require("@validatem/is-plain-object"),
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
			fileUtil.glob(path.join(__dirname, "..", "src", "program"), "**/*.js", {nodir : true}, this.parallel());
		},
		function testFormats(formats, programFilePaths)
		{
			const formatids = Object.values(formats).flatMap(v => Object.keys(v));
			const dupliacteFormatids = formatids.subtractOnce(formatids.unique());
			assert.strictEqual(dupliacteFormatids.length, 0, `Duplicate formatids detected: ${dupliacteFormatids}`);

			Object.values(formats).flatMap(v => Object.values(v)).forEach(format => validateFormat(format));
			programFilePaths.forEach(programFilePath => validateProgram(require(programFilePath)));		// eslint-disable-line node/global-require

			this();
		},
		cb
	);
};

function validateFormat(format)
{
	const fileSizeValues = [];
	if(!format.meta.ext || format.meta.ext.length===1)
		fileSizeValues.push(isPositive, arrayOf([isPositive]));
	else
		fileSizeValues.push(isPositive, arrayOf([isPositive]), [anyProperty({key : [required, isNonEmptyString, isLowercase], value : [required, either([[isPositive], arrayOf([isPositive])])]})]);

	const fileSizeValue = fileSizeValues.length===1 ? fileSizeValues : [either(fileSizeValues)];

	const formatMetaSchema =
	{
		name     : [required, isNonEmptyString],
		website  : [isNonEmptyString, isURL()],
		notes    : [isNonEmptyString],
		mimeType : [isNonEmptyString],
		encoding : [isNonEmptyString],
		family   : [isNonEmptyString],
		formatid : [isNonEmptyString],
		hljsLang : [isNonEmptyString],

		unsafe      : [isBoolean],
		unsupported      : [isBoolean],
		highConfidence   : [isBoolean],
		keepFilename     : [isBoolean],
		symlinkUnsafe    : [isBoolean],
		untouched        : [isBoolean],
		fallback         : [isBoolean],
		priority         : [isNumber, oneOf(Object.values(C.PRIORITY))],
		confidenceAdjust : [isFunction, hasLengthBetween(0, 3)],
		filesRequired    : [isFunction, hasLengthBetween(0, 3)],
		filesOptional    : [isFunction, hasLengthBetween(0, 3)],

		ext            : [arrayOf([isNonEmptyString, isLowercase]), hasLengthBetween(1, Infinity)],
		forbiddenExt   : [arrayOf(either([[isNonEmptyString], [isRegex]])), hasLengthBetween(1, Infinity)],
		forbidExtMatch : [either([[arrayOf([isNonEmptyString]), hasLengthBetween(1, Infinity)], [isBoolean]])],
		safeExt        : [isFunction, hasLengthBetween(0, 1)],

		magic          : [arrayOf(either([[isNonEmptyString], [isRegex]])), hasLengthBetween(1, Infinity)],
		forbiddenMagic : [arrayOf(either([[isNonEmptyString], [isRegex]])), hasLengthBetween(1, Infinity)],
		weakMagic      : [isBoolean],
		trustMagic     : [isBoolean],

		fileSize            : fileSizeValue,
		forbidFileSizeMatch : [isBoolean],

		filename : [arrayOf(either([[isNonEmptyString], [isRegex]])), hasLengthBetween(1, Infinity)]
	};

	const formatSchema =
	{
		meta : [required, formatMetaSchema],

		idCheck : [isFunction, hasLengthBetween(0, 2)],

		converterPriorty : [either([arrayOf(either([[required, isNonEmptyString], [{program : [required, isNonEmptyString], flags : [isPlainObject]}]])), hasLengthBetween(1, Infinity), [isFunction, hasLengthBetween(0, 2)]])],
		converterExclude : [arrayOf([required, isNonEmptyString]), hasLengthBetween(1, Infinity)],

		inputMeta       : [isFunction, hasLengthOf(3)],
		preSteps        : [arrayOf([required, isFunction, hasLengthBetween(0, 2)])],
		steps           : [arrayOf([required, isFunction])],
		postSteps       : [arrayOf([required, isFunction, hasLengthBetween(0, 2)])],
		post            : [isFunction, hasLengthOf(3)],
		updateProcessed : [isFunction, hasLengthOf(3)]
	};

	// Format specific properties that are shared for easier re-use
	["HFS_MAGICS"].forEach(v => { formatSchema[v] = [anything]; });

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
		website : [required, either([[isNonEmptyString, isURL()], [arrayOf([isNonEmptyString, isURL()])]])],
		notes   : [isNonEmptyString],

		informational : [isBoolean],
		unsafe        : [isBoolean],
		slow          : [isBoolean],

		gentooOverlay  : [either([[isNonEmptyString], [arrayOf([isNonEmptyString])]])],
		gentooPackage  : [either([[isNonEmptyString], [arrayOf([isNonEmptyString])]])],
		gentooUseFlags : [isNonEmptyString]
	};

	if(Array.isArray(program.meta.gentooPackage))
		programMetaSchema.bin = [arrayOf([isNonEmptyString])];

	const programSchema =
	{
		meta       : [required, programMetaSchema],
		bin        : [isFunction, hasLengthBetween(0, 2)],
		steps      : [isFunction, hasLengthBetween(0, 3)],
		preArgs    : [isFunction, hasLengthOf(4)],
		args       : [required, isFunction, hasLengthOf(3)], 	// Technically it's 5+, but args with defaults don't count in .length
		cwd        : [isFunction, hasLengthBetween(0, 3)],
		pre        : [isFunction, hasLengthOf(4)],
		post       : [isFunction, hasLengthOf(4)],
		runOptions : [isFunction, hasLengthBetween(0, 3)],
		qemu       : [isFunction, hasLengthBetween(0, 2)],
		qemuData   : [isFunction, hasLengthBetween(0, 3)],
		dos        : [isFunction, hasLengthBetween(0, 2)],
		dosData    : [isFunction, hasLengthBetween(0, 3)]
	};

	// Program specific properties that are shared for easier re-use
	["STRIP_ARGS", "BSAVE_TYPES"].forEach(v => { programSchema[v] = [anything]; });

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
