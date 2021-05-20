"use strict";
const XU = require("@sembiance/xu");

function checkShouldContinue(state)
{
	return !state.output.files && state.converters.length>0;
}

exports.converterSteps =
[
	(state, p) =>
	{
		state.converters = ((typeof p.format.converterPriorty==="function" ? p.format.converterPriorty(state, p) : p.format.converterPriorty) || []).map(v => (Object.isObject(v) ? v : {program : v}));
		return p.util.flow.noop;
	},
	(state0, p0) => p0.util.flow.batchRepeatUntil([
		(state, p) =>
		{
			state.converter = state.converters.shift();
			if(Array.isArray(state.converter))
				return p.util.flow.serial(state.converter);

			return state.converter;
		},
		(state, p) => p.util.file.findValidOutputFiles(),
		() => exports.validateOutputFiles], checkShouldContinue)
];

exports.steps =
[
	(state, p) => p.util.flow.serial(p.format.steps || exports.converterSteps),
	(state, p) => p.format.post || p.util.flow.noop
];

exports.validateOutputFiles = function validateOutputFiles(state, p, cb)
{
	if((state.output.files || []).length===0)
		delete state.converter;
	
	setImmediate(cb);
};

exports.updateProcessed = function updateProcessed(state, p, cb)
{
	// If we have any output files OR if we have input specific meta data, then count this as processed
	if(state.output.files || state.input.meta[p.format.meta.formatid])
		state.processed = true;

	if(p.format.updateProcessed)
		return p.format.updateProcessed(state, p, cb);

	setImmediate(cb);
};
