"use strict";
const XU = require("@sembiance/xu");

exports.steps =
[
	(state, p) => (p.format.steps ? p.util.flow.serial(p.format.steps) : p.util.flow.noop),
	(state, p) => p.format.post || p.util.flow.noop
];

exports.updateProcessed = function updateProcessed(state, p, cb)
{
	if(state.output.files)
		state.processed = true;

	if(p.format.updateProcessed)
		return p.format.updateProcessed(state, p, cb);
	
	setImmediate(cb);
};

