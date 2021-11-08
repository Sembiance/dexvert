import {xu} from "xu";
import {validateClass} from "./validate.js";
import {DexFile} from "./DexFile.js";

export class Identification
{
	// builder to get around the fact that constructors can't be async
	static create(o)
	{
		const id = new this();
		Object.assign(id, o);
		validateClass(id, {
			// required
			magic      : {type : "string", required : true},					// the value of the identification
			from       : {type : "string", required : true, enum : ["dexvert", "dexmagic", "file", "trid"]}, // which programid produced the magic
			confidence : {type : "number", required : true, range : [0, 100]},	// what confidence level this identification is

			// optional
			family           : {type : "string"},	// the familyid of this identification
			formatid         : {type : "string"},	// the formatid of the identification
			extensions       : {type : ["string"], allowEmpty : true},	// list of extensions that are expected with this type of identification
			matchType        : {type : "string", enum : ["magic", "filename", "ext", "fileSize", "fallback"]}, 	// the type of identification match
			unsupported      : {type : "boolean"},	// if true, this format is unsupported
			fileSizeMatchExt : {type : "boolean"},	// if true, the original file matched the extension
			auxFiles         : {type : [DexFile]}	// an array of DexFiles that are needed to support this identificatrion
		});

		return id;
	}

	pretty(prefix="")
	{
		const r = [prefix];
		r.push(xu.cf.fg.orange(this.from.padStart(8, " ")));
		r.push(` ${xu.cf.fg.white(this.confidence.toString().padStart(3, " "))}%`);
		r.push(` ${xu.cf.fg.magenta(this.magic)}`);
		if(this.from==="dexvert")
			r.push(` ${xu.cf.fg.peach(this.matchType)} ${xu.cf.fg.yellow(this.family)}${xu.cf.fg.cyan("/")}${xu.cf.fg.yellowDim(this.formatid)}`);
		if(this.unsupported)
			r.push(xu.cf.fg.deepSkyblue(" unsupported"));
		return r.join("");
	}
}
