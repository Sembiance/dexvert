"use strict";
const XU = require("@sembiance/xu");

function performStep(state, p, step, cb)
{
	let stepfn = step(state, p);

	if(Object.isObject(stepfn))
	{
		if(stepfn.program)
			stepfn = p.util.program.run(p.program[stepfn.program], {args : stepfn.args, runOptions : stepfn.runOptions});
		else
			throw new p.DexvertError(state, "Unsupported step object", stepfn, step);
	}

	stepfn(state, p, cb);
}

// This will perform a set of steps, in serial
exports.serial = function serial(steps)
{
	return (state, p, cb) => steps.serialForEach((step, subcb) => performStep(state, p, step, subcb), cb);
};

// Returns a function that when called will execute the given steps in parallel
exports.parallel = function parallel(steps)
{
	return (state, p, cb) => steps.parallelForEach((step, subcb) => performStep(state, p, step, subcb), cb);
};

// Returns a function that will perform serially the steps as a batch over and over until so long as shouldContinue returns true
exports.batchRepeatUntil = function batchRepeatUntil(steps, shouldContinue)
{
	function performBatch(state, p, cb)
	{
		exports.serial(steps)(state, p, err =>
		{
			if(err)
				return cb(err);
			
			if(!shouldContinue(state))
				return cb();
			
			setImmediate(() => performBatch(state, p, cb));
		});
	}

	return (state, p, cb) => performBatch(state, p, cb);
};

// Simply calls the cb right away and nothing else
exports.noop = function noop(state, p, cb)
{
	setImmediate(cb);
};
