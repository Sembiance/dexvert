import {xu} from "xu";
import {fileUtil} from "xutil";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import { assertStrictEquals } from "https://deno.land/std@0.110.0/testing/asserts.ts";
import {Family} from "./Family.js";
import {validateClass} from "./validate.js";

export class Format
{
	PRIORITY = {
		TOP      : 0,
		HIGH     : 1,
		STANDARD : 2,
		LOW      : 3,
		VERYLOW  : 4,
		LOWEST   : 5
	};

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
			formatid : {type : "string", required : true},
			name     : {type : "string", required : true},

			// meta
			charSet  : {type : "string"},
			mimeType : {type : "string"},
			notes    : {type : "string"},
			website  : {type : "string", url : true},

			// identification - extension
			ext            : {type : ["string"]},
			forbidExtMatch : {types : ["boolean", Array]},
			forbiddenExt   : {type : ["string"]},
			weakExt        : {types : ["boolean", Array]},

			// identification - filename
			filename : {type : ["string", RegExp]},

			// identification - filename
			fileSize      : {types : ["number", Array, Object]},
			matchFileSize : {type : "boolean"},

			// identification - magic
			magic            : {type : ["string", RegExp]},
			forbiddenMagic   : {type : ["string", RegExp]},
			forbidMagicMatch : {type : "boolean"},
			weakMagic        : {types : ["boolean", Array]},

			// other
			auxFiles         : {type : "function", length : [2, 3]},
			byteCheck        : {types : [Object, Array]},
			confidenceAdjust : {type : "function"},
			fallback         : {type : "boolean"},
			trustMagic       : {type : "boolean"},
			priority         : {type : "number", enum : Object.values(format.PRIORITY)},
			unsupported      : {type : "boolean"},
			untouched        : {type : "boolean"},

			// conversion
			converters     : {type : ["string", Object]}
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
			// TODO REMOVE BELOW AFTER CONVERTING ALL FORMATS
			if(!(await fileUtil.readFile(formatFilePath)).includes(" extends Format") || (await fileUtil.readFile(formatFilePath)).startsWith("/*"))
				continue;
			// TODO REMOVE ABOVE AFTER CONVERTING ALL FORMATS

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
