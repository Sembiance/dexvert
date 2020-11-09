"use strict";
const XU = require("@sembiance/xu");

function performStep(errorLoc, state, p, step, cb)
{
	if(step.length===3)
	{
		XU.log`${XU.cf.fg.red("FLOW ERROR")} step function is expecting 3 cbs, but should only be 2. Likely need to do () => fun instead of just 'fun'`;
		console.log(step, step.toString());
		console.trace();
		console.log(errorLoc);
		process.exit(1);
	}
	
	// This noop fallback allows you to specify synchronous functions (like those in many format.preSteps)
	let stepfn = step(state, p) || p.util.flow.noop;

	if(Object.isObject(stepfn))
	{
		if(stepfn.program)
			stepfn = p.util.program.run(stepfn.program, {args : stepfn.args, argsd : stepfn.argsd, runOptions : stepfn.runOptions, flags : stepfn.flags});
		else
			throw new p.DexvertError(state, "Unsupported step object", stepfn, step);
	}

	stepfn(state, p, cb);
}

// This will perform a set of steps, in serial
exports.serial = function serial(steps)
{
	if(!steps)
		throw new Error("steps are invalid");
	
	const errorLoc = new Error();

	return (state, p, cb) => steps.serialForEach((step, subcb) => performStep(errorLoc, state, p, step, subcb), cb);
};

// Returns a function that when called will execute the given steps in parallel
exports.parallel = function parallel(steps)
{
	if(!steps)
		throw new Error("steps are invalid");

	const errorLoc = new Error();

	return (state, p, cb) => steps.parallelForEach((step, subcb) => performStep(errorLoc, state, p, step, subcb), cb);
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
