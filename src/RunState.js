import {xu} from "xu";

export class RunState
{
	meta = {};
	
	// builder to get around the fact that constructors can't be async
	static create({input, output})
	{
		const runState = new this();
		Object.assign(runState, {input, output});
		return runState;
	}
}
