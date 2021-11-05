import {xu} from "xu";
import {fileUtil} from "xutil";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import { assertStrictEquals } from "https://deno.land/std@0.110.0/testing/asserts.ts";
import {validateClass} from "./validate.js";

export class Family
{
	static families = null;
	familyid = this.constructor.name;
	baseKeys = Object.keys(this);

	// builder to get around the fact that constructors can't be async
	constructor({allowNew}) { if(!allowNew) { throw new Error(`Use static ${this.constructor.name}.create() instead`); } }	// eslint-disable-line curly
	static create()
	{
		const family = new this({allowNew : true});
		validateClass(family, {
			// meta
			metaids : {type : ["string"]},
			getMeta : {type : "function", length : [1]}
		});
		return family;
	}

	// loads all src/family/*.js files from disk as Family objects. These are cached in the static this.families cache
	static async loadFamilies()
	{
		if(this.families)
			return this.families;
		
		this.families = {};

		for(const familyFilePath of await fileUtil.tree(path.join(xu.dirname(import.meta), "family"), {nodir : true, regex : /\.js$/}))
		{
			const familyModule = await import(familyFilePath);
			const familyid = Object.keys(familyModule)[0];

			// class name must match filename
			assertStrictEquals(familyid, path.basename(familyFilePath, ".js").toLowerCase(), `family file [${familyFilePath}] does not have a matching class name [${familyid}]`);

			// check for duplicates
			if(this.families[familyid])
				throw new Error(`family [${familyid}] at ${familyFilePath} is a duplicate of ${this.families[familyid]}`);

			// create the class and validate it
			this.families[familyid] = familyModule[familyid].create();
			if(!(this.families[familyid] instanceof this))
				throw new Error(`family [${familyid}] is not of type Family`);
		}
		
		return this.families;
	}
}
