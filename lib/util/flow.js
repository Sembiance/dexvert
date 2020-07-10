"use strict";
const XU = require("@sembiance/xu");

exports.parallel = function parallel(steps)
{
	return (state, p, cb) => steps.parallelForEach((step, stepcb) => step(state, p, stepcb), cb);
};

exports.batchRepeatUntil = function batchRepeatUntil(steps, checkFun)
{
	function performBatch(state, p, cb)
	{
		steps.serialForEach((step, stepcb) => step(state, p, stepcb), err =>
		{
			if(err)
				return cb(err);
			
			if(!checkFun(state))
				return cb();
			
			setImmediate(() => performBatch(state, p, cb));
		});
	}

	return (state, p, cb) => performBatch(state, p, cb);
};
