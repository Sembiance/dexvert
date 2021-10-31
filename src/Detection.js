import {xu} from "xu";
import {validateClass} from "./validate.js";
import {DexFile} from "./DexFile.js";

export class Detection
{
	// builder to get around the fact that constructors can't be async
	constructor({allowNew}) { if(!allowNew) { throw new Error(`Use static ${this.constructor.name}.create() instead`); } }	// eslint-disable-line curly
	static create({value, from, file, confidence=100, extensions=[]})
	{
		const detection = new this({allowNew : true});
		Object.assign(detection, {value, from, file, confidence, extensions});

		validateClass(detection, {
			// required
			value      : {type : "string", required : true},						// the value of the detection
			from       : {type : "string", required : true},						// which programid produced the value
			file       : {type : DexFile, required : true},							// the file that this detection is for
			confidence : {type : "number", required : true, range : [0, 100]}, 		// what confidence level this detection is. Default: 100
			extensions : {type : ["string"], required : true, allowEmpty : true} 	// list of extensions that are expected with this type of detection. Default: []
		});

		return detection;
	}
}
