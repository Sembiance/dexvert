import {Format} from "../../Format.js";

export class quantumPaint extends Format
{
	name       = "Quantum Paint";
	website    = "http://fileformats.archiveteam.org/wiki/QuantumPaint";
	ext        = [".pbx"];
	mimeType   = "image/x-quantum-paint";
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`];
}
