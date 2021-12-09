import {xu} from "xu";
import {validateClass} from "./validate.js";

export class Family
{
	familyid = this.constructor.name;
	baseKeys = Object.keys(this);

	// builder to get around the fact that constructors can't be async
	static create()
	{
		const family = new this();
		validateClass(family, {
			// meta
			verify  : {type : "function", length : 2}, 	// verifies the new files and ensures they are valid
			metaids : {type : ["string"]},	// list of meta provider id strings
			meta    : {type : "function", length : [1]}
		});
		return family;
	}

	pretty()
	{
		return this.familyid;
	}

	serialize()
	{
		return this.familyid;
	}

	static deserialize(v)
	{
		return this.families[v];
	}
}
