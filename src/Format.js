import {xu} from "xu";
import {fileUtil} from "xutil";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import { assertStrictEquals } from "https://deno.land/std@0.110.0/testing/asserts.ts";
import {Family} from "./Family.js";
import {validateClass} from "./validate.js";
import unsupported from "./format/unsupported.js";

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

	// will get meta info for this particular format and the passed input fileset
	getMeta(input)
	{
		return this.family.getMeta(input, this);
	}

	// returns a pretty string to output to console
	pretty()
	{
		const r = [];
		r.push(`${xu.cf.fg.magenta(this.name)} ${xu.cf.fg.yellow(this.familyid)}${xu.cf.fg.cyan("/")}${xu.cf.fg.yellowDim(this.formatid)}${this.unsupported ? xu.cf.fg.deepSkyblue(" unsupported") : ""} (${xu.cf.fg.greenDim(this.website)})`);
		return r.join("");
	}

	// builder to get around the fact that constructors can't be async
	static create(family, preValidate)
	{
		if(!family || !(family instanceof Family))
			throw new Error(`format [${this.formatid}] constructor called with invalid family [${family}] of type [${typeof family}]`);
		
		const format = new this();
		format.family = family;
		format.familyid = family.familyid;
		if(preValidate)
			preValidate(format);
		
		if((format.converters || []).includes("abydosconvert") && !format.mimeType)
			throw new Error(`format [${this.formatid}] has abydosconvert as a converter but doesn't have a mimeType set which is required for abydos`);

		validateClass(format, {
			// required
			formatid : {type : "string", required : true},
			family   : {type : Family, required : true},
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
			transformUnsafe  : {type : "boolean"},
			trustMagic       : {type : "boolean"},
			priority         : {type : "number", enum : Object.values(format.PRIORITY)},
			unsupported      : {type : "boolean"},
			untouched        : {types : ["boolean", "function"]},

			// conversion
			metaProviders : {type : ["string"], enum : (family.metaids || [])},
			converters    : {type : ["string", Object]},
			keepFilename  : {type : "boolean"},
			safeExt       : {type : "function", length : [0, 1]},
			pre           : {type : "function", length : [0, 1]},
			post          : {type : "function", length : [0, 1]}
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

		// process our 'unsupported.js' formats
		for(const [familyid, unsupportedFormats] of Object.entries(unsupported))
		{
			for(const [formatid, o] of Object.entries(unsupportedFormats))
			{
				const supportedKeys = ["name", "ext", "magic", "weakMagic", "filename", "notes"];
				const extraKeys = Object.keys(o).subtractAll(supportedKeys);
				if(extraKeys.length>0)
					throw new Error(`unsupported format ${familyid}/${formatid} has extra keys that are not currently copied over to the Unknown class, add them: ${extraKeys}`);
				
				class Unsupported extends Format
				{
					unsupported = true;
				}

				formats[formatid] = Unsupported.create(families[familyid], format =>	// eslint-disable-line sembiance/shorter-arrow-funs
				{
					for(const supportedKey of supportedKeys)
					{
						if(Object.hasOwn(o, supportedKey))
							format[supportedKey] = o[supportedKey];
					}
				});
			}
		}
		
		this.formats = formats;
		return formats;
	}
}
