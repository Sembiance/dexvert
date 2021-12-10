import {Format} from "../../Format.js";

export class quantum extends Format
{
	name       = "Quantum Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Quantum_compressed_archive";
	ext        = [".pak", ".q"];
	magic      = ["Quantum archive data", "Quantum compressed archive"];
	converters = ["unpaq"];
}
