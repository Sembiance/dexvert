import {xu} from "xu";

export class RunState
{
	meta = {};
	
	// builder to get around the fact that constructors can't be async
	constructor({allowNew}) { if(!allowNew) { throw new Error(`Use static ${this.constructor.name}.create() instead`); } }	// eslint-disable-line curly
	static create({input, output})
	{
		const runState = new this({allowNew : true});
		Object.assign(runState, {input, output});
		return runState;
	}
}
