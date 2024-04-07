import {xu, fg} from "xu";
import {validateClass} from "validator";
import {DexFile} from "./DexFile.js";
import {DETECTOR_PROGRAMS} from "./Detection.js";

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
			from       : {type : "string", required : true, enum : ["dexvert", "single", ...DETECTOR_PROGRAMS]}, // which programid produced the magic
			confidence : {type : "number", required : true, range : [0, 100]},	// what confidence level this identification is

			// optional
			family           : {type : "string"},	// the familyid of this identification
			formatid         : {type : "string"},	// the formatid of the identification
			website          : {type : "string"},	// the website for this formatid
			extensions       : {type : ["string"], allowEmpty : true},	// list of extensions that are expected with this type of identification
			matchType        : {type : "string", enum : ["magic", "idMeta", "filename", "ext", "fileSize", "fallback"]}, 	// the type of identification match
			unsupported      : {type : "boolean"},	// if true, this format is unsupported
			fileSizeMatchExt : {type : "string"},	// if true, the original file matched the extension
			auxFiles         : {type : [DexFile]},	// an array of DexFiles that are needed to support this identificatrion
			weak             : {type : "boolean"}	// if true, this identification comes frmo a weak detection
		});

		return id;
	}

	serialize()
	{
		const o = {};
		Object.assign(o, this);
		return o;
	}

	pretty(prefix="")
	{
		const r = [prefix];
		r.push(fg.orange(this.from.padStart(8, " ")));
		r.push(` ${fg.white(this.confidence.toString().padStart(3, " "))}${fg.cyanDim("%")}`);
		r.push(` ${fg.greenDim(this.magic)}`);
		if(this.from==="dexvert")
			r.push(` ${fg.peach(this.matchType)} ${fg.yellow(this.family)}${fg.cyanDim("/")}${fg.yellowDim(this.formatid)}`);
		if(this.unsupported)
			r.push(fg.deepSkyblue(" unsupported"));
		return r.join("");
	}
}
