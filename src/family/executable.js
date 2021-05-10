"use strict";
const XU = require("@sembiance/xu");

exports.steps =
[
	(state, p) => p.util.flow.serial(p.format.steps || []),
	(state, p) => p.format.post || p.util.flow.noop
];

exports.updateProcessed = function updateProcessed(state, p, cb)
{
	// Executaion processing is successful if there are any files. Don't return because format might override this and set processed back to false
	if(state.output.files || state.input.meta[p.format.meta.formatid])
		state.processed = true;

	if(p.format.updateProcessed)
		return p.format.updateProcessed(state, p, cb);
	
	setImmediate(cb);
};

