import {Format} from "../../Format.js";

export class volkswriter extends Format
{
	name        = "Volkswriter";
	website     = "https://winworldpc.com/product/volkswriter";
	ext         = [".vw"];
	unsupported = true;	// only ext match for now and unknown if it has magic or how many might be on discmaster. writing a file with v2.0 deluxe DOS program, doesn't show any magic at all
	converters  = ["softwareBridge[format:volkswriter3]", "wordForWord"];
}
