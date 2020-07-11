"use strict";
const XU = require("@sembiance/xu");

// Returns a function that when called will execute the given steps in parallel
exports.parallel = function parallel(steps)
{
	return (state, p, cb) => steps.parallelForEach((step, stepcb) => step(state, p, stepcb), cb);
};

// Returns a function that will perform serially the steps as a batch over and over until so long as shouldContinue returns true
exports.batchRepeatUntil = function batchRepeatUntil(steps, shouldContinue)
{
	function performBatch(state, p, cb)
	{
		steps.serialForEach((step, stepcb) => step(state, p, stepcb), err =>
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
