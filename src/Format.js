import {xu, fg} from "xu";
import {Family} from "./Family.js";
import {Program} from "./Program.js";
import {validateClass} from "validator";

export class Format
{
	// warning, don't change these numbers. They are hard-coded used in various places such as identify.js
	PRIORITY = {
		TOP      : 0,
		HIGH     : 1,
		STANDARD : 2,
		LOW      : 3,
		VERYLOW  : 4,
		LOWEST   : 5
	};

	formatid = this.constructor.name;
	family = null;
	familyid = null;
	baseKeys = Object.keys(this);

	// will get meta info for this particular format and the passed input fileset
	async getMeta(inputFile, dexState)
	{
		const xlog = dexState.xlog;
		const meta = {};

		// first if the family has a meta provider, call that
		Object.assign(meta, this.family.meta ? (await this.family.meta(inputFile, this, xlog)) || {} : {});
		
		// next, if the format.metaProvider has a programid, call that
		for(const metaProviderRaw of (this.metaProvider || []))
		{
			const metaProviderParts = metaProviderRaw.split("=>");
			const progRaw = metaProviderParts[0].trim();
			const metaProviderKey = metaProviderParts.length===2 ? metaProviderParts[1].trim() : null;
			
			if(!Program.hasProgram(progRaw))
				continue;

			const r = await Program.runProgram(progRaw, inputFile, {xlog});
			if(r.meta && Object.keys(r.meta).length>0)
			{
				if(metaProviderKey)
				{
					meta[metaProviderKey] = {};
					Object.assign(meta[metaProviderKey], r.meta);
				}
				else
				{
					Object.assign(meta, r.meta);
				}
			}
			await r.unlinkHomeOut();
		}

		// lastly, if the format itself has a meta function, call that
		if(this.meta)
			Object.assign(meta, (await this.meta(inputFile, dexState)) || {});

		return meta;
	}

	// returns a pretty string to output to console
	pretty(prefix="")
	{
		return `${prefix}${fg.yellow(this.familyid)}${fg.cyanDim("/")}${fg.yellowDim(this.formatid)} ${fg.greenDim(this.name)}${this.unsupported ? fg.deepSkyblue(" unsupported") : ""} ${xu.paren(fg.greenDim(this.website || "no website"))}`;
	}

	serialize()
	{
		return this.formatid;
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

		validateClass(format, {
			// required
			formatid : {type : "string", required : true},
			family   : {type : Family, required : true},
			name     : {type : "string", required : true},

			// meta
			charSet  : {type : "string"},
			classify : {type : "boolean"},
			mimeType : {type : "string"},
			notes    : {type : "string"},
			website  : {type : "string", url : true},

			// identification - extension
			ext            : {type : ["string"]},
			forbidExtMatch : {types : ["boolean", Array]},
			forbiddenExt   : {type : ["string"]},
			matchPreExt    : {type : "boolean"},
			weakExt        : {types : ["boolean", Array]},

			// identification - filename
			filename     : {type : [RegExp]},
			weakFilename : {type : "boolean"},
			weakFileSize : {type : ["number"]},

			// identification - filename
			fileSize      : {types : ["number", Array, Object]},
			matchFileSize : {type : "boolean"},

			// identification - magic
			magic            : {type : ["string", RegExp]},
			forbiddenMagic   : {type : ["string", RegExp]},
			forbidMagicMatch : {type : "boolean"},
			weakMagic        : {types : ["boolean", Array]},

			// identification - mac file type/creator, prodos file types, etc
			idMeta : {type : "function", length : [1]},

			// other
			alwaysIdentify   : {type : "boolean"},
			auxFiles         : {type : "function", length : [2, 4]},
			byteCheck        : {types : [Object, Array]},
			confidenceAdjust : {type : "function"},
			fallback         : {type : "boolean"},
			idCheck          : {type : "function", length : [0, 3]},
			meta             : {type : "function", length : [0, 2]},
			packed           : {type : "boolean"},
			priority         : {type : "number", enum : Object.values(format.PRIORITY)},
			simple           : {type : "boolean"},
			skipClassify     : {type : "boolean"},
			slow             : {type : "boolean"},
			trustMagic       : {type : "boolean"},
			unsupported      : {type : "boolean"},
			untouched        : {types : ["boolean", "function"]},
			verify           : {type : "function", length : 1},
			verifyUntouched  : {types : ["boolean", "function"]},

			// conversion
			converters   : {types : [Array, "function"]},
			keepFilename : {type : "boolean"},
			metaProvider : {type : ["string"], enum : []},
			safeExt      : {types : ["string", "function"], allowEmpty : true},
			processed    : {type : "function", length : [0, 1]},
			pre          : {type : "function", length : [0, 1]},
			post         : {type : "function", length : [0, 1]}
		});
		return format;
	}
}
