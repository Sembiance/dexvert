import {xu} from "xu";
import {fileUtil} from "xutil";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import { assertStrictEquals } from "https://deno.land/std@0.110.0/testing/asserts.ts";
import {Family} from "./Family.js";
import {validateClass} from "./validate.js";

export class Format
{
	static formats = null;
	formatid = this.constructor.name;
	family = null;
	familyid = null;
	baseKeys = Object.keys(this);

	// builder to get around the fact that constructors can't be async
	constructor({allowNew}) { if(!allowNew) { throw new Error(`Use static ${this.constructor.name}.create() instead`); } }	// eslint-disable-line curly
	static create(family)
	{
		if(!family || !(family instanceof Family))
			throw new Error(`format [${this.formatid}] constructor called with invalid family [${family}] of type [${typeof family}]`);
		
		const format = new this({allowNew : true});
		format.family = family;
		format.familyid = family.familyid;
		validateClass(format, {
			// required
			formatid : {type : "string", required : true},	// automatically set to the constructor name
			name     : {type : "string", required : true},	// human friendly name of the format. The only required field.

			// meta
			charSet  : {type : "string"}, 		// the character set for this file. Example: "IBM-943"
			mimeType : {type : "string"}, 		// mime type for this format. required to use abydosconvert
			notes    : {type : "string"}, 		// various notes about this format
			website  : {type : "string", url : true},	// URL about this format

			// identification - extension
			ext          : {type : ["string"]}, // array of extensions this format may have. first item should be the primary extension. always use lowercase
			forbiddenExt : {type : ["string"]},	// array of extensions that it should never be

			// identification - magic
			magic : {type : ["string", RegExp]},

			// conversion
			converters : {type : ["string"]}
		});
		return format;
	}

	// loads all src/format/*/*.js files from disk as Format objects. These are cached in the static this.formats cache
	static async loadFormats()
	{
		if(this.formats!==null)
		{
			await xu.waitUntil(() => Object.isObject(this.formats));
			return this.formats;
		}
		
		this.formats = false;
		const formats = {};

		const families = await Family.loadFamilies();

		for(const formatFilePath of await fileUtil.tree(path.join(xu.dirname(import.meta), "format"), {nodir : true, regex : /[^/]+\/.+\.js$/}))
		{
			const formatModule = await import(formatFilePath);
			const formatid = Object.keys(formatModule)[0];
			const familyid = path.basename(path.dirname(formatFilePath));
			if(!families[familyid])
				throw new Error(`format [${formatid}] at [${formatFilePath}] is in a directory [${familyid}] that does not have a family class`);

			// class name must match filename
			assertStrictEquals(formatid, path.basename(formatFilePath, ".js"), `format file [${formatFilePath}] does not have a matching class name [${formatid}]`);

			// check for duplicates
			if(formats[formatid])
				throw new Error(`format [${formatid}] at [${formatFilePath}] is a duplicate of ${formats[formatid]}`);

			// create the class and validate it
			formats[formatid] = formatModule[formatid].create(families[familyid]);
			if(!(formats[formatid] instanceof this))
				throw new Error(`format [${formatid}] at [${formatFilePath}] is not of type Format`);
		}
		
		this.formats = formats;
		return formats;
	}
}
