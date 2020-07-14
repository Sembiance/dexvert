"use strict";
const XU = require("@sembiance/xu"),
	unicodeUtil = require("@sembiance/xutil").unicode;

exports.steps =
[
	(state, p) => p.util.flow.serial(p.formats[state.id.family][state.id.formatid].steps),
	() => ({program : "fixPerms"}),
	() => exports.fixEncodings,
	(state, p) => p.formats[state.id.family][state.id.formatid].post || p.util.flow.noop
];

exports.updateProcessed = function updateProcessed(state, p, cb)
{
	// Archive extraction is successful if there are any files. Don't return because format might override this and set processed back to false
	if(state.output.files)
		state.processed = true;

	const format = p.formats[state.id.family][state.id.formatid];
	if(format.updateProcessed)
		return format.updateProcessed(state, p, cb);
	
	setImmediate(cb);
};

// Encodings out of archives can often be in something other than UTF-8. So we convert to UTF8 so that glob actually WORKS, as v8 chokes on anything other than UTF8 encoded filenames/dirs
exports.fixEncodings = function fixEncodings(state, p, cb)
{
	unicodeUtil.fixDirEncodings(state.output.absolute, cb);
};
