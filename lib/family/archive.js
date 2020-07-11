"use strict";
const XU = require("@sembiance/xu"),
	unicodeUtil = require("@sembiance/xutil").unicode;

exports.steps = function steps(state, p)
{
	const format = p.formats[state.id.family][state.id.formatid];

	return [
		...(format.steps ? format.steps(state, p) : Array.force(format.meta.program).map(prog => p.util.program.run(p.program[prog]))),
		p.util.program.run(p.program.fixPerms),
		exports.fixEncodings,
		format.post || p.util.flow.noop
	];
};

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
