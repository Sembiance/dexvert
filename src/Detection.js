import {xu, fg} from "xu";
import {validateClass} from "validator";
import {DexFile} from "./DexFile.js";
import {Program} from "./Program.js";
import {WEAK_VALUES} from "./WEAK.js";

export const DETECTOR_PROGRAMS = ["file", "trid", "checkBytes", "dexmagic", "perlTextCheck", "ancientID", "amigaBitmapFontContentDetector", "siegfried", "pc98ripperID", "lsar", "gt2", "disktype", "unp64ID", "detectItEasy", "binwalkID"];

export const TEXT_MAGIC_STRONG =
[
	// checkBytes
	"Printable ASCII",
	
	// file
	"ASCII text", "ISO-8859 text", "UTF-8 Unicode text", "Non-ISO extended-ASCII text", "ReStructuredText file", "International EBCDIC text", "UTF-8 Unicode text", "Unicode text, UTF-8 text",
	"Algol 68 source, ISO-8859 text",	// Algol 68 is often mis-identified, usually confused with Pascal files. Just treat it as regular text
	
	// trid
	"Text - UTF-8 encoded"
];

export const TEXT_MAGIC_WEAK =
[
	// perlTextCheck
	"Likely Text (Perl)",

	// GT2
	"Textdatei",

	// file
	"Microsoft HTML Help Project, ISO-8859 text, with CRLF line terminators", /^text\/plain/
];

export const TEXT_MAGIC = [...TEXT_MAGIC_STRONG, ...TEXT_MAGIC_WEAK];

export class Detection
{
	// builder to get around the fact that constructors can't be async
	static create({value, from, file, confidence=100, extensions=[]})
	{
		const detection = new this();
		Object.assign(detection, {value, from, file, confidence, extensions});
		detection.weak = WEAK_VALUES.some(v => v.test(value)) || confidence<5;

		validateClass(detection, {
			// required
			value      : {type : "string", required : true},						// the value of the detection
			from       : {type : "string", required : true},						// which programid produced the value
			file       : {type : DexFile, required : true},							// the file that this detection is for
			confidence : {type : "number", required : true, range : [0, 100]},		// what confidence level this detection is. Default: 100
			extensions : {type : ["string"], required : true, allowEmpty : true}, 	// list of extensions that are expected with this type of detection. Default: []
			weak       : {type : "boolean", required : true}						// if set to true this is a weak detection and should not be trusted too highly
		});

		return detection;
	}

	pretty(prefix="")
	{
		return `${prefix}${fg.orange(this.from.padStart(8, " "))} ${fg.white(this.confidence.toString().padStart(3, " "))}% ${fg.magenta(this.value)}${this.weak ? fg.deepSkyblue("weak") : ""}`;
	}
}

export async function getDetections(f, {xlog, detectors=DETECTOR_PROGRAMS}={})
{
	return (await Promise.all(detectors.map(programid => Program.runProgram(programid, f, {xlog, autoUnlink : true})))).flatMap(o => o.meta.detections).filter(detection => !!detection);
}
