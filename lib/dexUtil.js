"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
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

					if((meta.ext || []).some(ext => ext.charAt(0)!=="."))
						process.exit(XU.log`Handler ${FAMILY}/${formatid} has an ext that doesn't start with a period!`);

					if((meta.ext || []).some(ext => ext.match(/[A-Z]/)))
						process.exit(XU.log`Handler ${FAMILY}/${formatid} has an ext that is not lowercase!`);

					if(!meta.hasOwnProperty("name"))
						process.exit(XU.log`Handler ${FAMILY}/${formatid} does not have a name!`);
					
					
					formats[FAMILY][formatid] = format;
				});
			});

			return formats;
		},
		cb
	);
};

// Sets the state.output object according to the passed in outputDirPath
exports.setStateOutput = function setStateOutput(state, outputDirPath)
{
	state.output = { absolute : path.resolve(outputDirPath), dirPath : path.resolve(outputDirPath), ...path.parse(outputDirPath)};
};
