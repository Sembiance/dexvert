import {Format} from "../../Format.js";

export class eschalonSetupARCV extends Format
{
	name  = "Eschalon Setup ARCV Container";
	ext   = [".arv"];					// Also .a01, .a02, etc. but magic seems pretty strong
	magic = ["Eschalon Setup ARCV"];
	// This can be a multi-part archive, but each file can be extracted on it's own, so no need to use auxFiles and the filename doesn't need to be kept original either
	notes      = "Not all formats are supported by the converter";
	converters = ["arcvExtractor"];		// This claims support, but couldn't extract any of my samples: cmdTotal[wcx:InstExpl.wcx]
}
